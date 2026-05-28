import os
import json
import requests
from typing import Dict, Any

# Healthy disease default response
HEALTHY_RESPONSE = {
    "english": {
        "symptoms": [
            {
                "title": "Healthy Plant",
                "description": "No disease detected. The plant is in good condition.",
            }
        ],
        "treatment": {
            "spray_name": "N/A",
            "dosage": "N/A",
            "frequency": "0",
        },
    },
    "hindi": {
        "symptoms": [
            {
                "title": "स्वस्थ पौधा",
                "description": "कोई रोग नहीं पाया गया। पौधा अच्छी स्थिति में है।",
            }
        ],
        "treatment": {
            "spray_name": "N/A",
            "dosage": "N/A",
            "frequency": "0",
        },
    },
    "telugu": {
        "symptoms": [
            {
                "title": "ఆరోగ్యకరమైన మొక్క",
                "description": "ఎటువంటి వ్యాధి కనుగొనబడలేదు. మొక్క మంచి స్థితిలో ఉంది.",
            }
        ],
        "treatment": {
            "spray_name": "N/A",
            "dosage": "N/A",
            "frequency": "0",
        },
    },
    "tamil": {
        "symptoms": [
            {
                "title": "ஆரோக்கியமான செடி",
                "description": "நோய் கண்டறியப்படவில்லை. செடி நல்ல நிலையில் உள்ளது.",
            }
        ],
        "treatment": {
            "spray_name": "N/A",
            "dosage": "N/A",
            "frequency": "0",
        },
    },
    "punjabi": {
        "symptoms": [
            {
                "title": "ਸਵਸਥ ਪੌਦਾ",
                "description": "ਕੋਈ ਰੋਗ ਨਹੀਂ ਮਿਲਿਆ। ਪੌਦਾ ਚੰਗੀ ਸਥਿਤੀ ਵਿੱਚ ਹੈ।",
            }
        ],
        "treatment": {
            "spray_name": "N/A",
            "dosage": "N/A",
            "frequency": "0",
        },
    },
}

# No Leaf Found response
NO_LEAF_RESPONSE = {
    "english": {
        "symptoms": [
            {
                "title": "No Leaf of the Plant",
                "description": "This is not the image of the plant or image is not clear",
            }
        ],
        "treatment": {
            "spray_name": "N/A",
            "dosage": "N/A",
            "frequency": "0",
        },
    },
    "hindi": {
        "symptoms": [
            {
                "title": "पौधे की पत्ती नहीं",
                "description": "यह पौधे की छवि नहीं है या छवि स्पष्ट नहीं है",
            }
        ],
        "treatment": {
            "spray_name": "N/A",
            "dosage": "N/A",
            "frequency": "0",
        },
    },
    "telugu": {
        "symptoms": [
            {
                "title": "మొక్క యొక్క ఆకు లేదు",
                "description": "ఇది మొక్క యొక్క చిత్రం కాదు లేదా చిత్రం స్పష్టం కాదు",
            }
        ],
        "treatment": {
            "spray_name": "N/A",
            "dosage": "N/A",
            "frequency": "0",
        },
    },
    "tamil": {
        "symptoms": [
            {
                "title": "செடியின் இலை இல்லை",
                "description": "இது செடியின் படம் இல்லை அல்லது படம் தெளிவாக இல்லை",
            }
        ],
        "treatment": {
            "spray_name": "N/A",
            "dosage": "N/A",
            "frequency": "0",
        },
    },
    "punjabi": {
        "symptoms": [
            {
                "title": "ਪੌਦੇ ਦੀ ਪੱਤੀ ਨਹੀਂ",
                "description": "ਇਹ ਪੌਦੇ ਦੀ ਤਸਵੀਰ ਨਹੀਂ ਹੈ ਜਾਂ ਤਸਵੀਰ ਸਪਸ਼ਟ ਨਹੀਂ ਹੈ",
            }
        ],
        "treatment": {
            "spray_name": "N/A",
            "dosage": "N/A",
            "frequency": "0",
        },
    },
}


def is_healthy_disease(disease_name: str) -> bool:
    """Check if the disease is a healthy plant condition"""
    return "healthy" in disease_name.lower()


def is_no_leaf_found(disease_name: str) -> bool:
    """Check if no leaf was found"""
    return "no leaf found" in disease_name.lower()


def get_ai_response(prompt: str) -> str:
    """
    Get response from HuggingFace AI API
    
    Args:
        prompt: The prompt to send to the AI
        
    Returns:
        The AI response as a string
    """
    headers = {
        "Authorization": f"Bearer {os.getenv('HUGGINGFACE_AI_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.6,
    }
    try:
        response = requests.post(
            "https://router.huggingface.co/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=60,
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


def parse_ai_response_to_json(ai_response: str) -> Dict[str, Any]:
    """
    Parse AI response to structured JSON format
    
    Args:
        ai_response: Raw AI response
        
    Returns:
        Parsed JSON response
    """
    try:
        # Try to extract JSON if it's wrapped in markdown
        if "```json" in ai_response:
            json_str = ai_response.split("```json")[1].split("```")[0].strip()
        elif "```" in ai_response:
            json_str = ai_response.split("```")[1].split("```")[0].strip()
        else:
            json_str = ai_response
        
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response as JSON"}


def get_disease_info(disease_name: str) -> Dict[str, Any]:
    """
    Get detailed disease information in multilingual structured format
    
    Args:
        disease_name: The disease name
        
    Returns:
        Disease information in structured multilingual format
    """
    try:
        
        # Check for special cases
        if is_no_leaf_found(disease_name):
            return NO_LEAF_RESPONSE
        
        if is_healthy_disease(disease_name):
            return HEALTHY_RESPONSE
         
        # Extract crop name from disease_name (e.g., "Apple Scab (Apple)" -> "Apple")
        crop_name = disease_name.split('(')[-1].rstrip(')')
        
        # Create detailed prompt for structured response
        prompt = f"""Provide detailed information about "{disease_name}" affecting {crop_name} crops in the following JSON format:

{{
    "english": {{
        "symptoms": [
            {{
                "title": "Symptom Title",
                "description": "Detailed description of the symptom"
            }},
            {{
                "title": "Symptom Title 2",
                "description": "Detailed description of the symptom"
            }},
            {{
                "title": "Symptom Title 3",
                "description": "Detailed description of the symptom"
            }}
        ],
        "treatment": {{
            "spray_name": "Recommended chemical spray name",
            "dosage": "Dosage in ml/L format",
            "frequency": "Number of times to spray"
        }}
    }},
    "hindi": {{
        "symptoms": [
            {{
                "title": "लक्षण का शीर्षक",
                "description": "लक्षण का विस्तृत विवरण"
            }},
            {{
                "title": "लक्षण का शीर्षक 2",
                "description": "लक्षण का विस्तृत विवरण"
            }},
            {{
                "title": "लक्षण का शीर्षक 3",
                "description": "लक्षण का विस्तृत विवरण"
            }}
        ],
        "treatment": {{
            "spray_name": "अनुशंसित रासायनिक स्प्रे का नाम",
            "dosage": "ml/L प्रारूप में खुराक",
            "frequency": "स्प्रे करने की संख्या"
        }}
    }},
    "telugu": {{
        "symptoms": [
            {{
                "title": "లక్షణం యొక్క శీర్షిక",
                "description": "లక్షణం యొక్క వివరణ"
            }},
            {{
                "title": "లక్షణం యొక్క శీర్షిక 2",
                "description": "లక్షణం యొక్క వివరణ"
            }},
            {{
                "title": "లక్షణం యొక్క శీర్షిక 3",
                "description": "లక్షణం యొక్క వివరణ"
            }}
        ],
        "treatment": {{
            "spray_name": "సిఫారిస్ చేయబడిన రసాయన స్ప్రే పేరు",
            "dosage": "ml/L ఫార్మాట్‌లో మోతాదు",
            "frequency": "స్ప్రే చేసే సంఖ్య"
        }}
    }},
    "tamil": {{
        "symptoms": [
            {{
                "title": "அறிகுறி என்ற தலைப்பு",
                "description": "அறிகுறியின் விரிவான விளக்கம்"
            }},
            {{
                "title": "அறிகுறி என்ற தலைப்பு 2",
                "description": "அறிகுறியின் விரிவான விளக்கம்"
            }},
            {{
                "title": "அறிகுறி என்ற தலைப்பு 3",
                "description": "அறிகுறியின் விரிவான விளக்கம்"
            }}
        ],
        "treatment": {{
            "spray_name": "பரிந்துரைக்கப்பட்ட இரசாயன தெளிப்பு பெயர்",
            "dosage": "ml/L வடிவத்தில் அளவு",
            "frequency": "தெளிப்பதற்கான முறை"
        }}
    }},
    "punjabi": {{
        "symptoms": [
            {{
                "title": "ਲੱਛਣ ਦਾ ਸਿਰਲੇਖ",
                "description": "ਲੱਛਣ ਦਾ ਵਿਸਥਾਰ ਵਰਣਨ"
            }},
            {{
                "title": "ਲੱਛਣ ਦਾ ਸਿਰਲੇਖ 2",
                "description": "ਲੱਛਣ ਦਾ ਵਿਸਥਾਰ ਵਰਣਨ"
            }},
            {{
                "title": "ਲੱਛਣ ਦਾ ਸਿਰਲੇਖ 3",
                "description": "ਲੱਛਣ ਦਾ ਵਿਸਥਾਰ ਵਰਣਨ"
            }}
        ],
        "treatment": {{
            "spray_name": "ਸਿਫਾਰਿਸ਼ ਕੀਤਾ ਹੋਇਆ ਰਸਾਇਣਕ ਸਪ੍ਰੇ ਨਾਮ",
            "dosage": "ml/L ਫਾਰਮੈਟ ਵਿੱਚ ਖੁਰਾਕ",
            "frequency": "ਸਪ੍ਰੇ ਕਰਨ ਦੀ ਗਿਣਤੀ"
        }}
    }}
}}

Make sure:
1. Provide exactly 3 symptoms for each language
2. Symptoms should be realistic and specific to {disease_name}
3. Treatment spray names should be real agricultural chemicals
4. Dosage should be in ml/L format
5. Frequency should be a number (e.g., "2", "3")
6. Return ONLY valid JSON, no markdown wrapping
"""
        
        # Get response from AI
        ai_response = get_ai_response(prompt)
        
        # Check for errors
        if "Error:" in ai_response:
            return {"error": ai_response}
        
        # Parse response to JSON
        parsed_response = parse_ai_response_to_json(ai_response)
        
        # Validate response structure
        if "error" in parsed_response:
            return parsed_response
        
        # Validate that all required languages are present
        required_languages = ["english", "hindi", "telugu", "tamil", "punjabi"]
        for lang in required_languages:
            if lang not in parsed_response:
                return {"error": f"Missing language: {lang}"}
            if "symptoms" not in parsed_response[lang] or "treatment" not in parsed_response[lang]:
                return {"error": f"Invalid structure for {lang}"}
        
        return parsed_response
        
    except Exception as e:
        return {"error": f"Error processing disease information: {str(e)}"}



# Example usage
if __name__ == "__main__":
    # Single disease
    result = get_disease_info("Cedar Apple Rust (Apple)")  # Apple Scab
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Healthy plant
    result_healthy = get_disease_info("Healthy (Blueberry)")  # Healthy (Apple)
    print("\n" + "="*50)
    print(json.dumps(result_healthy, indent=2, ensure_ascii=False))
    
    # No leaf found
    result_no_leaf = get_disease_info("No Leaf Found")  # No Leaf Found
    print("\n" + "="*50)
    print(json.dumps(result_no_leaf, indent=2, ensure_ascii=False))