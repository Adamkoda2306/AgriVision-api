from flask import Flask, request, jsonify
import logging
from AgriVision.source import utils  # Assuming your utils file is in the specified path

app = Flask(__name__)

@app.route('/predicttodayWeather', methods=['POST'])
def predict_today_weather():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    
    try:
        logging.debug(f"✅ Weather Data Extracted Successfully")
        
        # Call the function from utils to fetch weather data
        weather_data = utils.get_today_forecast(latitude, longitude)
        
        if 'error' in weather_data:
            return jsonify(weather_data), 500  # Handle error case
        
        return jsonify(weather_data)
        
    except Exception as e:
        logging.error(f"❌ WeatherData Error: {str(e)}")
        return jsonify({"error": f"Failed to Extract Weather: {str(e)}"}), 500

@app.route('/predictforecastWeather', methods=['POST'])
def predict_forecast_weather():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    
    try:
        logging.debug(f"✅ Weather Data Extracted Successfully")
        
        # Call the function from utils to fetch weather data
        weather_data = utils.get_weather_forecast(latitude, longitude)
        
        if 'error' in weather_data:
            return jsonify(weather_data), 500  # Handle error case
        
        return jsonify(weather_data)
        
    except Exception as e:
        logging.error(f"❌ WeatherData Error: {str(e)}")
        return jsonify({"error": f"Failed to Extract Weather: {str(e)}"}), 500

if __name__ == '__main__':
    logging.info("🚀 Starting Flask server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5050, debug=True)
