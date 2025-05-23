import requests
import json
from typing import Dict, Any, Tuple

# Gemini API Key & Endpoint
API_KEY = "****MASKED****"  # Replace with a real secure key
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def analyze_mobile_lifespan(mobile_data: Dict[str, Any]) -> Tuple[int, Dict[str, Any], str]:
    """
    Analyze the lifespan and future-proofing of a mobile device using Gemini API.
    
    Args:
        mobile_data (dict): Dictionary containing mobile device details
        
    Returns:
        tuple: (score, breakdown, overall_verdict)
            - score (int): Overall score out of 100
            - breakdown (dict): Detailed scores for each category
            - overall_verdict (str): Textual summary of the analysis
    """
    # Extract relevant mobile details
    model = mobile_data.get('MODEL', '')
    brand = mobile_data.get('BRAND', '')
    processor = mobile_data.get('PROCESSOR', '')
    ram = mobile_data.get('RAM', '')
    storage = mobile_data.get('STORAGE', '')
    battery = mobile_data.get('BATTERY', '')
    display = mobile_data.get('DISPLAY', '')
    os = mobile_data.get('OS', '')
    release_date = mobile_data.get('RELEASEDATE', '')
    
    # Prepare the prompt for Gemini
    prompt = f"""
    Analyze the following mobile device and provide a future-proofing score (0-100) and detailed breakdown.
    
    Device Information:
    - Brand: {brand}
    - Model: {model}
    - Processor: {processor}
    - RAM: {ram}
    - Storage: {storage}
    - Battery: {battery}
    - Display: {display}
    - OS: {os}
    - Release Date: {release_date}
    
    Please analyze based on these categories (with weightage in parentheses):
    1. OS Support Lifespan (25%): How long the device will receive OS updates
    2. Processor Performance (20%): CPU/GPU performance and future compatibility
    3. Battery Health (15%): Battery capacity and longevity
    4. Connectivity (15%): 5G, Wi-Fi 6, Bluetooth versions, etc.
    5. Storage & RAM (10%): Future-proof storage and memory
    6. Build Quality (10%): Durability and repairability
    7. AI Hardware Support (5%): Dedicated AI/ML hardware
    
    Return the response in this exact JSON format:
    {{
        "score": 0-100,
        "overall_verdict": "Brief summary (1-2 sentences)",
        "breakdown": {{
            "os_support": {{"score": 0-25, "reasoning": "..."}},
            "processor": {{"score": 0-20, "reasoning": "..."}},
            "battery": {{"score": 0-15, "reasoning": "..."}},
            "connectivity": {{"score": 0-15, "reasoning": "..."}},
            "storage_ram": {{"score": 0-10, "reasoning": "..."}},
            "build_quality": {{"score": 0-10, "reasoning": "..."}},
            "ai_hardware": {{"score": 0-5, "reasoning": "..."}}
        }}
    }}
    """
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=data)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        content = result.get('candidates', [{}])[0].get('content', {})
        text_response = content.get('parts', [{}])[0].get('text', '{}')
        
        # Clean and parse the JSON response
        try:
            # Try to find JSON in the response
            json_start = text_response.find('{')
            json_end = text_response.rfind('}') + 1
            json_str = text_response[json_start:json_end]
            
            analysis = json.loads(json_str)
            score = analysis.get('score', 0)
            breakdown = analysis.get('breakdown', {})
            overall_verdict = analysis.get('overall_verdict', 'No verdict available')
            
            return score, breakdown, overall_verdict
            
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Raw response: {text_response}")
            return get_fallback_response()
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return get_fallback_response()

def get_fallback_response():
    """Return a fallback response if API call fails"""
    return 75, {
        "os_support": {"score": 18, "reasoning": "Average OS support expected"},
        "processor": {"score": 15, "reasoning": "Competent processor for near future"},
        "battery": {"score": 12, "reasoning": "Standard battery performance"},
        "connectivity": {"score": 10, "reasoning": "Good connectivity options"},
        "storage_ram": {"score": 8, "reasoning": "Adequate storage and RAM"},
        "build_quality": {"score": 7, "reasoning": "Standard build quality"},
        "ai_hardware": {"score": 5, "reasoning": "Basic AI capabilities"}
    }, "This device should perform well for the next 2-3 years with average usage."