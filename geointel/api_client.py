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
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.6",
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Brave\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "sec-gpc": "1",
            "Referer": "https://googleapis.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        # Make the API request
        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=request_body,
                timeout=20
            )
        except requests.Timeout:
            raise ValueError("API request timed out. Please try again later or check your internet connection.")
        
        if response.status_code != 200:
            raise ValueError(f"API request failed with status code {response.status_code}: {response.text}")
        
        return response.json()
