"""
Utility functions for GeoSpy.

This module provides helper functions for validation, formatting,
and other common operations.
"""

from typing import Dict, Any, Optional
import re


def validate_coordinates(lat: float, lng: float) -> bool:
    """
    Validate geographic coordinates.
    
    Args:
        lat: Latitude value
        lng: Longitude value
        
    Returns:
        True if coordinates are valid, False otherwise
    """
    return -90 <= lat <= 90 and -180 <= lng <= 180


def format_location_string(city: str, state: str, country: str) -> str:
    """
    Format location information into a readable string.
    
    Args:
        city: City name
        state: State/region/province name
        country: Country name
        
    Returns:
        Formatted location string
    """
    if state:
        return f"{city}, {state}, {country}"
    return f"{city}, {country}"


def extract_json_from_text(text: str) -> str:
    """
    Extract JSON content from text that might contain markdown or other formatting.
    
    Args:
        text: Text potentially containing JSON
        
    Returns:
        Cleaned JSON string
    """
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Try to find JSON object boundaries
    start = text.find('{')
    end = text.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    
    return text.strip()


def sanitize_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Sanitize API key for logging purposes.
    
    Args:
        api_key: API key to sanitize
        visible_chars: Number of characters to show at the end
        
    Returns:
        Sanitized API key string
    """
    if len(api_key) <= visible_chars:
        return '*' * len(api_key)
    
    return f"{'*' * (len(api_key) - visible_chars)}{api_key[-visible_chars:]}"


def is_url(path: str) -> bool:
    """
    Check if a path is a URL.
    
    Args:
        path: Path or URL to check
        
    Returns:
        True if path is a URL, False otherwise
    """
    return path.startswith(('http://', 'https://'))


def get_google_maps_url(lat: float, lng: float) -> str:
    """
    Generate a Google Maps URL for given coordinates.
    
    Args:
        lat: Latitude
        lng: Longitude
        
    Returns:
        Google Maps URL
    """
    return f"https://www.google.com/maps?q={lat},{lng}"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

