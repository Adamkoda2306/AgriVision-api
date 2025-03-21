import requests
from datetime import datetime
from AgriVision.source import ml_function, utils
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

def get_crop_recommendation(lat, lon, manual_data):
    #model_bundle = model.train_model("data/Crop_recommendation.csv")
    model_bundle = ml_function.load_model("models/crop_model.pkl")
    return ml_function.predict_crop(lat, lon, model_bundle, manual_data=manual_data)


def get_weather(lat, lon):
    return utils.get_weather_forecast(lat, lon)

def get_fertilizer_recommendation(lat, lon, manual_data):
    soil_data = utils.get_combined_data(lat, lon)
    recommended_crop = get_crop_recommendation(lat, lon, manual_data)
    return ml_function.get_fertilizer_suggestion(soil_data, recommended_crop)

def get_soil_moisture(lat, lon):
    return utils.get_soil_moisture(lat, lon)

def get_weather_alerts(forecast):
    return utils.generate_weather_alerts(forecast.get("Rainfall (mm)", 0), forecast.get("Wind Speed (m/s)", 0))

def get_disease_prediction(crop_disease):
    return utils.get_disease_info(crop_disease)