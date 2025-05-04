import requests
import json

# Gemini API Key & Endpoint
API_KEY = "****MASKED****"  # Replace with a real secure key
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Main chatbot interaction function
def get_chatbot_reply(user_input):
    """
    Send a message to Gemini and receive an AI-generated reply.

    Args:
        user_input (str): User's message input.

    Returns:
        str: Gemini's cleaned response or error fallback.
    """
    prompt = f"""
    You are a friendly, helpful chatbot assistant for a mobile insight platform. 
    Answer user queries in a clear and conversational tone.
    
    Example queries include:
    - Recommend a good mobile under ₹30,000 with good battery life.
    - What's the difference between AMOLED and OLED displays?
    - Suggest phones with best camera in mid-range.
    
    User's message:
    {user_input}
    
    Please answer in a helpful, informative manner. Keep your response short and user-friendly.
    """

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            result = response.json()
            result = result['candidates'][0]['content']['parts'][0]['text'].strip()
            return result
        else:
            print("❌ Gemini API Error:", response.status_code, response.text)
            return "Sorry, I couldn't process your message at the moment."

    except Exception as e:
        print(f"❌ Error during Gemini chat request: {e}")
        return "Oops! Something went wrong. Please try again later."
