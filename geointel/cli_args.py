import argparse
from typing import Any


def parse_arguments() -> Any:
    """
    Parse command line arguments for the GeoIntel CLI.
    
    Returns:
        Parsed arguments object
    """
    parser = argparse.ArgumentParser(
        prog="geointel",
        description="GeoIntel - AI powered geolocation tool"
    )
    
    parser.add_argument(
        "--image",
        type=str,
        help="Image path or URL to analyze"
    )
    parser.add_argument(
        "--context",
        type=str,
        help="Additional context information about the image"
    )
    parser.add_argument(
        "--guess",
        type=str,
        help="Your guess of where the image might have been taken"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path to save the results (JSON format)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Custom Gemini API key"
    )
    
    return parser.parse_args()

