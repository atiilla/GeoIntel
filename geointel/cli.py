import json
import sys
from .geointel import GeoIntel
from . import cli_args
from . import cli_formatter


def main():
    cli_formatter.display_banner()
    args = cli_args.parse_arguments()

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
                print(cli_formatter.format_error(results))
                sys.exit(1)
            
            print(cli_formatter.format_results(results))
            
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