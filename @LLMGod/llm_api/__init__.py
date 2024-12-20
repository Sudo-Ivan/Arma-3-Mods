import requests
import logging
import os
from datetime import datetime

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


def fibonacci(n):
    """
    Returns the n-th Fibonacci number
    To execute this function, call:
    ["basic.fibonacci", [30]] call py3_fnc_callExtension

    Yes, if you pass a "large" number, like 100 in the input, Arma will hang.
    To use functions that take time to compute, spawn a separate thread and
    poll that thread for completion.
    """
    logger.debug(f"fibonacci() called with n: {n}")
    if n < 2:
        return n
    return fibonacci(n - 2) + fibonacci(n - 1)


def prompt(system_prompt="You are a helpful AI assistant.", user_prompt="Hello"):
    """
    Sends a prompt to Ollama API
    To execute this function, call:
    ["llm_api.prompt", ["You are an Arma 3 AI Commander", "Create a patrol route"]] call py3_fnc_callExtension
    """
    logger.debug(f"prompt() called with system_prompt: {system_prompt}, user_prompt: {user_prompt}")
    try:
        response = requests.post(
            "http://100.94.142.23:11434/api/generate",
            json={
                "model": "llama3.2:latest",
                "system": system_prompt,
                "prompt": user_prompt,
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
