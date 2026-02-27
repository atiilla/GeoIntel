import base64
import mimetypes
import os
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse

import requests

from .config import DEFAULT_MIME_TYPE, IMAGE_DOWNLOAD_TIMEOUT, MAX_IMAGE_SIZE_BYTES, SUPPORTED_IMAGE_FORMATS
from .exceptions import InvalidImageError, NetworkError
from .logger import logger


class ImageProcessor:
    @staticmethod
    def is_url(path: str) -> bool:
       
        parsed = urlparse(path)
        return parsed.scheme in ("http", "https")

    @staticmethod
    def validate_image_format(path: str) -> None:
      
        if ImageProcessor.is_url(path):
            # For URLs, we can't validate extension reliably
            return

        extension = Path(path).suffix.lstrip(".").lower()
        if extension and extension not in SUPPORTED_IMAGE_FORMATS:
            raise InvalidImageError(
                f"Unsupported image format: {extension}. "
                f"Supported formats: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
            )

    @staticmethod
    def _check_size(data: bytes, source: str) -> None:
        if len(data) > MAX_IMAGE_SIZE_BYTES:
            size_mb = len(data) / (1024 * 1024)
            limit_mb = MAX_IMAGE_SIZE_BYTES / (1024 * 1024)
            raise InvalidImageError(
                f"Image is too large ({size_mb:.1f} MB). "
                f"Maximum allowed size is {limit_mb:.0f} MB. Source: {source}"
            )

    @staticmethod
    def _detect_mime_type(path: str) -> str:
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type and mime_type.startswith("image/"):
            return mime_type
        return DEFAULT_MIME_TYPE

    @staticmethod
    def download_image(url: str) -> Tuple[bytes, str]:
       
        try:
            logger.info(f"Downloading image from URL: {url}")
            response = requests.get(url, timeout=IMAGE_DOWNLOAD_TIMEOUT)
            response.raise_for_status()

            # Validate content-type
            content_type = response.headers.get("content-type", "").split(";")[0].strip()
            if not content_type.startswith("image/"):
                raise InvalidImageError(
                    f"URL does not return an image content-type: {content_type or 'unknown'}"
                )

            ImageProcessor._check_size(response.content, url)
            logger.debug(f"Successfully downloaded {len(response.content)} bytes")
            return response.content, content_type

        except (InvalidImageError, NetworkError):
            raise
        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timed out when downloading from: {url}")
        except requests.exceptions.ConnectionError:
            raise NetworkError(f"Connection failed for URL: {url}")
        except requests.exceptions.HTTPError as e:
            raise NetworkError(
                f"HTTP error {e.response.status_code} when downloading image from {url}"
            )
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Failed to download image: {e}")

    @staticmethod
    def load_local_image(path: str) -> Tuple[bytes, str]:
     
        try:
            logger.info(f"Loading local image: {path}")

            file_size = os.path.getsize(path)
            if file_size > MAX_IMAGE_SIZE_BYTES:
                size_mb = file_size / (1024 * 1024)
                limit_mb = MAX_IMAGE_SIZE_BYTES / (1024 * 1024)
                raise InvalidImageError(
                    f"Image file is too large ({size_mb:.1f} MB). "
                    f"Maximum allowed size is {limit_mb:.0f} MB."
                )

            with open(path, "rb") as file:
                content = file.read()

            mime_type = ImageProcessor._detect_mime_type(path)
            logger.debug(f"Successfully loaded {len(content)} bytes ({mime_type})")
            return content, mime_type

        except InvalidImageError:
            raise
        except FileNotFoundError:
            raise InvalidImageError(f"Image file not found: {path}")
        except PermissionError:
            raise InvalidImageError(f"Permission denied accessing: {path}")
        except Exception as e:
            raise InvalidImageError(f"Failed to read image file: {e}")

    @staticmethod
    def encode_to_base64(image_data: bytes) -> str:
     
        return base64.b64encode(image_data).decode("utf-8")

    @classmethod
    def process_image(cls, image_path: str) -> Tuple[str, str]:
        """
        Process an image and return its base64-encoded data and MIME type.
        
        Returns:
            Tuple of (base64_encoded_string, mime_type)
        """
        # Validate format
        cls.validate_image_format(image_path)

        # Load image data
        if cls.is_url(image_path):
            image_data, mime_type = cls.download_image(image_path)
        else:
            image_data, mime_type = cls.load_local_image(image_path)

        # Encode to base64
        return cls.encode_to_base64(image_data), mime_type
