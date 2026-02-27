import requests
import json
from typing import Dict, Any, Optional
from . import config


class GeminiAPIClient:
    """Client for communicating with the Gemini API."""
    
    def __init__(self, api_key: str, api_url: Optional[str] = None):
        """
        Initialize the Gemini API client.
        
        Args:
            api_key: The API key for authentication
            api_url: Optional custom API URL. Defaults to the standard Gemini endpoint.
        """
        self.api_key = api_key
        self.api_url = api_url or config.DEFAULT_API_URL
    
    def send_request(self, prompt_text: str, image_base64: str, mime_type: str = None) -> Dict[str, Any]:
        """
        Send a request to the Gemini API with the provided prompt and image.
        
        Args:
            prompt_text: The prompt text to send to the API
            image_base64: The base64 encoded image data
            mime_type: The MIME type of the image (defaults to DEFAULT_MIME_TYPE if not provided)
            
        Returns:
            The JSON response from the API
            
        Raises:
            ValueError: If the API request fails or returns an error status
            requests.RequestException: If there's a network or connection error
        """
        # Use provided MIME type or fall back to default
        if mime_type is None:
            mime_type = config.DEFAULT_MIME_TYPE
        
        # Prepare the request body
        request_body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt_text
                        },
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_base64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": config.DEFAULT_GENERATION_CONFIG
        }
        
        # Set request headers
        headers = {
            "Content-Type": "application/json",
        }
        
        # Make the API request
        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=request_body,
                timeout=60
            )
        except requests.Timeout:
            raise ValueError("API request timed out. Please try again later or check your internet connection.")
        
        if response.status_code != 200:
            try:
                error_body = response.json()
                error_msg = error_body.get("error", {}).get("message", response.text)
            except Exception:
                error_msg = response.text
            raise ValueError(f"API request failed with status code {response.status_code}: {error_msg}")
        
        return response.json()
