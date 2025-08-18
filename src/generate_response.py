from src.config import GEMINI_API_KEY
from typing import List
import base64
import requests
from src.log import logger

def generate_gemini_response(prompt: str, images_data: List[bytes]) -> str:
    """
    Sends a multimodal prompt to the Gemini API and returns the response.
    """
    if GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        return "ERROR: Please add your Gemini API key to the script to use this feature."

    headers = {
        "Content-Type": "application/json"
    }

    parts = [{"text": prompt}]
    for img_data in images_data:
        parts.append({
            "inlineData": {
                "mimeType": "image/jpeg",  # Use a common image type
                "data": base64.b64encode(img_data).decode('utf-8')
            }
        })

    payload = {
        "contents": [{"parts": parts}]
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Could not get a response from the API. Please check your API key and try again."
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return f"API request failed: {e}"
