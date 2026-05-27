import json
import sys
from source import ml_function, utils
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")


def get_crop_recommendation(lat, lon):
    """
    Get crop recommendation based on location and manual data.
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
    Returns:
        dict: Crop recommendation result
    """
    try:
        model_bundle = ml_function.load_model()
        result = ml_function.give_crop(lat, lon, manual_data=get_land_data(lat, lon))
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_weather(lat, lon):
    """
    Get weather forecast for given coordinates.
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
    Returns:
        dict: Weather forecast data
    """
    try:
        result = utils.get_weather_forecast(lat, lon)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
    

def get_today_weather(lat, lon):
    """
    Get weather forecast for given coordinates.
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
    Returns:
        dict: Weather forecast data
    """
    try:
        result = utils.get_today_forecast(lat, lon)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_fertilizer_recommendation(lat, lon, crop):
    """
    Get fertilizer recommendation based on crop and soil data.
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
        manual_data (string): Crop name
    Returns:
        dict: Fertilizer recommendation result
    """
    try:
        soil_data = utils.get_combined_data(lat, lon)
        result = ml_function.get_fertilizer_suggestion(soil_data, crop)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_land_data(lat, lon):
    """
    Get soil and weather data for given coordinates.
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
    Returns:
        dict: Soil + Weather data
    """
    try:
        result = utils.get_combined_data(lat, lon)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}



def get_disease_prediction(crop_disease):
    """
    Get disease prediction and information.
    Args:
        crop_disease (str): Crop disease name
    Returns:
        dict: Disease information
    """
    try:
        result = utils.get_disease_info(crop_disease)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def process_request(request_type, params):
    """
    Process different types of requests.
    Args:
        request_type (str): Type of request (crop, weather, fertilizer, soil, disease)
        params (dict): Parameters for the request
    Returns:
        dict: Result of the request
    """
    try:
        if request_type == "crop":
            return get_crop_recommendation(
                params.get("lat"),
                params.get("lon"),
                params.get("manual_data")
            )
        elif request_type == "weather":
            return get_weather(params.get("lat"), params.get("lon"))
        elif request_type == "fertilizer":
            return get_fertilizer_recommendation(
                params.get("lat"),
                params.get("lon"),
                params.get("crop")
            )
        elif request_type == "manual_data":
            return get_land_data(params.get("lat"), params.get("lon"))
        elif request_type == "weather_today":
            return get_today_weather(params.get("lat"), params.get("lon"))
        elif request_type == "disease":
            return get_disease_prediction(params.get("crop_disease"))
        else:
            return {"success": False, "error": f"Unknown request type: {request_type}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps({
            "error": "Usage: python agrivision_predict.py <request_type> <json_params>"
        }))
        sys.exit(1)

    request_type = sys.argv[1]
    params_json = sys.argv[2]

    try:
        params = json.loads(params_json)
        if not isinstance(params, dict):
            raise ValueError("Parameters must be a JSON object (dictionary).")
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    result = process_request(request_type, params)
    print(json.dumps(result))