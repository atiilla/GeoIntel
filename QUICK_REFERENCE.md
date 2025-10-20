# GeoSpy Quick Reference Guide

## Installation

```bash
pip install -r requirements.txt
```

## Basic Usage

### As a Library

```python
from geospyer import GeoSpy

# Initialize with API key
geospy = GeoSpy(api_key="your_gemini_api_key")

# Or use environment variable
# export GEMINI_API_KEY="your_key"
geospy = GeoSpy()

# Analyze an image
result = geospy.locate("path/to/image.jpg")

# Access results
for location in result["locations"]:
    print(f"{location['city']}, {location['country']}")
    print(f"Confidence: {location['confidence']}")
    print(f"Coordinates: {location['coordinates']}")
```

### Command Line

```bash
# Basic usage
geospyer --image photo.jpg

# With context and guess
geospyer --image photo.jpg --context "Beach photo" --guess "Mediterranean"

# Save results to file
geospyer --image photo.jpg --output results.json

# Verbose mode (debug logging)
geospyer --image photo.jpg --verbose

# Custom API key
geospyer --image photo.jpg --api-key YOUR_KEY

# Analyze image from URL
geospyer --image https://example.com/photo.jpg
```

## Advanced Usage

### Error Handling

```python
from geospyer import GeoSpy, APIError, ImageProcessingError, GeoSpyError

try:
    geospy = GeoSpy()
    result = geospy.locate("image.jpg")
    
except APIError as e:
    print(f"API error: {e}")
    # Handle API-specific errors
    
except ImageProcessingError as e:
    print(f"Image error: {e}")
    # Handle image loading/processing errors
    
except GeoSpyError as e:
    print(f"GeoSpy error: {e}")
    # Handle any GeoSpy-related error
```

### With Logging

```python
import logging
from geospyer import GeoSpy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use GeoSpy (will now output logs)
geospy = GeoSpy()
result = geospy.locate("image.jpg")
```

### Using Utilities

```python
from geospyer.utils import (
    validate_coordinates,
    format_location_string,
    get_google_maps_url,
    is_url
)

# Validate coordinates
if validate_coordinates(40.7128, -74.0060):
    print("Valid coordinates")

# Format location
location_str = format_location_string("New York", "NY", "USA")
# Output: "New York, NY, USA"

# Get Google Maps URL
maps_url = get_google_maps_url(40.7128, -74.0060)
# Output: "https://www.google.com/maps?q=40.7128,-74.0060"

# Check if path is URL
if is_url("https://example.com/image.jpg"):
    print("It's a URL")
```

## Configuration

### Environment Variables

```bash
# Set API key
export GEMINI_API_KEY="your_gemini_api_key"

# Windows PowerShell
$env:GEMINI_API_KEY="your_gemini_api_key"

# Windows CMD
set GEMINI_API_KEY=your_gemini_api_key
```

### Available Config (in `geospyer/config.py`)

```python
from geospyer.config import (
    GEMINI_API_URL,           # API endpoint
    DEFAULT_TEMPERATURE,       # AI temperature (0.4)
    REQUEST_TIMEOUT,          # API timeout (30s)
    IMAGE_DOWNLOAD_TIMEOUT,   # Image download timeout (10s)
    VALID_CONFIDENCE_LEVELS,  # ["High", "Medium", "Low"]
)
```

## Result Structure

```json
{
  "interpretation": "Detailed analysis of the image...",
  "locations": [
    {
      "city": "City Name",
      "state": "State/Province",
      "country": "Country Name",
      "confidence": "High|Medium|Low",
      "coordinates": {
        "latitude": 12.3456,
        "longitude": 78.9012
      },
      "explanation": "Detailed reasoning..."
    }
  ]
}
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- BMP (.bmp)

## Examples

### Example 1: Simple Analysis

```python
from geospyer import GeoSpy

geospy = GeoSpy()
result = geospy.locate("vacation.jpg")

if "error" not in result:
    top_location = result["locations"][0]
    print(f"Most likely: {top_location['city']}, {top_location['country']}")
```

### Example 2: With Context

```python
result = geospy.locate(
    image_path="beach.jpg",
    context_info="Photo taken during summer vacation",
    location_guess="Southern Europe"
)
```

### Example 3: Batch Processing

```python
import os
from pathlib import Path

geospy = GeoSpy()
image_dir = Path("./photos")

for image_path in image_dir.glob("*.jpg"):
    result = geospy.locate(str(image_path))
    if "error" not in result:
        print(f"{image_path.name}: {result['locations'][0]['city']}")
```

### Example 4: URL Analysis

```python
url = "https://example.com/landmark.jpg"
result = geospy.locate(url)
```

## Troubleshooting

### API Key Not Found

```
Error: API key not provided
```

**Solution:** Set the `GEMINI_API_KEY` environment variable or pass it to the constructor:
```python
geospy = GeoSpy(api_key="your_key")
```

### Image Not Found

```
Error: Image file not found: path/to/image.jpg
```

**Solution:** Check the file path is correct and the file exists.

### API Request Failed

```
Error: Failed to get response from Gemini API
```

**Solution:** 
- Check your internet connection
- Verify API key is valid
- Check API quota/limits
- Use `--verbose` flag for more details

### Timeout Error

```
Error: Request to Gemini API timed out
```

**Solution:**
- Check internet connection
- Try again (may be temporary)
- Increase timeout in `config.py` if needed

## Getting Help

1. Check the examples in `examples/` directory
2. Read `IMPROVEMENTS.md` for detailed documentation
3. Use `--help` flag: `geospyer --help`
4. Enable verbose logging: `geospyer --image photo.jpg --verbose`

## Common Patterns

### Save and Load Results

```python
import json

# Save
result = geospy.locate("image.jpg")
with open("result.json", "w") as f:
    json.dump(result, f, indent=2)

# Load
with open("result.json", "r") as f:
    result = json.load(f)
```

### Filter by Confidence

```python
result = geospy.locate("image.jpg")
high_confidence = [
    loc for loc in result["locations"]
    if loc["confidence"] == "High"
]
```

### Extract Coordinates

```python
result = geospy.locate("image.jpg")
coordinates = [
    (loc["coordinates"]["latitude"], loc["coordinates"]["longitude"])
    for loc in result["locations"]
]
```

## Performance Tips

1. **Reuse GeoSpy instance** - Initialize once, use many times
2. **Handle errors gracefully** - Use try/except blocks
3. **Enable logging** - For debugging and monitoring
4. **Use batch processing** - For multiple images
5. **Cache results** - Save API responses to avoid duplicate calls

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Use .gitignore** - Exclude config files with secrets
3. **Sanitize logs** - API keys are automatically sanitized in logs
4. **Validate inputs** - Check file paths and URLs before processing

## License

See LICENSE file for details.

