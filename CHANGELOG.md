# Changelog

## [Unreleased] - Code Quality Improvements

### Added
- **New Modules:**
  - `geospyer/config.py` - Centralized configuration and constants
  - `geospyer/prompts.py` - AI prompt template management
  - `geospyer/exceptions.py` - Custom exception classes
  - `geospyer/utils.py` - Utility helper functions
  - `examples/advanced_usage.py` - Comprehensive usage examples

- **Features:**
  - Professional logging system with configurable levels
  - Automatic MIME type detection for images
  - Support for multiple image formats (JPEG, PNG, GIF, WebP, BMP)
  - API key sanitization in logs for security
  - Custom exception types for better error handling
  - `--verbose` flag for CLI debug output
  - Response validation and normalization
  - Timeout handling for API requests

- **Documentation:**
  - Comprehensive docstrings for all functions and classes
  - Type hints throughout the codebase
  - Module-level documentation
  - `IMPROVEMENTS.md` detailing all changes
  - Advanced usage examples

### Changed
- Refactored prompt text into separate module
- Improved error messages with more context
- Better API response parsing with validation
- Enhanced CLI output formatting with color constants
- Reorganized code for better separation of concerns

### Improved
- **Error Handling:**
  - Custom exception hierarchy
  - Proper exception chaining
  - Granular error types (APIError, ImageProcessingError, ValidationError)
  - Better error messages with context

- **Code Quality:**
  - Added type hints to all functions
  - Improved docstrings
  - Reduced code duplication
  - Better naming conventions
  - Removed magic numbers and strings

- **Logging:**
  - Replaced print statements with proper logging
  - Structured log messages
  - Debug and info level separation
  - Integration-ready logging

- **Configuration:**
  - Centralized constants
  - Easy-to-modify settings
  - Environment variable support
  - Configurable timeouts

### Fixed
- Image MIME type now correctly detected from file extension and headers
- Better handling of malformed API responses
- Improved URL vs local file path detection
- Better coordinate validation

### Security
- API keys are now sanitized in logs
- Better validation of API key presence
- Secure error messages that don't leak sensitive data

### Developer Experience
- Better IDE autocomplete with type hints
- Easier debugging with logging
- Clear error messages
- Modular code for easier testing
- Well-organized file structure

## Backward Compatibility

✅ **100% Backward Compatible** - All existing code continues to work without changes.

```python
# This still works exactly as before
from geospyer import GeoSpy
geospy = GeoSpy(api_key="your_key")
result = geospy.locate("image.jpg")
```

## Migration Notes

No migration needed! To use new features:

1. **Enable logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

2. **Use specific exceptions:**
   ```python
   from geospyer import APIError, ImageProcessingError
   try:
       result = geospy.locate(image)
   except APIError as e:
       # Handle API-specific errors
       pass
   ```

3. **Use verbose CLI:**
   ```bash
   geospyer --image photo.jpg --verbose
   ```

