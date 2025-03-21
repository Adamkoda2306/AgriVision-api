from flask import Flask, request, jsonify
import os
import random
import logging
import requests

app = Flask(__name__)

# 🔹 Enable Debug Logging
logging.basicConfig(level=logging.DEBUG)

# 🔹 Load 2Factor API Key
TWOFACTOR_API_KEY = "a07a23ed-f513-11ef-8b17-0200cd936042"

TEMPLATE_ID = "AgriVision-Template"

if not TWOFACTOR_API_KEY:
    logging.error("\u274c 2Factor API key is missing! Set it as an environment variable.")

# 🔹 Store OTPs temporarily (Use DB for production)
otp_store = {}

@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    phone = data.get("phone")
    
    logging.debug(f"\ud83d\udce9 Received OTP request for: {phone}")

    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    phone = "+91" + phone[-10:]  # Ensure proper format
    otp = random.randint(1000, 9999)  # Generates a 4-digit OTP
    otp_store[phone] = otp

    logging.debug(f"\u2705 Generated OTP: {otp} for {phone}")

    try:
        response = requests.get(
            f"https://2factor.in/API/V1/{TWOFACTOR_API_KEY}/SMS/{phone}/{otp}/{TEMPLATE_ID}"
        )
        result = response.json()
        
        if result.get("Status") == "Success":
            logging.debug(f"\u2705 2Factor Response: {result}")
            return jsonify({"message": "OTP sent successfully", "session_id": result.get("Details")})
        else:
            logging.error(f"\u274c 2Factor Error: {result}")
            return jsonify({"error": "Failed to send OTP"}), 500
    except Exception as e:
        logging.error(f"\u274c API Error: {str(e)}")
        return jsonify({"error": f"Failed to send OTP: {str(e)}"}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    phone = data.get("phone")
    otp = data.get("otp")

    logging.debug(f"\ud83d\udd0d Verifying OTP for {phone} - Entered OTP: {otp}")

    if not phone or not otp:
        return jsonify({"error": "Phone and OTP are required"}), 400

    if otp_store.get(phone) == int(otp):
        del otp_store[phone]
        logging.debug(f"\u2705 OTP Verified for {phone}")
        return jsonify({"message": "OTP Verified Successfully"})
    else:
        logging.warning(f"\u274c Invalid OTP attempt for {phone}")
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

if __name__ == '__main__':
    logging.info("\ud83d\ude80 Starting Flask server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
