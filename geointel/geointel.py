from typing import Any, Dict, Optional

from .api_client import GeminiClient
from .exceptions import GeoIntelError
from .image_processor import ImageProcessor
from .logger import logger
from .prompts import get_geolocation_prompt
from .response_parser import ResponseParser


class GeoIntel:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_client = GeminiClient(api_key, model=model)
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

            # Process image — returns (base64_data, mime_type)
            image_base64, mime_type = self.image_processor.process_image(image_path)

            # Generate prompt
            prompt = get_geolocation_prompt(context_info, location_guess)

            # Call API with detected MIME type
            raw_response = self.api_client.generate_content(
                prompt=prompt,
                image_base64=image_base64,
                mime_type=mime_type
            )

            # Parse response
            result = self.response_parser.parse_response(raw_response)
            logger.info("Location analysis completed successfully")

            return result

        except GeoIntelError as e:
            # Log full details server-side for debugging
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            # Return a generic, user-safe error message without internal details
            return {
                "error": "Request could not be processed"
            }
        except Exception as e:
            # Log full details including stack trace, but do not expose them to the client
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # Return a generic message without including the raw exception string
            return {
                "error": "An unexpected error occurred"
            }
