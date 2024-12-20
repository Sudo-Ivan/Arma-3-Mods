import requests
import logging
from datetime import datetime
import os

# Get the same logger as __init__.py
logger = logging.getLogger('llm_api')

try:
    import requests
except ImportError:
    error_msg = "Error: 'requests' module not installed. Please run './install_requirements64.sh --requirements /path/to/llm_api/requirements.txt'"
    logger.error(error_msg)
    def chat_with_ai(*args, **kwargs):
        return error_msg

def chat_with_ai(prompt, temperature=0.7):
    """
    Simple chat interface with Ollama
    To execute this function, call:
    ["llm_api.module.chat_with_ai", ["Create a military mission objective", 0.7]] call py3_fnc_callExtension
    """
    logger.debug(f"chat_with_ai() called with prompt: {prompt}, temperature: {temperature}")
    try:
        response = requests.post(
            "http://100.94.142.23:11434/api/generate",
            json={
                "model": "llama3.2:latest",
                "prompt": prompt,
                "temperature": temperature,
                "stream": False  # Ensure we get a single response
            }
        )
        
        # Log raw response for debugging
        logger.debug(f"Raw API Response: {response.text[:500]}...")
        
        # Try to parse JSON response
        try:
            result = response.json()
            if 'response' in result:
                response_text = result['response']
                logger.debug(f"API Response: {response_text[:100]}...")
                return response_text
            else:
                error_msg = f"Unexpected API response structure: {result}"
                logger.error(error_msg)
                return error_msg
        except ValueError as json_err:
            error_msg = f"JSON parsing error: {str(json_err)}\nRaw response: {response.text[:200]}"
            logger.error(error_msg)
            return error_msg
            
    except Exception as e:
        error_msg = f"Request error: {str(e)}"
        logger.error(error_msg)
        return error_msg
