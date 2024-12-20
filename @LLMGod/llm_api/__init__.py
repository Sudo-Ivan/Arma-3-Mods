import requests
import logging
import os
from datetime import datetime
import threading
from queue import Queue
import time
import re

# Setup logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'debug_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('llm_api')

# Global response queue for async operations
response_queue = {}

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

def _async_request(system_prompt, user_prompt, provider, request_id):
    """Background worker for API requests"""
    try:
        response = requests.post(
            "http://100.104.232.123:8020/chat",
            json={
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "provider": provider,
                "temperature": 0.7
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

def prompt(system_prompt="You are a helpful AI assistant.", user_prompt="Hello", provider="ollama", request_id=None):
    """
    Sends a prompt to Middleman API
    To execute this function, call:
    First request:
    ["llm_api.prompt", ["You are an Arma 3 AI Commander", "Create a patrol route", "ollama", "unique_id_1"]] call py3_fnc_callExtension
    
    Check status:
    ["llm_api.prompt", ["You are an Arma 3 AI Commander", "", "ollama", "unique_id_1"]] call py3_fnc_callExtension
    """
    if not request_id:
        return "Error: request_id is required"

    # If this is a status check (empty user_prompt)
    if not user_prompt and request_id in response_queue:
        status, response = response_queue[request_id]
        if status == "success":
            del response_queue[request_id]  # Cleanup
        return response

    # If this is a new request
    if user_prompt and request_id not in response_queue:
        logger.debug(f"Starting new prompt request {request_id}")
        response_queue[request_id] = ("pending", "Request is being processed...")
        thread = threading.Thread(
            target=_async_request,
            args=(system_prompt, user_prompt, provider, request_id)
        )
        thread.daemon = True
        thread.start()
        return "Request started. Check status with empty user_prompt and same request_id."

    # If request is still pending
    return "Request is still being processed..."

def hello():
    """
    Returns the classic "Hello world!"
    To execute this function, call:
    ["basic.hello", []] call py3_fnc_callExtension
    """
    logger.debug("hello() called")
    return 'Hello world!'


def ping(*args):
    """
    Returns all the arguments passed to the function
    To execute this function, call:
    ["basic.ping", ["string", 1, 2.3, true]] call py3_fnc_callExtension
    """
    logger.debug(f"ping() called with args: {args}")
    return args
