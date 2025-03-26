from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import onnxruntime as ort
import os
from AgriVision.source import ml_function, utils
from googletrans import Translator

app = Flask(__name__)

translator = Translator()

# Load the ONNX model
MODEL_PATH = "prediction_model.onnx"
try:
    session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
except Exception as e:
    print(f"Failed to load ONNX model: {e}")
    session = None

IMG_SIZE = (224, 224)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        image = image.resize(IMG_SIZE)
        image = np.array(image) / 255.0
        image = np.transpose(image, (2, 0, 1))
        image = np.expand_dims(image, axis=0).astype(np.float32)
        return image
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def predict_onnx(image):
    try:
        outputs = session.run([output_name], {input_name: image})
        return np.argmax(outputs[0], axis=1)[0]
    except Exception as e:
        print(f"ONNX inference error: {e}")
        return None

@app.route('/predict', methods=['POST'])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = os.path.basename(file.filename)
        filepath = os.path.join("uploads", filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(filepath)

        image = preprocess_image(filepath)
        if image is None:
            return jsonify({"error": "Failed to process image"}), 500

        predicted_class = predict_onnx(image)
        if predicted_class is None:
            return jsonify({"error": "ONNX inference failed"}), 500

        return jsonify({"predicted_class": int(predicted_class)})
    else:
        return jsonify({"error": "Invalid file type"}), 400

@app.route('/predicttodayWeather', methods=['POST'])
def predict_today_weather():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    try:
        return jsonify(utils.get_today_forecast(latitude, longitude))
    except Exception as e:
        print(f"Failed to Extract Weather: {e}")
        return jsonify({"error": "Failed to Extract Weather"}), 500

@app.route('/predictforecastWeather', methods=['POST'])
def predict_forecast_weather():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    try:
        return jsonify(utils.get_weather_forecast(latitude, longitude))
    except Exception as e:
        print(f"Failed to Extract Weather: {e}")
        return jsonify({"error": "Failed to Extract Weather"}), 500

@app.route('/diseaseDescription', methods=['POST'])
def disease_prediction():
    data = request.json
    disease_input = data.get("disease_name")
    try:
        if disease_input == "No Leaf Found":
            return jsonify("Image is not Clear. Try Again.")
        return jsonify(utils.get_disease_info(disease_input))
    except Exception as e:
        print(f"Failed to Extract Description: {e}")
        return jsonify({"error": "Failed to Extract Description"}), 500

@app.route('/fertilizersRecommendation', methods=['POST'])
def fertilizers_recommendation():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    _ismanual = data.get("_ismanual")
    manual_data = data.get("manual_data")
    crop = data.get("crop")

    try:
        moisturefeature = utils.get_soil_moisture(latitude, longitude)
        soil_data = manual_data if _ismanual else {'P': 131.5, 'N': 221, 'K': 78.9, 'ph': 7.0, 'soil_moisture': moisturefeature}
        return jsonify(utils.get_fertilizer_recommendation(soil_data, crop))
    except Exception as e:
        print(f"Failed to Extract Description: {e}")
        return jsonify({"error": "Failed to Extract Description"}), 500

@app.route('/cropRecommendation', methods=['POST'])
def crop_recommendation():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    _ismanual = data.get("_ismanual")
    manual_data = data.get("manual_data")

    try:
        weather_data = utils.get_today_forecast(latitude, longitude)
        Csoil_data = manual_data if _ismanual else {
            'P': 131.5, 'N': 221, 'K': 78.9, 'ph': 7.0,
            'Temperature (°C)': weather_data['today']['Temperature (°C)'],
            'Humidity (%)': weather_data['today']['Humidity (%)'],
            'Rainfall (mm)': weather_data['today']['Rainfall (mm)']
        }
        return jsonify(ml_function.give_crop(latitude, longitude, Csoil_data))
    except Exception as e:
        print(f"Failed to Extract Description: {e}")
        return jsonify({"error": "Failed to Extract Description"}), 500
    
@app.route('/translate', methods=['POST'])
def translate_description():
    try:
        data = request.json
        description = data.get("description")
        language = data.get("language", "en")  # Default to English

        if not description:
            return jsonify({"error": "No text provided"}), 400

        # Perform translation
        translated_text = translator.translate(description, dest=language).text

        return jsonify({"translated_text": translated_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)