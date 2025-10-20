# GeoSpy Library Examples

This directory contains simple examples showing how to use GeoSpy as a library.

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your Gemini API key:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
   On Windows:
   ```bash
   set GEMINI_API_KEY=your-api-key-here
   ```

## Library Usage

GeoSpy returns a JSON object that you can use in your application. Here's how to use it:

```python
from geospyer import GeoSpy

# Initialize
geospy = GeoSpy()  # Uses GEMINI_API_KEY from environment

# Analyze an image and get the result JSON
result = geospy.locate(image_path="your_image.jpg")

# The result is a JSON object you can work with
if "error" in result:
    # Handle errors
    print(f"Error: {result['error']}")
else:
    # Work with the data
    locations = result.get("locations", [])
    if locations:
        top_location = locations[0]
        print(f"Location: {top_location.get('city')}, {top_location.get('country')}")
```

### Accessing the JSON Data

The result object contains these main sections:

1. `interpretation`: Analysis of the image
2. `locations`: Array of possible locations, ordered by confidence

Example of accessing location data:

```python
# Get coordinates for Google Maps
if "locations" in result and result["locations"]:
    location = result["locations"][0]
    
    if "coordinates" in location:
        lat = location["coordinates"].get("latitude")
        lng = location["coordinates"].get("longitude")
        maps_url = f"https://www.google.com/maps?q={lat},{lng}"
```

### Saving to a File

You can easily save the results to a JSON file:

```python
import json

with open("result.json", "w") as f:
    json.dump(result, f, indent=2)
```

### Run the Example

```bash
python library_usage.py
```

This will analyze an image and save the results to `geospy_result.json` without printing to the console.

## Examples

### 1. Basic Library Usage (`library_usage.py`)

The simplest way to use GeoSpy:

```python
from geospyer import GeoSpy

# Initialize
geospy = GeoSpy()  # Uses GEMINI_API_KEY from environment

# Analyze an image
result = geospy.locate(image_path="your_image.jpg")

# Print results
print(result)
```

Run the example with:
```bash
python library_usage.py
```

### 2. Advanced Usage (`advanced_usage.py`) 🆕

Demonstrates best practices including:
- ✅ Proper error handling with custom exceptions
- ✅ Logging configuration
- ✅ Batch processing multiple images
- ✅ Working with results programmatically
- ✅ Saving results to files

```python
from geospyer import GeoSpy, APIError, ImageProcessingError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    geospy = GeoSpy()
    result = geospy.locate("image.jpg")
    
    # Process results
    if "error" not in result:
        for location in result["locations"]:
            print(f"{location['city']}, {location['country']}")
            
except APIError as e:
    print(f"API error: {e}")
except ImageProcessingError as e:
    print(f"Image processing error: {e}")
```

Run the example with:
```bash
python advanced_usage.py
```

### 3. Simple API

The `simple_api.py` file shows a minimal Flask API (if available):

```python
from flask import Flask, request, jsonify
from geospyer import GeoSpy

app = Flask(__name__)
geospy = GeoSpy()

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    image_url = data['image_url']
    
    result = geospy.locate(image_path=image_url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

Run it with:
```bash
python simple_api.py
```

Test it with:
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'
```

## Error Handling

GeoSpy provides custom exceptions for different error scenarios:

```python
from geospyer import GeoSpy, GeoSpyError, APIError, ImageProcessingError, ValidationError

try:
    geospy = GeoSpy()
    result = geospy.locate("image.jpg")
    
except APIError as e:
    # Handle API-related errors (failed requests, invalid responses, etc.)
    print(f"API error: {e}")
    
except ImageProcessingError as e:
    # Handle image loading/processing errors
    print(f"Image error: {e}")
    
except ValidationError as e:
    # Handle validation errors
    print(f"Validation error: {e}")
    
except GeoSpyError as e:
    # Catch any other GeoSpy errors
    print(f"GeoSpy error: {e}")
    
except ValueError as e:
    # Handle configuration errors (e.g., missing API key)
    print(f"Configuration error: {e}")
```

## Logging

Enable logging to see detailed information:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # or logging.DEBUG for more detail
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now use GeoSpy (it will output logs)
from geospyer import GeoSpy
geospy = GeoSpy()
```

## Utility Functions 🆕

GeoSpy includes helpful utility functions:

```python
from geospyer.utils import (
    validate_coordinates,
    format_location_string,
    get_google_maps_url,
    is_url,
    sanitize_api_key
)

# Validate coordinates
if validate_coordinates(40.7128, -74.0060):
    print("Valid coordinates")

# Format location
location = format_location_string("New York", "NY", "USA")
# Output: "New York, NY, USA"

# Generate Google Maps URL
maps_url = get_google_maps_url(40.7128, -74.0060)

# Check if path is URL
if is_url("https://example.com/image.jpg"):
    print("It's a URL")
```

## Using in Your Projects

To use GeoSpy in your own projects:

1. Install the package:
   ```bash
   pip install geospyer
   ```

2. Import and initialize:
   ```python
   from geospyer import GeoSpy
   
   # Initialize with API key
   geospy = GeoSpy(api_key="your-api-key-here")
   
   # Or use from environment variable
   # geospy = GeoSpy()
   ```

3. Analyze images:
   ```python
   results = geospy.locate(
       image_path="path/to/image.jpg",
       context_info="Optional context",
       location_guess="Optional guess"
   )
   ```

## Supported Image Formats

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- GIF (`.gif`)
- WebP (`.webp`)
- BMP (`.bmp`)

MIME types are automatically detected from file extensions and HTTP headers.

## Additional Resources

- 📖 **[Quick Reference Guide](../QUICK_REFERENCE.md)** - Quick start and common patterns
- 📋 **[Improvements Documentation](../IMPROVEMENTS.md)** - Detailed code improvements
- 📝 **[Changelog](../CHANGELOG.md)** - Version history and changes