import os

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


def get_api_key(api_key: str = None) -> str:
    """
    Get the API key from the provided parameter or environment variable.
    
    Args:
        api_key: Optional API key to use. If provided, this is returned.
        
    Returns:
        The API key from the parameter, environment variable, or default fallback.
    """
    if api_key:
        return api_key
    return os.environ.get(DEFAULT_API_KEY_ENV_VAR, "your_api_key_here")
