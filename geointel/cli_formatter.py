from typing import Dict, Any, List
import sys


def display_banner():
    """Display the GeoIntel ASCII art banner."""
    font = """
                 _      __      __
  ___ ____ ___  (_)__  / /____ / /
 / _ `/ -_) _ \/ / _ \/ __/ -_) / 
 \_, /\__/\___/_/_//_/\__/\__/_/  
/___/                             
----------------------------------------
AI powered geo-location tool
Uncover the location of photos using AI
----------------------------------------
# Disclaimer: Experimental use only. Not for production.
# Github: https://github.com/atiilla/geointel
"""
    print(font)


def format_error(error_result: Dict[str, Any]) -> str:
    """
    Format an error result for display.
    
    Args:
        error_result: Dictionary containing error information
        
    Returns:
        Formatted error string with ANSI color codes
    """
    error_msg = f"\033[91mError: {error_result.get('error', 'Unknown error')}\033[0m"
    
    if "details" in error_result:
        error_msg += f"\nDetails: {error_result['details']}"
    
    if "exception" in error_result:
        error_msg += f"\nException: {error_result['exception']}"
    
    return error_msg


def format_location(location: Dict[str, Any], index: int) -> str:
    """
    Format a single location entry for display.
    
    Args:
        location: Dictionary containing location information
        index: The index of this location in the list
        
    Returns:
        Formatted location string with ANSI color codes
    """
    confidence = location.get("confidence", "Unknown")
    confidence_color = "\033[92m" if confidence == "High" else "\033[93m" if confidence == "Medium" else "\033[91m"
    
    output = f"\n{index + 1}. {location.get('city', 'Unknown city')}, {location.get('state', '')}, {location.get('country', 'Unknown country')}\n"
    output += f"   Confidence: {confidence_color}{confidence}\033[0m\n"
    
    if "coordinates" in location and location["coordinates"]:
        coords = location["coordinates"]
        lat = coords.get("latitude", 0)
        lng = coords.get("longitude", 0)
        output += f"   Coordinates: {lat}, {lng}\n"
        output += f"   Google Maps: https://www.google.com/maps?q={lat},{lng}\n"
    
    output += f"   Explanation: {location.get('explanation', 'No explanation available')}"
    
    return output


def format_results(results: Dict[str, Any]) -> str:
    """
    Format successful results for display.
    
    Args:
        results: Dictionary containing the analysis results
        
    Returns:
        Formatted results string with ANSI color codes
    """
    output = "\n\033[92m===== Analysis Results =====\033[0m\n"
    output += f"\033[96mInterpretation:\033[0m\n"
    output += f"{results.get('interpretation', 'No interpretation available')}\n"
    
    output += f"\n\033[96mPossible Locations:\033[0m"
    
    for i, location in enumerate(results.get("locations", [])):
        output += format_location(location, i)
    
    return output
