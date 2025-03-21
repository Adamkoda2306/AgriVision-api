import os
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)

# Load the trained Keras model
MODEL_PATH = "prediction_model.h5"  # Update with your model's path
model = tf.keras.models.load_model(MODEL_PATH)

# Define the input image size (must match the model's input size)
IMG_SIZE = (224, 224)  # Update if needed

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

@app.route("/predict", methods=["POST"])
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

        # Preprocess and predict
        image = preprocess_image(filepath)
        prediction = model.predict(image)
        predicted_class = np.argmax(prediction, axis=1)[0]
        confidence = float(np.max(prediction))

        return jsonify({"predicted_class": int(predicted_class)})
    else:
        return jsonify({"error": "Invalid file type"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050,debug=True)
