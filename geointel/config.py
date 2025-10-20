"""Configuration constants and settings for GeoIntel."""

# API Configuration
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-lite-001:generateContent"
DEFAULT_API_KEY_ENV = "GEMINI_API_KEY"

# Generation Configuration
DEFAULT_TEMPERATURE = 0.4
DEFAULT_TOP_K = 32
DEFAULT_TOP_P = 1
DEFAULT_MAX_OUTPUT_TOKENS = 2048

# Request Configuration
REQUEST_TIMEOUT = 30  # seconds
IMAGE_DOWNLOAD_TIMEOUT = 10  # seconds

# Confidence Levels
CONFIDENCE_HIGH = "High"
CONFIDENCE_MEDIUM = "Medium"
CONFIDENCE_LOW = "Low"
VALID_CONFIDENCE_LEVELS = [CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW]

# MIME Types
MIME_TYPES = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.bmp': 'image/bmp',
}
DEFAULT_MIME_TYPE = 'image/jpeg'

# HTTP Headers
API_HEADERS = {
    "content-type": "application/json",
    "User-Agent": "GeoIntel/1.0 (Python HTTP Client)"
}

# Color Codes for CLI
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

