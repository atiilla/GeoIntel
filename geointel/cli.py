import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, NoReturn

from .geointel import GeoIntel
from .exceptions import GeoIntelError


# Terminal color codes
class Colors:
    """ANSI color codes for terminal output."""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


def print_banner() -> None:
    banner = r"""
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
    print(banner)


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="geointel",
        description="GeoIntel - AI powered geolocation analysis tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  geointel --image photo.jpg
  geointel --image https://example.com/photo.jpg --context "Taken in summer"
  geointel --image photo.jpg --guess "Mediterranean" --output results.json
  geointel --web  # Launch web interface
        """
    )

    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch web interface"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address for web interface (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port number for web interface (default: 5000)"
    )
    parser.add_argument(
        "--image",
        type=str,
        help="Path to local image file or image URL"
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
        help="Output file path to save results (JSON format)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Custom Gemini API key (overrides GEMINI_API_KEY env var)"
    )

    return parser


def validate_output_path(output_path: str) -> None:
    output_file = Path(output_path)

    # Check if parent directory exists
    if not output_file.parent.exists():
        print(f"{Colors.RED}Error: Directory does not exist: {output_file.parent}{Colors.RESET}")
        sys.exit(1)

    # Check if file exists and warn
    if output_file.exists():
        print(f"{Colors.YELLOW}Warning: File will be overwritten: {output_path}{Colors.RESET}")


def get_confidence_color(confidence: str) -> str:
    confidence_colors = {
        "High": Colors.GREEN,
        "Medium": Colors.YELLOW,
        "Low": Colors.RED
    }
    return confidence_colors.get(confidence, Colors.RESET)


def format_location_info(location: Dict[str, Any]) -> str:
    city = location.get("city", "Unknown")
    state = location.get("state", "")
    country = location.get("country", "Unknown")

    parts = [city]
    if state:
        parts.append(state)
    parts.append(country)

    return ", ".join(parts)


def display_results(results: Dict[str, Any]) -> None:
    print(f"\n{Colors.GREEN}===== Analysis Results ====={Colors.RESET}")

    # Display interpretation
    print(f"\n{Colors.CYAN}Interpretation:{Colors.RESET}")
    print(results.get("interpretation", "No interpretation available"))

    # Display locations
    print(f"\n{Colors.CYAN}Possible Locations:{Colors.RESET}")
    locations = results.get("locations", [])

    if not locations:
        print("No locations identified")
        return

    for i, location in enumerate(locations, 1):
        confidence = location.get("confidence", "Unknown")
        confidence_color = get_confidence_color(confidence)

        print(f"\n{i}. {format_location_info(location)}")
        print(f"   Confidence: {confidence_color}{confidence}{Colors.RESET}")

        # Display coordinates and map link
        coordinates = location.get("coordinates")
        if coordinates:
            lat = coordinates.get("latitude", 0)
            lng = coordinates.get("longitude", 0)
            if lat != 0 or lng != 0:
                print(f"   Coordinates: {lat}, {lng}")
                print(f"   Google Maps: https://www.google.com/maps?q={lat},{lng}")

        # Display explanation
        explanation = location.get("explanation", "No explanation available")
        print(f"   Explanation: {explanation}")


def display_error(results: Dict[str, Any]) -> NoReturn:
    print(f"\n{Colors.RED}Error: {results['error']}{Colors.RESET}")

    if "details" in results:
        print(f"Details: {results['details']}")

    sys.exit(1)


def save_results(results: Dict[str, Any], output_path: str) -> None:
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n{Colors.GREEN}Results saved to: {output_path}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Failed to save results: {e}{Colors.RESET}")


def main() -> None:
    print_banner()

    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()

    # Check if web interface mode
    if args.web:
        print(f"\n{Colors.CYAN}Starting GeoIntel Web Interface...{Colors.RESET}")
        try:
            from .web_server import run_server
            run_server(host=args.host, port=args.port, debug=False)
        except ImportError as e:
            print(f"\n{Colors.RED}Error: Flask is required for web interface{Colors.RESET}")
            print(f"Install it with: pip install flask flask-cors")
            sys.exit(1)
        except Exception as e:
            print(f"\n{Colors.RED}Failed to start web server: {e}{Colors.RESET}")
            sys.exit(1)
        return

    # Require --image for CLI mode
    if not args.image:
        parser.error("the following arguments are required: --image (or use --web for web interface)")

    # Validate output path if provided
    if args.output:
        validate_output_path(args.output)

    # Display processing info
    print(f"\nAnalyzing image: {args.image}")
    if args.image.startswith(('http://', 'https://')):
        print("Downloading image from URL...")
    print("This may take a few moments...")

    try:
        # Initialize GeoIntel
        geointel = GeoIntel(api_key=args.api_key)

        # Perform analysis
        results = geointel.locate(
            image_path=args.image,
            context_info=args.context,
            location_guess=args.guess
        )

        # Handle errors
        if "error" in results:
            display_error(results)

        # Display results
        display_results(results)

        # Save to file if requested
        if args.output:
            save_results(results, args.output)

    except GeoIntelError as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()