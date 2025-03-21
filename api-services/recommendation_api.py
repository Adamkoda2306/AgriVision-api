from flask import Flask, request, jsonify
import logging
from AgriVision.source import ml_function, utils  # Assuming your utils file is in the specified path

app = Flask(__name__)

@app.route('/diseaseDescription', methods=['POST'])
def disease_prediction():
    data = request.json
    disease_input = data.get("disease_name")
    
    try:
        logging.debug(f"✅ Disease Name Extracted Successfully")
        
        if (disease_input == "No Leaf Found"):
            Optext = "Image is not Clear. Try Again.";
            return jsonify(Optext);
        
        # Call the function from utils to fetch description
        description = utils.get_disease_info(disease_input)
        
        if 'error' in description:
            return jsonify(description), 500  # Handle error case
        
        return jsonify(description)
        
    except Exception as e:
        logging.error(f"❌ AI API Error: {str(e)}")
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
        logging.debug(f"✅ lat and lon Extracted Successfully")
        moisturefeature = utils.get_soil_moisture(latitude, longitude)
        
        print(f"Received _ismanual: {_ismanual} (Type: {type(_ismanual)})")
        if not _ismanual:
            features = utils.get_soil_data(latitude, longitude)
            print(f"Received features: {features} (Type: {type(features)})")
            soil_data = {
                'P' : features['P'],
                'N': features['N'],
                'K': features['K'],
                'ph': features['ph'],
                'soil_moisture': moisturefeature
            }
        else:
            soil_data = {
                'P' : manual_data['P'],
                'N': manual_data['N'],
                'K': manual_data['K'],
                'ph': manual_data['ph'],
                'soil_moisture': moisturefeature
            }
        
        recommend = utils.get_fertilizer_recommendation(soil_data, crop);
        
        if 'error' in recommend:
            return jsonify(recommend), 500  # Handle error case
        
        return jsonify(recommend)
        
    except Exception as e:
        logging.error(f"❌ AI API Error: {str(e)}")
        return jsonify({"error": f"Failed to Extract Description: {str(e)}"}), 500
    
@app.route('/cropRecommendation', methods=['POST'])
def crop_recommendation():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    _ismanual = data.get("_ismanual")
    manual_data = data.get("manual_data")
    
    try:
        logging.debug(f"✅ lat and lon Extracted Successfully")
        weather_data = utils.get_today_forecast(latitude, longitude)
        logging.debug(f"${_ismanual}")
        
        if (_ismanual == "false"):
            features = utils.get_soil_data(latitude, longitude)
            Csoil_data = {
                'P' : features['P'],
                'N': features['N'],
                'K': features['K'],
                'ph': features['pH'],
                'Temperature (°C)': weather_data['Avg Temperature (°C)'],
                'Humidity (%)': weather_data['Avg Humidity (%)'],
                'Rainfall (mm)': weather_data['Total Rainfall (mm)']
            }
        else:
            Csoil_data = {
                'P' : manual_data['P'],
                'N': manual_data['N'],
                'K': manual_data['K'],
                'ph': manual_data['pH'],
                'Temperature (°C)': manual_data['Temperature (°C)'],
                'Humidity (%)': manual_data['Humidity (%)'],
                'Rainfall (mm)': manual_data['Rainfall (mm)']
            }
        logging.debug(Csoil_data)
        CropRecommend = ml_function.predict_crop(latitude,longitude,Csoil_data);
        
        if 'error' in CropRecommend:
            return jsonify(CropRecommend), 500  # Handle error case
        
        return jsonify(CropRecommend)
        
    except Exception as e:
        logging.error(f"❌ AI API Error: {str(e)}")
        return jsonify({"error": f"Failed to Extract Description: {str(e)}"}), 500



if __name__ == '__main__':
    logging.info("🚀 Starting Flask server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=3000, debug=True)
