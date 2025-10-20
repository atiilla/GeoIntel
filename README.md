# geospy

![GitHub](https://img.shields.io/github/license/atiilla/geospy)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/atiilla/geospy)

Python tool using Google's Gemini API to uncover the location where photos were taken through AI-powered geo-location analysis.

[![asciicast](https://asciinema.org/a/722241.svg)](https://asciinema.org/a/722241)

## Installation

```bash
pip install geospyer
```

## Usage

### Command Line Interface

```bash
geospyer --image path/to/your/image.jpg
```

#### Available Arguments

| Argument | Description |
|----------|-------------|
| `--image` | **Required.** Path to the image file or URL to analyze |
| `--context` | Additional context information about the image |
| `--guess` | Your guess of where the image might have been taken |
| `--output` | Output file path to save the results (JSON format) |
| `--api-key` | Custom Gemini API key |
| `--verbose`, `-v` | Enable verbose logging for debugging |

#### Examples

Basic usage:
```bash
geospyer --image vacation_photo.jpg
```

With additional context:
```bash
geospyer --image vacation_photo.jpg --context "Taken during summer vacation in 2023"
```

With location guess:
```bash
geospyer --image vacation_photo.jpg --guess "Mediterranean coast"
```

Saving results to a file:
```bash
geospyer --image vacation_photo.jpg --output results.json
```

Using a custom API key:
```bash
geospyer --image vacation_photo.jpg --api-key "your-api-key-here"
```

Enable verbose logging for debugging:
```bash
geospyer --image vacation_photo.jpg --verbose
```

### API Key Setup

GeoSpy uses Google's Gemini API. You can:
1. Set the API key as an environment variable: `GEMINI_API_KEY=your_key_here`
2. Pass the API key directly when initializing: `GeoSpy(api_key="your_key_here")`
3. Use the `--api-key` parameter in the command line

Get your Gemini API key from [Google AI Studio](https://ai.google.dev/).

### Python Library

#### Basic Usage

```python
from geospyer import GeoSpy

# Initialize GeoSpy
geospy = GeoSpy()  # Uses GEMINI_API_KEY from environment

# Analyze an image and get JSON result
result = geospy.locate(image_path="image.jpg")

# Work with the JSON data
if "error" in result:
    print(f"Error: {result['error']}")
else:
    # Access the first location
    if "locations" in result and result["locations"]:
        location = result["locations"][0]
        print(f"Location: {location['city']}, {location['country']}")
        
        # Get Google Maps URL
        if "coordinates" in location:
            lat = location["coordinates"]["latitude"]
            lng = location["coordinates"]["longitude"]
            maps_url = f"https://www.google.com/maps?q={lat},{lng}"
```

#### Advanced Usage with Error Handling

```python
from geospyer import GeoSpy, APIError, ImageProcessingError
import logging

# Configure logging (optional)
logging.basicConfig(level=logging.INFO)

try:
    geospy = GeoSpy()
    result = geospy.locate(
        image_path="image.jpg",
        context_info="Historic building in urban setting",
        location_guess="Europe"
    )
    
    if "error" not in result:
        print(f"Found {len(result['locations'])} location(s)")
        
except APIError as e:
    print(f"API error: {e}")
except ImageProcessingError as e:
    print(f"Image processing error: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
```

#### Using Utility Functions

```python
from geospyer.utils import validate_coordinates, format_location_string, get_google_maps_url

# Validate coordinates
if validate_coordinates(40.7128, -74.0060):
    print("Valid coordinates")

# Format location string
location = format_location_string("New York", "NY", "USA")
# Output: "New York, NY, USA"

# Generate Google Maps URL
maps_url = get_google_maps_url(40.7128, -74.0060)
```

See the [examples directory](./examples) for more detailed usage examples, including batch processing and advanced patterns.

## Features

### Core Features
- 🤖 **AI-powered geolocation** using Google's Gemini API
- 🗺️ **Google Maps integration** with automatic coordinate linking
- 📊 **Confidence levels** for location predictions (High/Medium/Low)
- 🌐 **URL support** - Analyze images from URLs or local files
- 📝 **Context support** - Provide additional context and location guesses
- 💾 **Export results** to JSON format

### Image Support
- 🖼️ **Multiple formats**: JPEG, PNG, GIF, WebP, BMP
- 🔍 **Automatic MIME type detection**
- 🌍 **URL and local file support**

### Developer Features
- 🐍 **Type hints** throughout the codebase
- 📚 **Comprehensive documentation** and examples
- 🛡️ **Custom exceptions** for better error handling
- 📊 **Logging support** with configurable levels
- 🔧 **Utility functions** for common tasks
- ✅ **Production-ready** code structure

### CLI Features
- 🎨 **Colored output** for better readability
- 🔍 **Verbose mode** for debugging (`--verbose`)
- 📄 **JSON export** option
- ⚙️ **Flexible API key configuration**

## Response Format

The API returns a structured JSON response with:

```json
{
  "interpretation": "Comprehensive analysis of the image including architectural style, environment, and cultural elements...",
  "locations": [
    {
      "city": "City Name",
      "state": "State/Province",
      "country": "Country Name",
      "confidence": "High",
      "coordinates": {
        "latitude": 40.7128,
        "longitude": -74.0060
      },
      "explanation": "Detailed reasoning for this location identification..."
    }
  ]
}
```

**Response fields:**
- `interpretation`: Comprehensive analysis of the image
- `locations`: Array of possible locations (ordered by confidence) with:
  - `city`: City name
  - `state`: State/province/region name
  - `country`: Country name
  - `confidence`: Confidence level (`High`, `Medium`, or `Low`)
  - `coordinates`: Latitude and longitude
  - `explanation`: Detailed reasoning for the identification

## Documentation

- 📖 **[Quick Reference Guide](./QUICK_REFERENCE.md)** - Quick start and common patterns
- 📋 **[Improvements Documentation](./IMPROVEMENTS.md)** - Detailed code improvements
- 📝 **[Changelog](./CHANGELOG.md)** - Version history and changes
- 💡 **[Examples](./examples/)** - Code examples and usage patterns

## Architecture

GeoSpy is built with a modular architecture:

```
geospyer/
├── __init__.py          # Package exports
├── geospy.py            # Main GeoSpy class
├── cli.py               # Command-line interface
├── config.py            # Configuration and constants
├── prompts.py           # AI prompt templates
├── exceptions.py        # Custom exception classes
└── utils.py             # Utility functions
```

**Key Components:**
- **Custom Exceptions**: `GeoSpyError`, `APIError`, `ImageProcessingError`, `ValidationError`
- **Logging System**: Professional logging with configurable levels
- **Type Safety**: Complete type hints for better IDE support
- **Utilities**: Helper functions for validation, formatting, and more

## Disclaimer
GeoSpy is intended for educational and research purposes only. While it uses AI models to estimate the location of where an image was taken, its predictions are not guaranteed to be accurate. Do not use this tool for surveillance, stalking, law enforcement, or any activity that may infringe on personal privacy, violate laws, or cause harm.

The author(s) and contributors are not responsible for any damages, legal issues, or consequences resulting from the use or misuse of this software. Use at your own risk and discretion.

Always comply with local, national, and international laws and regulations when using AI-based tools.


## Contributing

1. Fork the repository
2. Create a new branch (git checkout -b feature/new-feature).
3. Commit your changes (git commit -am 'Add new feature').
4. Push to the branch (git push origin feature/new-feature).
5. Create a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments