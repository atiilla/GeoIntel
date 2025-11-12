from typing import Any, Dict, Optional

from .api_client import GeminiClient
from .exceptions import GeoIntelError
from .image_processor import ImageProcessor
from .logger import logger
from .prompts import get_geolocation_prompt
from .response_parser import ResponseParser


class GeoIntel:
    def __init__(self, api_key: Optional[str] = None):
       
        self.api_client = GeminiClient(api_key)
        self.image_processor = ImageProcessor()
        self.response_parser = ResponseParser()
        logger.info("GeoIntel initialized successfully")

    def locate(
        self,
        image_path: str,
        context_info: Optional[str] = None,
        location_guess: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Starting location analysis for: {image_path}")

            # Process image
            image_base64 = self.image_processor.process_image(image_path)

            # Generate prompt
            prompt = get_geolocation_prompt(context_info, location_guess)

            # Call API
            raw_response = self.api_client.generate_content(
                prompt=prompt,
                image_base64=image_base64
            )

            # Parse response
            result = self.response_parser.parse_response(raw_response)
            logger.info("Location analysis completed successfully")

            return result

        except GeoIntelError as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            return {
                "error": str(e),
                "details": type(e).__name__
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "error": "An unexpected error occurred",
                "details": str(e)
            }

    def locate_with_gemini(
        self,
        image_path: str,
        context_info: Optional[str] = None,
        location_guess: Optional[str] = None
    ) -> Dict[str, Any]:
        return self.locate(image_path, context_info, location_guess)