"""
GeoIntel - AI-powered geolocation analysis using Gemini API.

This module provides functionality to analyze images and identify their likely
geographic locations using Google's Gemini AI model.
"""

import json
import logging
import mimetypes
import os
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urlparse

import requests

from .config import (
    GEMINI_API_URL,
    DEFAULT_API_KEY_ENV,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_TOP_P,
    DEFAULT_MAX_OUTPUT_TOKENS,
    REQUEST_TIMEOUT,
    IMAGE_DOWNLOAD_TIMEOUT,
    MIME_TYPES,
    DEFAULT_MIME_TYPE,
    API_HEADERS,
    VALID_CONFIDENCE_LEVELS,
    CONFIDENCE_MEDIUM,
)
from .prompts import build_prompt
from .exceptions import GeoIntelError, APIError, ImageProcessingError
from .utils import sanitize_api_key


# Set up logging
logger = logging.getLogger(__name__)


class GeoIntel:
    """
    GeoIntel client for analyzing images and identifying geographic locations.
    
    This class provides an interface to Google's Gemini AI model for
    geolocation analysis of images.
    
    Attributes:
        gemini_api_key (str): API key for Gemini service
        gemini_api_url (str): URL endpoint for Gemini API
        
    Example:
        >>> geointel = GeoIntel(api_key="your_api_key")
        >>> results = geointel.locate("path/to/image.jpg")
        >>> print(results["locations"][0]["city"])
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize GeoIntel client.
        
        Args:
            api_key: Gemini API key. If not provided, will look for
                    GEMINI_API_KEY environment variable.
                    
        Raises:
            ValueError: If no API key is provided or found in environment
        """
        self.gemini_api_key = api_key or os.environ.get(DEFAULT_API_KEY_ENV)
        
        if not self.gemini_api_key or self.gemini_api_key == "your_api_key_here":
            raise ValueError(
                f"API key not provided. Please set {DEFAULT_API_KEY_ENV} "
                "environment variable or pass api_key parameter."
            )
            
        self.gemini_api_url = GEMINI_API_URL
        logger.info(f"GeoIntel client initialized (API key: {sanitize_api_key(self.gemini_api_key)})")
        
    def _detect_mime_type(self, image_path: str) -> str:
        """
        Detect MIME type of an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            MIME type string (e.g., 'image/jpeg')
        """
        # Try to get extension from path
        ext = Path(image_path).suffix.lower()
        mime_type = MIME_TYPES.get(ext, DEFAULT_MIME_TYPE)
        
        # Fall back to mimetypes module if not in our map
        if mime_type == DEFAULT_MIME_TYPE and ext not in MIME_TYPES:
            guessed_type = mimetypes.guess_type(image_path)[0]
            if guessed_type and guessed_type.startswith('image/'):
                mime_type = guessed_type
        
        logger.debug(f"Detected MIME type '{mime_type}' for {image_path}")
        return mime_type
    
    def encode_image_to_base64(self, image_path: str) -> Tuple[str, str]:
        """
        Convert an image file to base64 encoding.
        Supports both local files and URLs.
        
        Args:
            image_path: Path to the image file or URL
            
        Returns:
            Tuple of (base64_encoded_string, mime_type)
            
        Raises:
            ImageProcessingError: If the image cannot be loaded
            FileNotFoundError: If the local image file doesn't exist
        """
        logger.info(f"Encoding image: {image_path}")
        
        # Check if the image_path is a URL
        parsed_url = urlparse(image_path)
        if parsed_url.scheme in ('http', 'https'):
            try:
                response = requests.get(image_path, timeout=IMAGE_DOWNLOAD_TIMEOUT)
                response.raise_for_status()
                
                # Detect MIME type from Content-Type header or URL
                mime_type = response.headers.get('Content-Type', '').split(';')[0]
                if not mime_type or not mime_type.startswith('image/'):
                    mime_type = self._detect_mime_type(image_path)
                
                encoded = base64.b64encode(response.content).decode('utf-8')
                logger.debug(f"Successfully encoded image from URL ({len(encoded)} chars)")
                return encoded, mime_type
                
            except requests.exceptions.ConnectionError as e:
                raise ImageProcessingError(
                    f"Failed to connect to URL: {image_path}. "
                    "Please check your internet connection."
                ) from e
            except requests.exceptions.HTTPError as e:
                raise ImageProcessingError(
                    f"HTTP error when downloading image: {e}"
                ) from e
            except requests.exceptions.Timeout as e:
                raise ImageProcessingError(
                    f"Request timed out when downloading image from URL: {image_path}"
                ) from e
            except requests.exceptions.RequestException as e:
                raise ImageProcessingError(
                    f"Failed to download image from URL: {e}"
                ) from e
        else:
            # Assume it's a local file path
            try:
                with open(image_path, "rb") as image_file:
                    content = image_file.read()
                    encoded = base64.b64encode(content).decode('utf-8')
                    mime_type = self._detect_mime_type(image_path)
                    
                logger.debug(f"Successfully encoded local image ({len(encoded)} chars)")
                return encoded, mime_type
                
            except FileNotFoundError as e:
                raise FileNotFoundError(
                    f"Image file not found: {image_path}"
                ) from e
            except PermissionError as e:
                raise ImageProcessingError(
                    f"Permission denied when accessing image file: {image_path}"
                ) from e
            except Exception as e:
                raise ImageProcessingError(
                    f"Failed to read image file: {str(e)}"
                ) from e
    
    def _validate_location_data(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize location data.
        
        Args:
            location: Raw location data from API
            
        Returns:
            Validated and normalized location data
        """
        validated = {
            "country": location.get("country", "Unknown"),
            "state": location.get("state", ""),
            "city": location.get("city", "Unknown"),
            "confidence": location.get("confidence", CONFIDENCE_MEDIUM),
            "coordinates": location.get("coordinates", {"latitude": 0, "longitude": 0}),
            "explanation": location.get("explanation", "")
        }
        
        # Validate confidence level
        if validated["confidence"] not in VALID_CONFIDENCE_LEVELS:
            logger.warning(
                f"Invalid confidence level '{validated['confidence']}', "
                f"defaulting to {CONFIDENCE_MEDIUM}"
            )
            validated["confidence"] = CONFIDENCE_MEDIUM
        
        return validated
    
    def _parse_api_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and validate API response.
        
        Args:
            response_data: Raw API response
            
        Returns:
            Parsed location data
            
        Raises:
            APIError: If response cannot be parsed
        """
        try:
            raw_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise APIError(
                f"Unexpected API response structure: {e}"
            ) from e
        
        # Strip any markdown formatting and code blocks
        json_string = raw_text.replace("```json", "").replace("```", "").strip()
        
        try:
            parsed_result = json.loads(json_string)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {raw_text[:200]}...")
            raise APIError(
                f"Failed to parse API response as JSON: {e}"
            ) from e
        
        # Handle potential single location format where the location is not in an array
        if "city" in parsed_result and "locations" not in parsed_result:
            parsed_result = {
                "interpretation": parsed_result.get("interpretation", ""),
                "locations": [self._validate_location_data(parsed_result)]
            }
        else:
            # Validate each location
            if "locations" in parsed_result:
                parsed_result["locations"] = [
                    self._validate_location_data(loc)
                    for loc in parsed_result.get("locations", [])
                ]
        
        return parsed_result
    
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
        logger.info(f"Starting geolocation analysis for: {image_path}")
        
        # Convert image to base64
        try:
            image_base64, mime_type = self.encode_image_to_base64(image_path)
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {"error": f"Failed to process image: {str(e)}"}
        
        # Build the prompt
        prompt_text = build_prompt(context_info, location_guess)
        
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
            "generationConfig": {
                "temperature": DEFAULT_TEMPERATURE,
                "topK": DEFAULT_TOP_K,
                "topP": DEFAULT_TOP_P,
                "maxOutputTokens": DEFAULT_MAX_OUTPUT_TOKENS
            }
        }
        
        # Make the API request
        logger.debug("Sending request to Gemini API")
        try:
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                headers=API_HEADERS,
                json=request_body,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                error_msg = f"API request failed with status code {response.status_code}"
                logger.error(f"{error_msg}: {response.text}")
                return {
                    "error": "Failed to get response from Gemini API",
                    "details": response.text,
                    "status_code": response.status_code
                }
            
            data = response.json()
            logger.debug("Successfully received API response")
            
            # Parse and validate the response
            try:
                result = self._parse_api_response(data)
                logger.info(
                    f"Analysis complete. Found {len(result.get('locations', []))} location(s)"
                )
                return result
            except APIError as e:
                logger.error(f"Failed to parse API response: {e}")
                return {
                    "error": "Failed to parse API response",
                    "exception": str(e)
                }
                
        except requests.exceptions.Timeout as e:
            logger.error(f"API request timed out: {e}")
            return {
                "error": "Request to Gemini API timed out",
                "exception": str(e)
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                "error": "Failed to communicate with Gemini API",
                "exception": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error during API communication: {e}")
            return {
                "error": "An unexpected error occurred",
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