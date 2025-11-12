import os
from typing import Any, Dict, Optional

import requests

from .config import (
    API_TIMEOUT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_TOP_P,
    ENV_API_KEY,
    GEMINI_API_BASE_URL,
    GEMINI_MODEL,
    MAX_OUTPUT_TOKENS,
)
from .exceptions import APIError, APIKeyError
from .logger import logger


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get(ENV_API_KEY)
        if not self.api_key or self.api_key == "your_api_key_here":
            raise APIKeyError(
                f"API key required. Set {ENV_API_KEY} environment variable "
                "or pass api_key parameter"
            )

        self.base_url = GEMINI_API_BASE_URL
        self.model = GEMINI_MODEL
        logger.info(f"Initialized Gemini client with model: {self.model}")

    def _build_endpoint_url(self) -> str:
        return f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

    def _build_request_payload(
        self,
        prompt: str,
        image_base64: str,
        mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        return {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
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
                "maxOutputTokens": MAX_OUTPUT_TOKENS
            }
        }

    def _get_request_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json"
        }

    def _extract_response_text(self, response_data: Dict[str, Any]) -> str:
        try:
            # Log the full response structure for debugging
            logger.debug(f"Full API response structure: {response_data}")
            
            # Check if candidates exist
            if "candidates" not in response_data:
                raise APIError("No 'candidates' field in API response")
            
            candidates = response_data["candidates"]
            if not candidates:
                raise APIError("Empty candidates array in API response")
            
            candidate = candidates[0]
            logger.debug(f"First candidate structure: {candidate}")
            
            # Check if content exists
            if "content" not in candidate:
                raise APIError("No 'content' field in candidate")
            
            content = candidate["content"]
            logger.debug(f"Content structure: {content}")
            
            # Handle different content structures
            if "parts" in content:
                # Standard structure with parts array
                parts = content["parts"]
                if not parts:
                    raise APIError("Empty parts array in content")
                
                part = parts[0]
                if "text" not in part:
                    raise APIError("No 'text' field in content part")
                
                return part["text"]
            
            elif "text" in content:
                # Direct text in content (alternative structure)
                return content["text"]
            
            else:
                # Try to find text in any nested structure recursively
                def find_text_recursive(obj, path=""):
                    if isinstance(obj, dict):
                        if "text" in obj:
                            logger.debug(f"Found text at path: {path}.text")
                            return obj["text"]
                        for key, value in obj.items():
                            result = find_text_recursive(value, f"{path}.{key}" if path else key)
                            if result:
                                return result
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            result = find_text_recursive(item, f"{path}[{i}]" if path else f"[{i}]")
                            if result:
                                return result
                    return None
                
                # Search the entire response for text content
                text = find_text_recursive(response_data)
                if text:
                    return text
                
                # If still no text found, check for common alternative fields
                alternative_fields = ["message", "output", "response", "result"]
                for field in alternative_fields:
                    if field in content:
                        logger.debug(f"Trying alternative field: {field}")
                        alt_content = content[field]
                        if isinstance(alt_content, str):
                            return alt_content
                        elif isinstance(alt_content, dict) and "text" in alt_content:
                            return alt_content["text"]
                
                raise APIError(f"Could not find text content in response. Content structure: {content}")
        
        except APIError:
            # Re-raise APIError as-is
            raise
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Invalid response structure: {e}")
            logger.error(f"Full response: {response_data}")
            raise APIError(f"Invalid API response structure: '{e}' - Full response logged for debugging")

    def generate_content(
        self,
        prompt: str,
        image_base64: str,
        mime_type: str = "image/jpeg"
    ) -> str:
        endpoint_url = self._build_endpoint_url()
        headers = self._get_request_headers()
        payload = self._build_request_payload(prompt, image_base64, mime_type)

        try:
            logger.info("Sending request to Gemini API")
            response = requests.post(
                endpoint_url,
                headers=headers,
                json=payload,
                timeout=API_TIMEOUT
            )

            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}"
                logger.error(f"{error_msg}: {response.text}")
                raise APIError(f"{error_msg}: {response.text}")

            # Parse and extract response
            response_data = response.json()
            logger.info("Successfully received API response")
            return self._extract_response_text(response_data)

        except requests.exceptions.Timeout:
            raise APIError("API request timed out")
        except requests.exceptions.RequestException as e:
            raise APIError(f"API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during API call: {e}")
            raise APIError(f"Unexpected error: {e}")
