"""
Custom exceptions for GeoSpy.

This module defines all custom exception types used throughout the GeoSpy package.
"""


class GeoSpyError(Exception):
    """
    Base exception for all GeoSpy errors.
    
    All custom GeoSpy exceptions inherit from this base class,
    allowing for easy catching of any GeoSpy-related error.
    """
    pass


class APIError(GeoSpyError):
    """
    Exception raised for API-related errors.
    
    This includes errors such as:
    - Failed API requests
    - Invalid API responses
    - API rate limiting
    - Authentication failures
    """
    pass


class ImageProcessingError(GeoSpyError):
    """
    Exception raised for image processing errors.
    
    This includes errors such as:
    - Failed image loading
    - Unsupported image formats
    - Image encoding failures
    - Network errors when downloading images
    """
    pass


class ValidationError(GeoSpyError):
    """
    Exception raised for validation errors.
    
    This includes errors such as:
    - Invalid coordinates
    - Invalid configuration values
    - Invalid response data
    """
    pass

