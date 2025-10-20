import os
from typing import Optional

# Default API configuration
DEFAULT_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-lite-001:generateContent"
DEFAULT_API_KEY_ENV_VAR = "GEMINI_API_KEY"
DEFAULT_MIME_TYPE = "image/jpeg"

# Default generation configuration for Gemini API
DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.4,
    "topK": 32,
    "topP": 1,
    "maxOutputTokens": 2048
}


def get_api_key(api_key: str | None = None) -> str:
    """
    Get the API key from the provided parameter or environment variable.
    
    Args:
        api_key: Optional API key to use. If provided, this is returned.
        
    Returns:
        The API key from the parameter or environment variable.
        
    Raises:
        ValueError: If no API key is provided and the environment variable is not set.
    """
    if api_key:
        return api_key
    env_key = os.environ.get(DEFAULT_API_KEY_ENV_VAR)
    if not env_key:
        raise ValueError(f"Missing API key. Set {DEFAULT_API_KEY_ENV_VAR} environment variable or pass api_key parameter.")
    return env_key
