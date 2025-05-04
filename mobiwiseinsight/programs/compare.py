import google.generativeai as genai
import requests
import json
from decimal import Decimal

API_KEY = "****MASKED****"  # Replace with your real key
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def convert_decimal_to_float(data):
    """ Recursively convert all Decimal values to float in a dictionary or list """
    if isinstance(data, list):
        return [convert_decimal_to_float(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_decimal_to_float(value) for key, value in data.items()}
    elif isinstance(data, Decimal):  # Convert Decimal to float
        return float(data)
    return data 

def compare_and_recommend(mobiles_list, preferences):
    """
    Uses OpenAI GPT-4 to compare mobile specifications and recommend the best mobile.
    """
    mobiles_list = convert_decimal_to_float(mobiles_list)

    prompt = f"""
    You are an AI mobile comparison expert. The user has selected the following mobiles for comparison:

    {json.dumps(mobiles_list, indent=4)}

    The user preferences are: {preferences}

    Based on real-time mobile market trends, analyze and compare the mobiles in these categories:
    - Price (Lower is better)
    - RAM (Higher is better)
    - Storage (Higher is better)
    - Battery Capacity (Higher is better)
    - Display Quality (AMOLED > OLED > LCD > TFT)
    - Processor Performance (Ranked by real-world benchmarks)
    - Front Camera (Higher MP is better)
    - Rear Camera (Count lenses first, then compare MP)
    - User Rating (Higher rating is better)

    **Tasks to Perform:**
    1️⃣ Provide a detailed **comparison table** with the best model for each category.
    2️⃣ Recommend the **best mobile overall** based on user preferences.

    Provide a JSON response in this format:
    {{
        "comparisons": [
            {{
                "feature": "Feature Name",
                "best_model": "Model Name",
                "best_value": "Best Value"
            }},
            ...
        ],
        "best_suggestion": {{
            "model": "Best Mobile Model Name",
            "brand": "Brand Name",
            "price": "₹ Best Price",
            "reason": "Explain why this mobile is best based on user preferences."
        }}
    }}
    """
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print("Gemini API Error:", response.status_code, response.text)
            return "Could not get AI recommendation."

    except Exception as e:
        print(f"Error in AI Comparison & Recommendation: {e}")
        return {
            "comparisons": [],
            "best_suggestion": {
                "model": "N/A",
                "brand": "N/A",
                "price": "N/A",
                "reason": "AI analysis failed. Try again later."
            }
        }