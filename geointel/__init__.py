"""
GeoIntel - AI-powered geolocation analysis.

This package provides tools to analyze images and identify their likely
geographic locations using Google's Gemini AI model.
"""

from .geointel import GeoIntel
from .exceptions import GeoIntelError, APIError, ImageProcessingError, ValidationError

__version__ = "0.1.10"
__all__ = ["GeoIntel", "GeoIntelError", "APIError", "ImageProcessingError", "ValidationError"]