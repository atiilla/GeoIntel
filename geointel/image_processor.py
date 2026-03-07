import base64
import mimetypes
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests

from .config import DEFAULT_MIME_TYPE, IMAGE_DOWNLOAD_TIMEOUT, SUPPORTED_IMAGE_FORMATS
from .exceptions import InvalidImageError, NetworkError
from .logger import logger


class ImageProcessor:
    MIME_TYPE_SUFFIXES = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }

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
    def download_image(url: str) -> bytes:
       
        try:
            logger.info(f"Downloading image from URL: {url}")
            response = requests.get(url, timeout=IMAGE_DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            logger.debug(f"Successfully downloaded {len(response.content)} bytes")
            return response.content

        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timed out when downloading from: {url}")
        except requests.exceptions.ConnectionError:
            raise NetworkError(f"Connection failed for URL: {url}")
        except requests.exceptions.HTTPError as e:
            raise NetworkError(f"HTTP error when downloading image: {e}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Failed to download image: {e}")

    @staticmethod
    def load_local_image(path: str) -> bytes:
     
        try:
            logger.info(f"Loading local image: {path}")
            with open(path, "rb") as file:
                content = file.read()
            logger.debug(f"Successfully loaded {len(content)} bytes")
            return content

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
    def normalize_mime_type(cls, mime_type: Optional[str]) -> Optional[str]:
        if not mime_type:
            return None

        normalized = mime_type.strip().lower()
        if normalized == "image/jpg":
            normalized = "image/jpeg"

        if normalized in cls.MIME_TYPE_SUFFIXES:
            return normalized

        return None

    @classmethod
    def get_file_suffix(cls, mime_type: Optional[str]) -> str:
        normalized_mime_type = cls.normalize_mime_type(mime_type)
        return cls.MIME_TYPE_SUFFIXES.get(normalized_mime_type, ".jpg")

    @classmethod
    def parse_data_url(cls, image_data: str) -> Tuple[Optional[str], str]:
        if not image_data.startswith("data:"):
            return None, image_data

        header, separator, encoded_data = image_data.partition(",")
        if not separator or ";base64" not in header:
            raise InvalidImageError("Image data URI must be base64 encoded")

        mime_type = header[5:].split(";", 1)[0]
        normalized_mime_type = cls.normalize_mime_type(mime_type)
        if not normalized_mime_type:
            raise InvalidImageError(
                "Unsupported image MIME type. Supported formats: JPEG, PNG, WebP, GIF"
            )

        return normalized_mime_type, encoded_data

    @classmethod
    def get_mime_type(
        cls,
        image_path: str,
        mime_type_override: Optional[str] = None
    ) -> str:
        override_mime_type = cls.normalize_mime_type(mime_type_override)
        if override_mime_type:
            return override_mime_type

        parsed = urlparse(image_path)
        path = parsed.path if parsed.scheme in ("http", "https") else image_path
        mime_type, _ = mimetypes.guess_type(path)
        return cls.normalize_mime_type(mime_type) or DEFAULT_MIME_TYPE

    @classmethod
    def process_image(cls, image_path: str) -> str:
     
        # Validate format
        cls.validate_image_format(image_path)

        # Load image data
        if cls.is_url(image_path):
            image_data = cls.download_image(image_path)
        else:
            image_data = cls.load_local_image(image_path)

        # Encode to base64
        return cls.encode_to_base64(image_data)
