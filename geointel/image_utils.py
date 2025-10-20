import base64
import requests
import os
import mimetypes
from urllib.parse import urlparse
from typing import Optional, Tuple


def encode_image_to_base64(image_path: str) -> Tuple[str, str]:
    """
    Convert an image file to base64 encoding.
    Supports both local files and URLs.
    
    Args:
        image_path: Path to the image file or URL
        
    Returns:
        Tuple of (base64_encoded_string, mime_type)
        
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
            
            # Try to get MIME type from Content-Type header
            mime_type = response.headers.get('content-type', 'image/jpeg')
            # Handle cases where content-type includes charset or other parameters
            if ';' in mime_type:
                mime_type = mime_type.split(';')[0].strip()
            
            # Fallback to image/jpeg if MIME type is not recognized
            if not mime_type.startswith('image/'):
                mime_type = 'image/jpeg'
            
            return base64.b64encode(response.content).decode('utf-8'), mime_type
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
            # Infer MIME type from file extension
            mime_type, _ = mimetypes.guess_type(image_path)
            if mime_type is None or not mime_type.startswith('image/'):
                mime_type = 'image/jpeg'  # Safe fallback
            
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8'), mime_type
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except PermissionError:
            raise ValueError(f"Permission denied when accessing image file: {image_path}")
        except Exception as e:
            raise ValueError(f"Failed to read image file: {str(e)}")
