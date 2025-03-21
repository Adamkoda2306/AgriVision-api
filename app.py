from flask import Flask, request, jsonify
import random
import logging
import requests
from AgriVision.source import ml_function, utils
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import tensorflow as tf
import os
from google.cloud import translate_v2 as translate

app = Flask(__name__)

# Enable Logging
logging.basicConfig(level=logging.INFO)

# Load 2Factor API Key
TWOFACTOR_API_KEY = "a07a23ed-f513-11ef-8b17-0200cd936042"

if not TWOFACTOR_API_KEY:
    logging.error("2Factor API key is missing! Set it as an environment variable.")

# Store OTPs temporarily (Use DB for production)
otp_store = {}

# Load the trained Keras model
MODEL_PATH = "prediction_model.h5"
keras_model = tf.keras.models.load_model(MODEL_PATH)

# Define the input image size (must match the model's input size)
IMG_SIZE = (224, 224)

# Allowed extensions for image uploads
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize(IMG_SIZE)
    image = np.array(image) / 255.0  # Normalize pixel values
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    phone = data.get("phone")

    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    phone = "+91" + phone[-10:]  # Ensure proper format
    otp = random.randint(1000, 9999)  # Generates a 4-digit OTP
    otp_store[phone] = otp

    try:
        response = requests.get(
            f"https://2factor.in/API/V1/{TWOFACTOR_API_KEY}/SMS/{phone}/{otp}"
        )
        result = response.json()

        if result.get("Status") == "Success":
            return jsonify({"message": "OTP sent successfully", "session_id": result.get("Details")})
        else:
            return jsonify({"error": "Failed to send OTP"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to send OTP: {str(e)}"}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    phone = data.get("phone")
    otp = data.get("otp")

    if not phone or not otp:
        return jsonify({"error": "Phone and OTP are required"}), 400

    if otp_store.get(phone) == int(otp):
        del otp_store[phone]
        return jsonify({"message": "OTP Verified Successfully"})
    else:
        return jsonify({"error": "Invalid OTP"}), 400

@app.route('/resend-otp', methods=['POST'])
def resend_otp():
    return send_otp()

@app.route('/change-number', methods=['POST'])
def change_number():
    data = request.json
    phone = data.get("phone")

    if phone in otp_store:
        del otp_store[phone]

    return jsonify({"message": "Number changed successfully"}), 200

@app.route('/diseaseDescription', methods=['POST'])
def disease_prediction():
    data = request.json
    disease_input = data.get("disease_name")

    try:
        if disease_input == "No Leaf Found":
            return jsonify("Image is not Clear. Try Again.")

        description = utils.get_disease_info(disease_input)

        if 'error' in description:
            return jsonify(description), 500
        
        return jsonify(description)
    except Exception as e:
        return jsonify({"error": f"Failed to Extract Description: {str(e)}"}), 500

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

        if not _ismanual:
            soil_data = {
                'P': 131.5,
                'N': 221,
                'K': 78.9,
                'ph': 7.0,
                'soil_moisture': moisturefeature
            }
        else:
            soil_data = {
                'P': manual_data['P'],
                'N': manual_data['N'],
                'K': manual_data['K'],
                'ph': manual_data['ph'],
                'soil_moisture': moisturefeature
            }

        recommend = utils.get_fertilizer_recommendation(soil_data, crop)

        if 'error' in recommend:
            return jsonify(recommend), 500
        
        return jsonify(recommend)
    except Exception as e:
        return jsonify({"error": f"Failed to Extract Description: {str(e)}"}), 500

@app.route('/cropRecommendation', methods=['POST'])
def crop_recommendation():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    _ismanual = data.get("_ismanual")
    manual_data = data.get("manual_data")

    try:
        weather_data = utils.get_today_forecast(latitude, longitude)

        if not _ismanual:
            Csoil_data = {
                'P': 131.5,
                'N': 221,
                'K': 78.9,
                'ph': 7.0,
                'Temperature (°C)': weather_data['today']['Temperature (°C)'],
                'Humidity (%)': weather_data['today']['Humidity (%)'],
                'Rainfall (mm)': weather_data['today']['Rainfall (mm)']
            }
        else:
            Csoil_data = {
                'P': manual_data['P'],
                'N': manual_data['N'],
                'K': manual_data['K'],
                'ph': manual_data['ph'],
                'Temperature (°C)': manual_data['Temperature (°C)'],
                'Humidity (%)': manual_data['Humidity (%)'],
                'Rainfall (mm)': manual_data['Rainfall (mm)']
            }

        CropRecommend = ml_function.give_crop(latitude, longitude, Csoil_data)

        if 'error' in CropRecommend:
            return jsonify(CropRecommend), 500
        
        return jsonify(CropRecommend)
    except Exception as e:
        return jsonify({"error": f"Failed to Extract Description: {str(e)}"}), 500

@app.route('/predicttodayWeather', methods=['POST'])
def predict_today_weather():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    try:
        weather_data = utils.get_today_forecast(latitude, longitude)
        if 'error' in weather_data:
            return jsonify(weather_data), 500
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({"error": f"Failed to Extract Weather: {str(e)}"}), 500

@app.route('/predictforecastWeather', methods=['POST'])
def predict_forecast_weather():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    try:
        weather_data_f = utils.get_weather_forecast(latitude, longitude)
        if 'error' in weather_data_f:
            return jsonify(weather_data), 500
        return jsonify(weather_data_f)
    except Exception as e:
        return jsonify({"error": f"Failed to Extract Weather: {str(e)}"}), 500

@app.route('/predict', methods=['POST'])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join("uploads", filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(filepath)

        image = preprocess_image(filepath)
        prediction = keras_model.predict(image)
        predicted_class = np.argmax(prediction, axis=1)[0]

        return jsonify({"predicted_class": int(predicted_class)})
    else:
        return jsonify({"error": "Invalid file type"}), 400
    
@app.route('/translate', methods=['POST'])
def translate_description():
    try:
        data = request.json
        description = data.get("description")
        language = data.get("language", "en")  # Default to English if missing

        if not description:
            return jsonify({"error": "No text provided"}), 400

        service_account_path = os.path.join(os.getcwd(), "api.json")
        if not os.path.exists(service_account_path):
            return jsonify({"error": "Missing API key file"}), 500

        # Initialize Google Translate Client
        client = translate.Client.from_service_account_json(service_account_path)
        
        # Corrected method usage
        result = client.translate(description, target_language=language)

        return jsonify({"translated_text": result["translatedText"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logging.info("Starting Flask server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000)
