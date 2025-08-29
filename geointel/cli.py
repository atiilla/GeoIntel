import argparse
import json
from geointel import GeoIntel
import sys


def banner():
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


def main():
    banner()
    parser = argparse.ArgumentParser(
        prog="geointel",
        description="GeoIntel - AI powered geolocation tool"
    )
    parser.add_argument("--image", type=str, help="Image path or URL to analyze")
    parser.add_argument("--context", type=str, help="Additional context information about the image")
    parser.add_argument("--guess", type=str, help="Your guess of where the image might have been taken")
    parser.add_argument("--output", type=str, help="Output file path to save the results (JSON format)")
    parser.add_argument("--api-key", type=str, help="Custom Gemini API key")
    args = parser.parse_args()

    if args.image:
        # Initialize GeoIntel with optional API key
        geointel = GeoIntel(api_key=args.api_key)
        
        # Get results
        print(f"Analyzing image: {args.image}")
        if args.image.startswith(('http://', 'https://')):
            print("Downloading image from URL...")
        print("This may take a few moments...")
        
        try:
            results = geointel.locate(
                image_path=args.image,
                context_info=args.context,
                location_guess=args.guess
            )
            
            # Display the results
            if "error" in results:
                print(f"\033[91mError: {results['error']}\033[0m")
                if "details" in results:
                    print(f"Details: {results['details']}")
                if "exception" in results:
                    print(f"Exception: {results['exception']}")
                sys.exit(1)
            
            print("\n\033[92m===== Analysis Results =====\033[0m")
            print(f"\033[96mInterpretation:\033[0m")
            print(results.get("interpretation", "No interpretation available"))
            
            print("\n\033[96mPossible Locations:\033[0m")
            for i, location in enumerate(results.get("locations", [])):
                confidence = location.get("confidence", "Unknown")
                confidence_color = "\033[92m" if confidence == "High" else "\033[93m" if confidence == "Medium" else "\033[91m"
                
                print(f"\n{i+1}. {location.get('city', 'Unknown city')}, {location.get('state', '')}, {location.get('country', 'Unknown country')}")
                print(f"   Confidence: {confidence_color}{confidence}\033[0m")
                
                if "coordinates" in location and location["coordinates"]:
                    coords = location["coordinates"]
                    lat = coords.get("latitude", 0)
                    lng = coords.get("longitude", 0)
                    print(f"   Coordinates: {lat}, {lng}")
                    print(f"   Google Maps: https://www.google.com/maps?q={lat},{lng}")
                
                print(f"   Explanation: {location.get('explanation', 'No explanation available')}")
            
            # Save to file if requested
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"\nResults saved to {args.output}")
        except Exception as e:
            print(f"\033[91mError: An unexpected error occurred: {str(e)}\033[0m")
            sys.exit(1)
    else:
        print("Please provide an image path or URL using the --image argument.")


if __name__ == "__main__":
    main()