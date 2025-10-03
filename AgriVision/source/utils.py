import requests
import os
from datetime import datetime

def get_soil_data(lat, lon):
    url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lat={lat}&lon={lon}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        
        features = {}
        for layer in data.get('properties', {}).get('layers', []):
            name = layer['name'].lower()
            mean = layer.get('depths', [{}])[0].get('values', {}).get('mean')
            if name in ['phh2o', 'ph']:
                features['ph'] = round(mean / 10, 2) if mean is not None else None
            elif name in ['nitrogen', 'n']:
                features['N'] = round(mean, 2) if mean is not None else None
            elif name == 'cec':
                features['cec'] = round(mean, 2) if mean is not None else None
            else:
                features.setdefault('soil_type', layer['name'])
        features['P'] = round(features.get("cec", 0) * 0.5, 2)
        features['K'] = round(features.get("cec", 0) * 0.3, 2)
        return features

    except requests.RequestException as e:
        return {"error": f"Failed to fetch soil data: {e}"}

def get_weather_data(lat, lon):
    url = f"http://api.agromonitoring.com/agro/1.0/weather?lat={lat}&lon={lon}&appid={os.getenv('AGROMONITORING_API_KEY')}"
    res = requests.get(url)
    data = res.json()
    temp = data.get("main", {}).get("temp")
    if temp is not None:
        temp -= 273.15
    return {
        "temperature": temp,
        "humidity": data.get("main", {}).get("humidity"),
        "rainfall": data.get("rain", {}).get("1h", 0)
    }

def get_combined_data(lat, lon):
    soil = get_soil_data(lat, lon)
    weather = get_weather_data(lat, lon)
    return {**soil, **weather}

def get_weather_forecast(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={os.getenv('OPENWEATHERMAP_API_KEY')}&units=metric"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        
        forecast = {}
        today = datetime.utcnow().date()
        today_weather = None
        
        for entry in data.get("list", []):
            date = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S").date()
            temp = entry["main"]["temp"]
            humidity = entry["main"]["humidity"]
            rainfall = entry.get("rain", {}).get("3h", 0)
            wind = entry["wind"]["speed"]
            
            if date == today:
                today_weather = {
                    "Date": str(date),
                    "Temperature (°C)": temp,
                    "Humidity (%)": humidity,
                    "Rainfall (mm)": rainfall,
                    "Wind Speed (m/s)": wind
                }
            elif date > today:
                if date not in forecast:
                    forecast[date] = {"temps": [], "humidity": [], "rain": 0, "wind": []}
                forecast[date]["temps"].append(temp)
                forecast[date]["humidity"].append(humidity)
                forecast[date]["rain"] += rainfall
                forecast[date]["wind"].append(wind)
        
        forecast_data = [{
            "Date": str(date),
            "Avg Temperature (°C)": sum(vals["temps"]) / len(vals["temps"]),
            "Avg Humidity (%)": sum(vals["humidity"]) / len(vals["humidity"]),
            "Total Rainfall (mm)": vals["rain"],
            "Avg Wind Speed (m/s)": sum(vals["wind"]) / len(vals["wind"])
        } for date, vals in sorted(forecast.items())][:6]
        
        return {"forecast": forecast_data}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch weather forecast: {e}"}

def get_today_forecast(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={os.getenv('OPENWEATHERMAP_API_KEY')}&units=metric"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        
        today = datetime.utcnow().date()

        today_weather = None
        
        for entry in data.get("list", []):
            date = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S").date()
            if date == today:
                today_weather = {
                    "Date": str(date),
                    "Temperature (°C)": entry["main"]["temp"],
                    "Humidity (%)": entry["main"]["humidity"],
                    "Rainfall (mm)": entry.get("rain", {}).get("3h", 0),
                    "Wind Speed (m/s)": entry["wind"]["speed"]
                }
                break
        
        return {"today": today_weather} if today_weather else {"error": "No forecast available for today."}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch today's forecast: {e}"}

def get_soil_moisture(lat, lon):
    url = f"http://api.agromonitoring.com/agro/1.0/soil?lat={lat}&lon={lon}&appid={os.getenv('AGROMONITORING_API_KEY')}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        return {"soil_moisture": data.get("moisture")}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch soil moisture: {e}"}

def generate_weather_alerts(rainfall, wind_speed):
    alerts = []
    if rainfall > 10:
        alerts.append("Heavy Rainfall Alert: Expect significant rain, take necessary precautions!")
    elif rainfall > 5:
        alerts.append("Moderate Rainfall Alert: Possibility of rain, plan accordingly.")
    
    if wind_speed > 15:
        alerts.append("Strong Wind Alert: High wind speeds detected, be cautious!")
    elif wind_speed > 10:
        alerts.append("Moderate Wind Alert: Expect breezy conditions.")
    
    return alerts if alerts else ["No severe weather conditions expected."]


def get_disease_info(disease_input):
    """Process disease names with type codes and crop information"""
    try:
        parts = [p.strip() for p in disease_input.replace(')', '(').split('(') if p.strip()]
        
        disease_name = parts[0]
        code = None
        crop = None
        
        for part in parts[1:]:
            if part in ('P', 'A'):  # Disease type codes
                code = part
            else:  # Crop name
                crop = part
        
        full_disease_name = disease_name
        if code:
            full_disease_name += f" ({code})"
        
        if not crop:
            return {"error": "Crop name is missing. Please provide a valid crop."}
        
        prompt = f"""Provide a detailed and structured explanation about {full_disease_name} affecting {crop} crops.
        Include:
        - Disease Type: {'Pest' if code=='P' else 'Abiotic' if code=='A' else 'Biological'}
        - Symptoms
        - Recommended Chemical Controls with Dosage
        - Biological/Organic Treatments
        - Prevention Strategies
        - Growth Stage Most Affected
        Ensure clarity and completeness in your response."""
        
        response = get_ai_response(prompt)
        return clean_response(response) if response else {"error": "Failed to retrieve disease information."}
    except Exception as e:
        return {"error": f"Error processing disease information: {str(e)}"}

def get_fertilizer_recommendation(soil_data, crop):
    """Get fertilizer recommendation using Hugging Face API"""
    prompt = f"""As a soil expert, recommend fertilizers for {crop} based on:
    - N: {soil_data.get('N', 0)} mg/kg
    - P: {soil_data.get('P', 0)} mg/kg
    - K: {soil_data.get('K', 0)} mg/kg
    - pH: {soil_data.get('ph', 6.5)}
    - Moisture: {soil_data.get('soil_moisture', 0)}%
    
    Include:
    1. Recommended NPK ratio
    2. Application schedule
    3. Organic alternatives
    4. Soil amendment suggestions
    Format in markdown sections."""
    
    return clean_response(get_ai_response(prompt))

def get_ai_response(prompt):
    """With improved error handling"""
    url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_AI_KEY')}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 400,
            "temperature": 0.6
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 403:
            return "Error: Model access denied. Accept terms at: https://huggingface.co/HuggingFaceH4/zephyr-7b-beta"
            
        if response.status_code == 429:
            return "API Limit reached (free tier). Try again later."
            
        response.raise_for_status()
        return response.json()[0]['generated_text']
        
    except Exception as e:
        return f"API Error: {str(e)}"
    



def clean_response(text):
    """Remove unwanted instructions from the response"""
    unwanted_phrases = [
        "Present in markdown format with clear headers",
        "Add emojis relevant to agriculture",
        "Use reliable sources for information",
        "Format in markdown sections"
    ]
    
    for phrase in unwanted_phrases:
        text = text.replace(phrase, '')
    return text.strip()
