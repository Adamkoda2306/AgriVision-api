import ee
import os
import requests
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()
def _init_gee():
    try:
        import json
        key_file = os.getenv("GEE_KEY_FILE")
        key_json = os.getenv("GEE_SERVICE_ACCOUNT_KEY")

        if key_file and os.path.exists(key_file):
            with open(key_file, "r") as f:
                key_data = json.load(f)
            
            key_data["private_key"] = key_data["private_key"].replace("\\n", "\n")
            credentials = ee.ServiceAccountCredentials(
                key_data["client_email"],
                key_data=json.dumps(key_data)
            )
        elif key_json:
            key_data = json.loads(key_json)
            
            key_data["private_key"] = key_data["private_key"].replace("\\n", "\n")
            credentials = ee.ServiceAccountCredentials(
                key_data["client_email"],
                key_data=json.dumps(key_data)
            )
        else:
            ee.Initialize()
            return True

        ee.Initialize(credentials)
        return True
    except Exception as e:
        print(f"GEE init failed: {e}")
        return False

_GEE_READY = _init_gee()


_INDIA_STATE_SOIL = {
    "andhra pradesh": {"ph": 7.2, "N": 280, "cec": 17.0, "P": 53.0, "K": 48.0},
    "telangana":      {"ph": 7.0, "N": 260, "cec": 16.5, "P": 51.0, "K": 46.0},
    "karnataka":      {"ph": 6.5, "N": 240, "cec": 15.5, "P": 49.0, "K": 44.0},
    "tamil nadu":     {"ph": 7.5, "N": 300, "cec": 18.5, "P": 55.0, "K": 50.0},
    "kerala":         {"ph": 5.8, "N": 210, "cec": 13.0, "P": 44.0, "K": 40.0},
    "maharashtra":    {"ph": 7.8, "N": 320, "cec": 19.0, "P": 57.0, "K": 52.0},
    "punjab":         {"ph": 8.1, "N": 360, "cec": 21.0, "P": 62.0, "K": 56.0},
    "gujarat":        {"ph": 7.6, "N": 310, "cec": 18.0, "P": 55.0, "K": 50.0},
    "odisha":         {"ph": 6.2, "N": 250, "cec": 14.5, "P": 47.0, "K": 43.0},
    "west bengal":    {"ph": 6.0, "N": 245, "cec": 14.0, "P": 46.0, "K": 42.0},
    "uttar pradesh":  {"ph": 7.9, "N": 330, "cec": 19.5, "P": 58.0, "K": 53.0},
    "madhya pradesh": {"ph": 7.3, "N": 290, "cec": 17.5, "P": 53.0, "K": 48.0},
    "rajasthan":      {"ph": 8.2, "N": 340, "cec": 20.0, "P": 60.0, "K": 54.0},
    "bihar":          {"ph": 7.1, "N": 275, "cec": 16.8, "P": 52.0, "K": 47.0},
    "assam":          {"ph": 5.5, "N": 210, "cec": 12.0, "P": 42.0, "K": 38.0},
}

_REGIONAL_SOIL = {
    "INDIA":   {"ph": 6.8, "N": 280, "cec": 18.0, "P": 53.0, "K": 48.0},
    "AFRICA":  {"ph": 6.2, "N": 220, "cec": 14.0, "P": 45.0, "K": 40.0},
    "USA":     {"ph": 6.5, "N": 300, "cec": 20.0, "P": 58.0, "K": 52.0},
    "SE_ASIA": {"ph": 5.8, "N": 200, "cec": 12.0, "P": 40.0, "K": 36.0},
    "EUROPE":  {"ph": 6.9, "N": 270, "cec": 22.0, "P": 56.0, "K": 50.0},
    "LATAM":   {"ph": 5.9, "N": 230, "cec": 13.0, "P": 44.0, "K": 39.0},
    "DEFAULT": {"ph": 6.5, "N": 260, "cec": 16.0, "P": 53.0, "K": 48.0}
}


def _detect_region(lat, lon):
    if   8   <= lat <= 37  and  68  <= lon <=  97: return "INDIA"
    elif -35  <= lat <= 37  and -18  <= lon <=  52: return "AFRICA"
    elif 25   <= lat <= 83  and -168 <= lon <= -52: return "USA"
    elif -10  <= lat <= 28  and  92  <= lon <= 141: return "SE_ASIA"
    elif 35   <= lat <= 71  and -10  <= lon <=  40: return "EUROPE"
    elif -55  <= lat <= 32  and -82  <= lon <= -34: return "LATAM"
    else:                                            return "DEFAULT"


def _get_india_state(lat, lon):
    try:
        res = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "soil-app/1.0"},
            timeout=10,
        )
        res.raise_for_status()
        return res.json().get("address", {}).get("state", "").lower()
    except Exception:
        return None


def _soil_fallback(lat=None, lon=None, reason="Live APIs unavailable"):
    region = _detect_region(lat, lon) if lat is not None else "DEFAULT"
    if region == "INDIA" and lat is not None:
        state = _get_india_state(lat, lon)
        if state:
            for key, data in _INDIA_STATE_SOIL.items():
                if key in state:
                    result = data.copy()
                    result["soil_type"] = f"{key.title()} state average (ICAR)"
                    result["warning"] = (
                        f"Live soil APIs unavailable ({reason}). "
                        f"Using ICAR state average for {key.title()}. "
                        f"Estimates only — not field measurements."
                    )
                    return result
    data = _REGIONAL_SOIL[region].copy()
    data["warning"] = (
        f"Live soil APIs unavailable ({reason}). "
        f"Using {region} regional average. "
        f"Estimates only — not field measurements."
    )
    return data


def _try_gee(lat, lon):
    try:
        point = ee.Geometry.Point([lon, lat])
        ph_val = (
            ee.Image("OpenLandMap/SOL/SOL_PH-H2O_USDA-4C1A2A_M/v02")
            .select("b0").sample(point, 250).first().get("b0").getInfo()
        )
        oc_val = (
            ee.Image("OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02")
            .select("b0").sample(point, 250).first().get("b0").getInfo()
        )
        if ph_val is None:
            return None
        oc  = round(oc_val * 5, 2) if oc_val is not None else None
        n   = round(oc * 1000 * 0.05 * 0.1, 2) if oc is not None else None
        cec = round(oc * 0.58, 2) if oc is not None else None
        fallback = _soil_fallback(lat, lon, reason="P/K not available from GEE")
        p = fallback.get("P", 53.0)
        k = fallback.get("K", 48.0)
        return {
            "ph":     round(ph_val / 10, 2),
            "N":      n,
            "cec":    cec,
            "P":      p,
            "K":      k,
            "source": "GEE OpenLandMap 250m (P/K from regional avg)",
        }
    except Exception as e:
        print(f"GEE soil query failed: {e}")
        return None


def _try_openepi(lat, lon, retries=2, backoff=2):
    for attempt in range(1, retries + 1):
        try:
            res = requests.get(
                "https://api.openepi.io/soil/property",
                params={"lat": lat, "lon": lon, "depths": ["0-5cm"],
                        "properties": ["phh2o", "nitrogen", "cec"], "values": ["mean"]},
                timeout=15,
            )
            if res.status_code in (502, 503, 504, 530):
                if attempt < retries:
                    time.sleep(backoff * attempt)
                    continue
                return None
            res.raise_for_status()
            return _parse_soil_response(res.json(),lat,lon)
        except requests.RequestException:
            if attempt < retries:
                time.sleep(backoff * attempt)
    return None


def _try_soilgrids(lat, lon, retries=2, backoff=2):
    url = (
        f"https://rest.isric.org/soilgrids/v2.0/properties/query"
        f"?lat={lat}&lon={lon}&property=phh2o&property=nitrogen"
        f"&property=cec&depth=0-5cm&value=mean"
    )
    for attempt in range(1, retries + 1):
        try:
            res = requests.get(url, timeout=15)
            if res.status_code in (502, 503, 504, 530):
                if attempt < retries:
                    time.sleep(backoff * attempt)
                    continue
                return None
            res.raise_for_status()
            return _parse_soil_response(res.json(),lat,lon)
        except requests.RequestException:
            if attempt < retries:
                time.sleep(backoff * attempt)
    return None


def _parse_soil_response(data,lat,lon):
    features = {}
    for layer in data.get("properties", {}).get("layers", []):
        name = layer.get("name", "").lower()
        mean = layer.get("depths", [{}])[0].get("values", {}).get("mean")
        if name == "phh2o":
            features["ph"]  = round(mean / 10, 2) if mean is not None else None
        elif name == "nitrogen":

            features["N"]   = round(mean * 10, 2) if mean is not None else None
        elif name == "cec":
            features["cec"] = round(mean / 10, 2) if mean is not None else None
    if not features:
        return None
    fallback = _soil_fallback(lat, lon, reason="P/K not in SoilGrids")
    features["P"] = fallback.get("P", 53.0)
    features["K"] = fallback.get("K", 48.0)

    return features


def get_soil_data(lat, lon):
    if _GEE_READY:
        result = _try_gee(lat, lon)
        if result:
            return result
    result = _try_openepi(lat, lon)
    if result:
        return result
    result = _try_soilgrids(lat, lon)
    if result:
        return result
    return _soil_fallback(lat, lon, reason="GEE + OpenEPI + SoilGrids all failed")


def get_weather_data(lat, lon):
    url = (
        f"http://api.agromonitoring.com/agro/1.0/weather"
        f"?lat={lat}&lon={lon}&appid={os.getenv('AGROMONITORING_API_KEY')}"
    )
    res = requests.get(url, timeout=10)
    data = res.json()
    temp = data.get("main", {}).get("temp")
    if temp is not None:
        temp -= 273.15
    return {
    "Temperature (°C)": round(temp, 2) if temp is not None else None,
    "Humidity (%)":      data.get("main", {}).get("humidity"),
    "Rainfall (mm)":     data.get("rain", {}).get("1h", 0),
    }


def get_combined_data(lat, lon):
    soil = get_soil_data(lat, lon)
    weather = get_weather_data(lat, lon)
    return {**soil, **weather}


def get_weather_forecast(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={os.getenv('OPENWEATHERMAP_API_KEY')}&units=metric"
    )
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        today    = datetime.now(timezone.utc).date()
        forecast = {}

        for entry in data.get("list", []):
            dt   = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            date = dt.date()
            if date > today:
                if date not in forecast:
                    forecast[date] = {"temps": [], "humidity": [], "rain": 0, "wind": []}
                forecast[date]["temps"].append(entry["main"]["temp"])
                forecast[date]["humidity"].append(entry["main"]["humidity"])
                forecast[date]["rain"] += entry.get("rain", {}).get("3h", 0)
                forecast[date]["wind"].append(entry["wind"]["speed"])

        forecast_data = [
            {
                "Date":                 str(date),
                "Avg Temperature (°C)": round(sum(v["temps"])    / len(v["temps"]),    2),
                "Avg Humidity (%)":     round(sum(v["humidity"]) / len(v["humidity"]), 2),
                "Total Rainfall (mm)":  round(v["rain"], 2),
                "Avg Wind Speed (m/s)": round(sum(v["wind"])     / len(v["wind"]),     2),
            }
            for date, v in sorted(forecast.items())
        ][:6]

        return {"forecast": forecast_data}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch weather forecast: {e}"}


def get_today_forecast(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={os.getenv('OPENWEATHERMAP_API_KEY')}&units=metric"
    )
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data  = res.json()
        today = datetime.now(timezone.utc).date()

        for entry in data.get("list", []):
            dt = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            if dt.date() == today:
                return {"today": {
                    "Date":             str(today),
                    "Temperature (°C)": entry["main"]["temp"],
                    "Humidity (%)":     entry["main"]["humidity"],
                    "Rainfall (mm)":    entry.get("rain", {}).get("3h", 0),
                    "Wind Speed (m/s)": entry["wind"]["speed"],
                }}

        return {"error": "No forecast available for today."}
    except requests.RequestException as e:
        return {"error": f"Failed to fetch today's forecast: {e}"}


def get_soil_moisture(lat, lon):
    url = (
        f"http://api.agromonitoring.com/agro/1.0/soil"
        f"?lat={lat}&lon={lon}&appid={os.getenv('AGROMONITORING_API_KEY')}"
    )
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return {"soil_moisture": res.json().get("moisture")}
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
    try:
        parts = [p.strip() for p in disease_input.replace(')', '(').split('(') if p.strip()]
        disease_name = parts[0]
        code = None
        crop = None
        for part in parts[1:]:
            if part in ('P','A'):  # Disease type codes
                code = part
            else:
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
    headers = {
        "Authorization": f"Bearer {os.getenv('HUGGINGFACE_AI_KEY')}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model":       "Qwen/Qwen2.5-72B-Instruct",
        "messages":    [{"role": "user", "content": prompt}],
        "max_tokens":  400,
        "temperature": 0.6,
    }
    try:
        response = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            json=payload, headers=headers, timeout=60,
        )
        if response.status_code == 401:
            return "Error: Invalid HuggingFace token."
        if response.status_code == 403:
            return "Error: Token lacks Inference Providers permission."
        if response.status_code == 404:
            return "Error: Model not found."
        if response.status_code == 429:
            return "Rate limit reached. Try again shortly."
        if response.status_code == 402:
            return "Monthly free quota exhausted."
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"API Error: {str(e)}"


def clean_response(text):
    unwanted_phrases = [
        "Present in markdown format with clear headers",
        "Add emojis relevant to agriculture",
        "Use reliable sources for information",
        "Format in markdown sections"
    ]
    for phrase in unwanted_phrases:
        text = text.replace(phrase, '')
    return text.strip()
if __name__ == "__main__":
    LAT, LON = 13.6288, 79.4192
 
    results = {"passed": 0, "failed": 0}
 
    def ok(msg):   print(f"  ✔ PASS  {msg}"); results["passed"] += 1
    def fail(msg): print(f"  ✘ FAIL  {msg}"); results["failed"] += 1
    def warn(msg): print(f"  ⚠ WARN  {msg}")
    def check(cond, msg): ok(msg) if cond else fail(msg)
    def section(t): print(f"\n{'─'*55}\n  {t}\n{'─'*55}")
 
    # ── 1. GEE ────────────────────────────────────────────────────────────────
    section("1. GEE initialisation")
    if _GEE_READY:
        ok("GEE initialised — Tier 1 active")
    else:
        warn("GEE not initialised — falling back to Tier 2/3/4")
 
    # ── 2. Soil chain ─────────────────────────────────────────────────────────
    section("2. Soil — 4-tier chain")
    print(f"  Querying soil for lat={LAT}, lon={LON} ...")
    soil = get_soil_data(LAT, LON)
    check(isinstance(soil, dict) and len(soil) > 0, "Soil chain returned a dict")
    check(all(k in soil for k in ("ph", "N", "P", "K", "cec")), "All keys present (ph, N, P, K, cec)")
    if "GEE" in str(soil.get("source", "")):
        ok(f"Tier 1 (GEE) — ph={soil.get('ph')}, N={soil.get('N')}, cec={soil.get('cec')}")
    elif "warning" in soil:
        warn(f"Fallback used: {soil['warning']}")
        check(soil["ph"] is not None, "Fallback ph is not None")
    else:
        ok(f"Live API responded — ph={soil.get('ph')}, N={soil.get('N')}")
        if soil.get("ph"):
            check(3.0 <= soil["ph"] <= 10.0, f"pH in valid range: {soil['ph']}")
 
    fb = _soil_fallback(LAT, LON)
    check("warning" in fb and fb["ph"] is not None, "_soil_fallback() returns regional average + warning")
 
    # ── 3. Weather forecast ───────────────────────────────────────────────────
    section("3. OpenWeatherMap — forecast & today")
    print("  Fetching 6-day forecast ...")
    fc = get_weather_forecast(LAT, LON)
    if "error" in fc:
        warn(f"Forecast error: {fc['error']}")
    else:
        days = fc.get("forecast", [])
        check(len(days) > 0, f"Forecast returned {len(days)} day(s)")
        if days:
            check(all(k in days[0] for k in ("Date", "Avg Temperature (°C)", "Total Rainfall (mm)")),
                  "Forecast entries have expected keys")
            today = datetime.now(timezone.utc).date()
            check(all(datetime.strptime(d["Date"], "%Y-%m-%d").date() > today for d in days),
                  "All forecast dates are in the future")
 
    print("  Fetching today's forecast ...")
    td = get_today_forecast(LAT, LON)
    if "error" in td:
        warn(f"Today forecast: {td['error']}")
    else:
        check("today" in td and td["today"] is not None, f"Today's data: {td['today']}")
 
    # ── 4. AI response ────────────────────────────────────────────────────────
    section("4. HuggingFace — Qwen2.5-72B-Instruct:auto")
    print("  Sending test prompt ...")
    resp = get_ai_response("In one sentence, what is rice blast disease?")
    if "402" in resp:
        warn("Monthly quota exhausted")
    elif "429" in resp:
        warn("Rate limit hit — wait and retry")
    else:
        check(isinstance(resp, str) and len(resp) > 10
              and not any(e in resp for e in ("Error", "404", "410", "403")),
              f"AI response ({len(resp)} chars): {resp[:100]}...")
 
    # ── 5. Disease info ───────────────────────────────────────────────────────
    section("5. get_disease_info — input parsing")
    r = get_disease_info("Rice Blast (P)(Rice)")
    check(not (isinstance(r, dict) and "error" in r), "Valid input parsed without error")
    check(isinstance(get_disease_info("Unknown Disease"), dict)
          and "error" in get_disease_info("Unknown Disease"),
          "Missing crop returns error dict")
 
    # ── 6. Weather alerts ─────────────────────────────────────────────────────
    section("6. generate_weather_alerts — logic")
    check(any("Heavy"         in a for a in generate_weather_alerts(15, 5)),  "Rainfall > 10 mm → Heavy alert")
    check(any("Moderate Rain" in a for a in generate_weather_alerts(7,  5)),  "Rainfall 5–10 mm → Moderate alert")
    check(any("Strong Wind"   in a for a in generate_weather_alerts(0, 20)),  "Wind > 15 m/s → Strong Wind alert")
    check(generate_weather_alerts(0, 0) == ["No severe weather conditions expected."],
          "No rain/wind → default safe message")
 
    # ── 7. Soil moisture ──────────────────────────────────────────────────────
    section("7. get_soil_moisture — AgroMonitoring")
    print("  Fetching soil moisture ...")
    sm = get_soil_moisture(LAT, LON)
    if "error" in sm:
        warn(f"Soil moisture error: {sm['error']}")
    else:
        check("soil_moisture" in sm, f"Soil moisture: {sm.get('soil_moisture')}")
 
    # ── Summary ───────────────────────────────────────────────────────────────
    section("Summary")
    total = results["passed"] + results["failed"]
    print(f"  ✔ {results['passed']} passed  |  ✘ {results['failed']} failed  |  {total} total\n")
 