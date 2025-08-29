import json
import requests
import base64
import os
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urlparse

class GeoIntel:
    def __init__(self, api_key: Optional[str] = None):
        self.gemini_api_key = api_key or os.environ.get("GEMINI_API_KEY", "your_api_key_here")
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-lite-001:generateContent"
        
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Convert an image file to base64 encoding.
        Supports both local files and URLs.
        
        Args:
            image_path: Path to the image file or URL
            
        Returns:
            Base64 encoded string of the image
            
        Raises:
            ValueError: If the image cannot be loaded or the URL is invalid
            FileNotFoundError: If the local image file doesn't exist
        """
        # Check if the image_path is a URL
        parsed_url = urlparse(image_path)
        if parsed_url.scheme in ('http', 'https'):
            try:
                response = requests.get(image_path, timeout=10)
                response.raise_for_status()  # Raise an exception for HTTP errors
                return base64.b64encode(response.content).decode('utf-8')
            except requests.exceptions.ConnectionError:
                raise ValueError(f"Failed to connect to URL: {image_path}. Please check your internet connection.")
            except requests.exceptions.HTTPError as e:
                raise ValueError(f"HTTP error when downloading image: {e}")
            except requests.exceptions.Timeout:
                raise ValueError(f"Request timed out when downloading image from URL: {image_path}")
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Failed to download image from URL: {e}")
        else:
            # Assume it's a local file path
            try:
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            except FileNotFoundError:
                raise FileNotFoundError(f"Image file not found: {image_path}")
            except PermissionError:
                raise ValueError(f"Permission denied when accessing image file: {image_path}")
            except Exception as e:
                raise ValueError(f"Failed to read image file: {str(e)}")
    
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
        # Convert image to base64
        try:
            image_base64 = self.encode_image_to_base64(image_path)
        except Exception as e:
            return {"error": f"Failed to process image: {str(e)}"}
        
        # Build the prompt
        prompt_text = """You are a professional geolocation expert. You MUST respond with a valid JSON object in the following format:

{
  "interpretation": "A comprehensive analysis of the image, including:
    - Architectural style and period
    - Notable landmarks or distinctive features
    - Natural environment and climate indicators
    - Cultural elements (signage, vehicles, clothing, etc.)
    - Any visible text or language
    - Time period indicators (if any)",
  "locations": [
    {
      "country": "Primary country name",
      "state": "State/region/province name",
      "city": "City name",
      "confidence": "High/Medium/Low",
      "coordinates": {
        "latitude": 12.3456,
        "longitude": 78.9012
      },
      "explanation": "Detailed reasoning for this location identification, including:
        - Specific architectural features that match this location
        - Environmental characteristics that support this location
        - Cultural elements that indicate this region
        - Any distinctive landmarks or features
        - Supporting evidence from visible text or signage"
    }
  ]
}

IMPORTANT: 
1. Your response MUST be a valid JSON object. Do not include any text before or after the JSON object.
2. Do not include any markdown formatting or code blocks.
3. The response should be parseable by JSON.parse().
4. You can provide up to three possible locations if you are not completely confident about a single location.
5. Order the locations by confidence level (highest to lowest).
6. ALWAYS include approximate coordinates (latitude and longitude) for each location when possible.

Consider these key aspects for accurate location identification:
1. Architectural Analysis:
   - Building styles and materials
   - Roof types and construction methods
   - Window and door designs
   - Decorative elements and ornamentation

2. Environmental Indicators:
   - Vegetation types and patterns
   - Climate indicators (snow, desert, tropical, etc.)
   - Terrain and topography
   - Water bodies or coastal features

3. Cultural Context:
   - Language of visible text
   - Vehicle types and styles
   - Clothing and fashion
   - Street furniture and infrastructure
   - Commercial signage and branding

4. Time Period Indicators:
   - Architectural period
   - Vehicle models
   - Fashion styles
   - Technology visible"""

        # Add additional context if provided
        if context_info:
            prompt_text += f"\n\nAdditional context provided by the user:\n{context_info}"
        
        # Add location guess if provided
        if location_guess:
            prompt_text += f"\n\nUser suggests this might be in: {location_guess}"
        
        prompt_text += "\n\nRemember: Your response must be a valid JSON object only. No additional text or formatting."
        
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
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 2048
            }
        }
        
        # Make the API request
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
        
        try:
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                headers=headers,
                json=request_body
            )
            
            if response.status_code != 200:
                print(f"Error: API request failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                return {"error": "Failed to get response from Gemini API", "details": response.text}
            
            data = response.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Strip any markdown formatting and code blocks
            json_string = raw_text.replace("```json", "").replace("```", "").strip()
            
            try:
                parsed_result = json.loads(json_string)
                
                # Handle potential single location format where the location is not in an array
                if "city" in parsed_result and "locations" not in parsed_result:
                    return {
                        "interpretation": parsed_result.get("interpretation", ""),
                        "locations": [{
                            "country": parsed_result.get("country", ""),
                            "state": parsed_result.get("state", ""),
                            "city": parsed_result.get("city", ""),
                            "confidence": parsed_result.get("confidence", "Medium"),
                            "coordinates": parsed_result.get("coordinates", {"latitude": 0, "longitude": 0}),
                            "explanation": parsed_result.get("explanation", "")
                        }]
                    }
                
                return parsed_result
                
            except json.JSONDecodeError as e:
                return {
                    "error": "Failed to parse API response",
                    "rawResponse": raw_text,
                    "exception": str(e)
                }
        except Exception as e:
            return {
                "error": "Failed to communicate with Gemini API",
                "exception": str(e)
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