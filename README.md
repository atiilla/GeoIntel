# GeoIntel

![PyPI - Version](https://img.shields.io/pypi/v/geointel?style=flat)


Python tool using Google's Gemini API to uncover the location where photos were taken through AI-powered geo-location analysis.

## Installation

```bash
# Basic installation
pip install geointel
```

## Usage

### Web Interface (NEW!)

Launch the interactive web interface with a modern UI:

```bash
- Standard:
$ geointel --web

- Custom host and port:
$ geointel --web --host 0.0.0.0 --port 4000 
```

<img src="screenshot.jpg" alt="GeoIntel Web Interface">

Then open your browser to `http://127.0.0.1:5000`

Features:
- Drag-and-drop image upload
- In-browser API key configuration
- Interactive 3D Google Maps
- Real-time AI analysis with detailed explanations

### Command Line Interface

```bash
geointel --image path/to/your/image.jpg
```

[![asciicast](https://asciinema.org/a/I6NqhIr6QkBWaaHNjSlieId5s.svg)](https://asciinema.org/a/I6NqhIr6QkBWaaHNjSlieId5s)

Available Arguments

Argument	Description
```
--web	Launch web interface (no --image required)
--host	Host address for web interface (default: 127.0.0.1)
--port	Port number for web interface (default: 5000)
--image	Required for CLI mode. Path to the image file or URL to analyze
--context	Additional context information about the image
--guess	Your guess of where the image might have been taken
--output	Output file path to save the results (JSON format)
--api-key	Custom Gemini API key
```

Examples
```bash
Launch web interface:
$ geointel --web

Basic CLI usage:
$ geointel --image vacation_photo.jpg

With additional context:
$ geointel --image vacation_photo.jpg --context "Taken during summer vacation in 2023"

With location guess:
$ geointel --image vacation_photo.jpg --guess "Mediterranean coast"

Saving results to a file:
$ geointel --image vacation_photo.jpg --output results.json

Using a custom API key:
$ geointel --image vacation_photo.jpg --api-key "your-api-key-here"
```

API Key Setup

GeoIntel uses Google's Gemini API. You can:
```
- Set the API key as an environment variable: GEMINI_API_KEY=your_key_here

- Use the --api-key parameter in the command line
```


Get your Gemini API key from Google AI Studio.

### SDK
```
from geointel import GeoIntel

# Initialize GeoIntel
geointel = GeoIntel()

# Analyze an image and get JSON result
result = geointel.locate(image_path="image.jpg")

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

Features

- AI-powered geolocation of images using Google's Gemini API

- Generate Google Maps links based on image coordinates

- Provide confidence levels for location predictions

- Support for additional context and location guesses

- Export results to JSON

- Handles both local image files and image URLs


Response Format

- The API returns a structured JSON response with:

- interpretation: Comprehensive analysis of the image

- locations: Array of possible locations with:

- Country, state, and city information

- Confidence level (High/Medium/Low)

- Coordinates (latitude/longitude)

- Detailed explanation of the reasoning



Disclaimer:

GeoIntel is intended for educational and research purposes only. While it uses AI models to estimate the location of where an image was taken, its predictions are not guaranteed to be accurate. Do not use this tool for surveillance, stalking, law enforcement, or any activity that may infringe on personal privacy, violate laws, or cause harm.

The author(s) and contributors are not responsible for any damages, legal issues, or consequences resulting from the use or misuse of this software. Use at your own risk and discretion.

Always comply with local, national, and international laws and regulations when using AI-based tools.

Contributing

1. Fork the repository

2. Create a new branch (git checkout -b feature/new-feature).

3. Commit your changes (git commit -am 'Add new feature').

4. Push to the branch (git push origin feature/new-feature).

5. Create a pull request.


License

This project is licensed under the MIT License - see the LICENSE file for details.


![Star History Chart](https://api.star-history.com/svg?repos=atiilla/geointel&type=Date)