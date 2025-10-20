"""
GeoSpy - AI-powered geolocation analysis.

This package provides tools to analyze images and identify their likely
geographic locations using Google's Gemini AI model.
"""

from .geospy import GeoSpy
from .exceptions import GeoSpyError, APIError, ImageProcessingError, ValidationError

__version__ = "0.1.9"
__all__ = ["GeoSpy", "GeoSpyError", "APIError", "ImageProcessingError", "ValidationError"]