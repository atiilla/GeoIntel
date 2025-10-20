"""
Custom exceptions for GeoIntel.

This module defines all custom exception types used throughout the GeoIntel package.
"""


class GeoIntelError(Exception):
    """
    Base exception for all GeoIntel errors.
    
    All custom GeoIntel exceptions inherit from this base class,
    allowing for easy catching of any GeoIntel-related error.
    """
    pass


class APIError(GeoIntelError):
    """
    Exception raised for API-related errors.
    
    This includes errors such as:
    - Failed API requests
    - Invalid API responses
    - API rate limiting
    - Authentication failures
    """
    pass


class ImageProcessingError(GeoIntelError):
    """
    Exception raised for image processing errors.
    
    This includes errors such as:
    - Failed image loading
    - Unsupported image formats
    - Image encoding failures
    - Network errors when downloading images
    """
    pass


class ValidationError(GeoIntelError):
    """
    Exception raised for validation errors.
    
    This includes errors such as:
    - Invalid coordinates
    - Invalid configuration values
    - Invalid response data
    """
    pass

