from typing import Dict, Any, Optional
from . import image_utils
from . import prompt_builder
from . import api_client
from . import response_parser
from . import config


class GeoIntel:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the GeoIntel geolocation analyzer.
        
        Args:
            api_key: Optional API key. If not provided, will try to get from GEMINI_API_KEY environment variable.
        """
        resolved_api_key = config.get_api_key(api_key)
        self.api_client = api_client.GeminiAPIClient(resolved_api_key)
        
    def locate_with_gemini(self, 
                          image_path: str, 
                          context_info: Optional[str] = None, 
                          location_guess: Optional[str] = None) -> Dict[str, Any]:
        """
        Use Gemini API to analyze and geolocate an image with higher accuracy.
        
        Args:
            image_path: Path to the image file or URL
            context_info: Optional additional context about the image
            location_guess: Optional user's guess of the location
            
        Returns:
            Dictionary containing the analysis and location information with structure:
            {
                "interpretation": str,  # Analysis of the image
                "locations": [          # List of possible locations
                    {
                        "country": str,
                        "state": str,
                        "city": str,
                        "confidence": "High"/"Medium"/"Low",
                        "coordinates": {
                            "latitude": float,
                            "longitude": float
                        },
                        "explanation": str
                    }
                ]
            }
            
            On error, returns:
            {
                "error": str,           # Error message
                "details": str,         # Optional details about the error
                "exception": str        # Optional exception information
            }
        """
        # Convert image to base64 and get MIME type
        try:
            image_base64, mime_type = image_utils.encode_image_to_base64(image_path)
        except Exception as e:
            return {
                "error": f"Failed to process image: {str(e)}",
                "details": str(e),
                "exception": type(e).__name__
            }
        
        # Build the prompt
        prompt_text = prompt_builder.build_geolocation_prompt(context_info, location_guess)
        
        # Send request to API
        try:
            api_response = self.api_client.send_request(prompt_text, image_base64, mime_type)
        except Exception as e:
            return {
                "error": "Failed to communicate with Gemini API",
                "details": str(e),
                "exception": type(e).__name__
            }
        
        # Parse the response
        try:
            parsed_result = response_parser.parse_geolocation_response(api_response)
            return parsed_result
        except Exception as e:
            return {
                "error": "Failed to parse API response",
                "details": str(e),
                "exception": type(e).__name__
            }
            
    def locate(self, image_path: str, context_info: Optional[str] = None, 
              location_guess: Optional[str] = None) -> Dict[str, Any]:
        """
        Locate an image using Gemini API.
        
        Args:
            image_path: Path to the image file or URL
            context_info: Optional additional context about the image
            location_guess: Optional user's guess of the location
            
        Returns:
            Dictionary containing the analysis and location information.
            See locate_with_gemini method for detailed return structure.
            
        Note:
            This is an alias for locate_with_gemini for backward compatibility.
        """
        return self.locate_with_gemini(image_path, context_info, location_guess)