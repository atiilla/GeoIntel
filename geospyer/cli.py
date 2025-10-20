"""
Command-line interface for GeoSpy.

This module provides a CLI for analyzing images and identifying their
geographic locations using AI.
"""

import argparse
import json
import logging
import sys
from typing import Dict, Any, Optional

from geospyer import GeoSpy, GeoSpyError
from geospyer.config import (
    COLOR_RED,
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_CYAN,
    COLOR_BOLD,
    COLOR_RESET,
)


# Set up logging
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the CLI.
    
    Args:
        verbose: If True, set logging level to DEBUG
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def banner() -> None:
    """Display the GeoSpy banner."""
    font = """
█▀▀▀ █▀▀ █▀▀█ █▀▀ █▀▀█ █──█ 
█─▀█ █▀▀ █──█ ▀▀█ █──█ █▄▄█ 
▀▀▀▀ ▀▀▀ ▀▀▀▀ ▀▀▀ █▀▀▀ ▄▄▄█
----------------------------------------
AI powered geo-location tool
Uncover the location of photos using AI
----------------------------------------
# Disclaimer: Experimental use only. Not for production.
# Github: https://github.com/atiilla/geospy
"""
    print(font)


def print_error(message: str, details: Optional[str] = None, 
                exception: Optional[str] = None) -> None:
    """
    Print formatted error messages.
    
    Args:
        message: Main error message
        details: Optional additional details
        exception: Optional exception information
    """
    print(f"{COLOR_RED}✗ Error: {message}{COLOR_RESET}", file=sys.stderr)
    if details:
        print(f"  Details: {details}", file=sys.stderr)
    if exception:
        print(f"  Exception: {exception}", file=sys.stderr)
    logger.error(f"{message} - Details: {details} - Exception: {exception}")


def print_success(message: str) -> None:
    """
    Print formatted success messages.
    
    Args:
        message: Success message
    """
    print(f"{COLOR_GREEN}✓ {message}{COLOR_RESET}")
    logger.info(message)


def print_info(message: str) -> None:
    """
    Print formatted info messages.
    
    Args:
        message: Info message
    """
    print(f"{COLOR_CYAN}ℹ {message}{COLOR_RESET}")
    logger.info(message)


def display_results(results: Dict[str, Any]) -> None:
    """
    Display analysis results in a formatted manner.
    
    Args:
        results: Analysis results from GeoSpy
    """
    print(f"\n{COLOR_GREEN}{'=' * 50}")
    print("ANALYSIS RESULTS")
    print(f"{'=' * 50}{COLOR_RESET}")
    
    # Display interpretation
    interpretation = results.get("interpretation", "No interpretation available")
    print(f"\n{COLOR_CYAN}📝 Interpretation:{COLOR_RESET}")
    print(f"   {interpretation}")
    
    # Display locations
    locations = results.get("locations", [])
    if not locations:
        print(f"\n{COLOR_YELLOW}⚠ No locations identified{COLOR_RESET}")
        return
    
    print(f"\n{COLOR_CYAN}📍 Possible Locations ({len(locations)}):{COLOR_RESET}")
    
    for i, location in enumerate(locations, 1):
        confidence = location.get("confidence", "Unknown")
        
        # Color code confidence levels
        confidence_colors = {
            "High": COLOR_GREEN,
            "Medium": COLOR_YELLOW,
            "Low": COLOR_RED
        }
        confidence_color = confidence_colors.get(confidence, COLOR_RESET)
        
        # Format location name
        city = location.get("city", "Unknown city")
        state = location.get("state", "")
        country = location.get("country", "Unknown country")
        location_name = f"{city}, {state}, {country}" if state else f"{city}, {country}"
        
        print(f"\n  {i}. {COLOR_BOLD}{location_name}{COLOR_RESET}")
        print(f"     Confidence: {confidence_color}{confidence}{COLOR_RESET}")
        
        # Display coordinates and map link
        if "coordinates" in location and location["coordinates"]:
            coords = location["coordinates"]
            lat = coords.get("latitude", 0)
            lng = coords.get("longitude", 0)
            print(f"     Coordinates: {lat}, {lng}")
            print(f"     🗺️  Google Maps: https://www.google.com/maps?q={lat},{lng}")
        
        # Display explanation
        explanation = location.get("explanation", "No explanation available")
        print(f"     Explanation: {explanation}")


def save_results(results: Dict[str, Any], output_path: str) -> None:
    """
    Save results to a JSON file.
    
    Args:
        results: Analysis results to save
        output_path: Path to save the JSON file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print_success(f"Results saved to {output_path}")
    except IOError as e:
        print_error(f"Failed to save results to {output_path}", exception=str(e))


def main() -> None:
    """Main entry point for the GeoSpy CLI."""
    parser = argparse.ArgumentParser(
        prog="geospyer",
        description="GeoSpy - AI powered geolocation tool",
        epilog="Example: geospyer --image photo.jpg --context 'Taken in summer' --output results.json"
    )
    
    parser.add_argument(
        "--image",
        type=str,
        required=False,
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
        help="Custom Gemini API key (or set GEMINI_API_KEY environment variable)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Display banner
    banner()

    # Validate required arguments
    if not args.image:
        print_error("No image provided")
        print("\nUsage: geospyer --image <path_or_url> [options]")
        print("Run 'geospyer --help' for more information")
        sys.exit(1)

    # Initialize GeoSpy
    try:
        geospy = GeoSpy(api_key=args.api_key)
    except ValueError as e:
        print_error("Failed to initialize GeoSpy", exception=str(e))
        print("\nPlease set GEMINI_API_KEY environment variable or use --api-key option")
        sys.exit(1)
    except GeoSpyError as e:
        print_error("Failed to initialize GeoSpy", exception=str(e))
        sys.exit(1)
    except Exception as e:
        print_error("An unexpected error occurred during initialization", exception=str(e))
        sys.exit(1)
    
    # Analyze image
    print_info(f"Analyzing image: {args.image}")
    
    if args.image.startswith(('http://', 'https://')):
        print_info("Downloading image from URL...")
    
    if args.context:
        print_info(f"Using context: {args.context}")
    
    if args.guess:
        print_info(f"Using location guess: {args.guess}")
    
    print_info("Processing... This may take a few moments...")
    
    try:
        results = geospy.locate(
            image_path=args.image,
            context_info=args.context,
            location_guess=args.guess
        )
        
        # Check for errors in results
        if "error" in results:
            print_error(
                results["error"],
                details=results.get("details"),
                exception=results.get("exception")
            )
            sys.exit(1)
        
        # Display results
        display_results(results)
        
        # Save to file if requested
        if args.output:
            save_results(results, args.output)
            
    except KeyboardInterrupt:
        print(f"\n\n{COLOR_YELLOW}⚠ Operation cancelled by user{COLOR_RESET}")
        sys.exit(130)
    except GeoSpyError as e:
        print_error("A GeoSpy error occurred", exception=str(e))
        sys.exit(1)
    except Exception as e:
        print_error("An unexpected error occurred", exception=str(e))
        logger.exception("Unexpected error during analysis")
        sys.exit(1)


if __name__ == "__main__":
    main()