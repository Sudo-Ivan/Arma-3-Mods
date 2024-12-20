import requests
import logging
from datetime import datetime
import os
import threading
from queue import Queue
import time
import re

# Get the same logger as __init__.py
logger = logging.getLogger('llm_api')

# Global response queue for async operations
response_queue = {}

try:
    import requests
except ImportError:
    error_msg = "Error: 'requests' module not installed. Please run './install_requirements64.sh --requirements /path/to/llm_api/requirements.txt'"
    logger.error(error_msg)
    def chat_with_ai(*args, **kwargs):
        return error_msg

def sanitize_for_arma(text):
    """Sanitize text for Arma 3 string handling"""
    if text is None:
        return ""
        
    # First remove markdown formatting
    markdown_patterns = [
        (r'\*\*.*?\*\*', ''),  # Bold
        (r'\*.*?\*', ''),      # Italic
        (r'\_.*?\_', ''),      # Underscore emphasis
        (r'\`.*?\`', ''),      # Code
        (r'\#+ ', ''),         # Headers
        (r'\[.*?\]\(.*?\)', '') # Links
    ]
    
    for pattern, replacement in markdown_patterns:
        text = re.sub(pattern, replacement, text)
    
    # Replace problematic characters
    replacements = {
        '"': '""',
        '\n': '. ',
        '\r': '',
        '[': '',
        ']': '',
        '\\': '', 
        '*': '',       
        '_': '',
        '#': '',
        '|': '',
        '{': '',
        '}': '',
        '`': ''
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    text = ' '.join(text.split())
    
    text = re.sub(r'\.+', '.', text)
    
    text = text[:10000]
    
    return text

def _async_request(prompt, temperature, provider, request_id):
    """Background worker for API requests"""
    try:
        response = requests.post(
            "http://100.104.232.123:8020/chat",
            json={
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "provider": provider
            },
            timeout=30
        )
        
        logger.debug(f"Raw API Response for {request_id}: {response.text[:500]}...")
        
        try:
            result = response.json()
            if 'response' in result:
                response_text = sanitize_for_arma(result['response'])
                logger.debug(f"Sanitized API Response for {request_id}: {response_text[:100]}...")
                response_queue[request_id] = ("success", response_text)
            else:
                error_msg = sanitize_for_arma(f"Unexpected API response structure: {result}")
                logger.error(error_msg)
                response_queue[request_id] = ("error", error_msg)
        except ValueError as json_err:
            error_msg = sanitize_for_arma(f"JSON parsing error: {str(json_err)}")
            logger.error(error_msg)
            response_queue[request_id] = ("error", error_msg)
            
    except requests.Timeout:
        error_msg = sanitize_for_arma("Request timed out after 30 seconds")
        logger.error(error_msg)
        response_queue[request_id] = ("error", error_msg)
    except Exception as e:
        error_msg = sanitize_for_arma(f"Request error: {str(e)}")
        logger.error(error_msg)
        response_queue[request_id] = ("error", error_msg)

def chat_with_ai(prompt, temperature=0.7, provider="ollama", request_id=None):
    """
    Simple chat interface with LLM through middleman API
    To execute this function, call:
    First request:
    ["llm_api.module.chat_with_ai", ["Create a military mission objective", 0.7, "ollama", "unique_id_1"]] call py3_fnc_callExtension
    
    Check status:
    ["llm_api.module.chat_with_ai", ["", 0.7, "ollama", "unique_id_1"]] call py3_fnc_callExtension
    """
    if not request_id:
        return "Error: request_id is required"

    # If this is a status check (empty prompt)
    if not prompt and request_id in response_queue:
        status, response = response_queue[request_id]
        if status == "success":
            del response_queue[request_id]  # Cleanup
        return response

    # If this is a new request
    if prompt and request_id not in response_queue:
        logger.debug(f"Starting new chat request {request_id} with prompt: {prompt}")
        response_queue[request_id] = ("pending", "Request is being processed...")
        thread = threading.Thread(
            target=_async_request,
            args=(prompt, temperature, provider, request_id)
        )
        thread.daemon = True
        thread.start()
        return "Request started. Check status with empty prompt and same request_id."

    # If request is still pending
    return "Request is still being processed..."
