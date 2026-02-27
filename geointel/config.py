from typing import Final

# API Configuration
GEMINI_API_BASE_URL: Final[str] = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_MODEL: Final[str] = "gemini-3-flash"
API_TIMEOUT: Final[int] = 30

# Generation Configuration
DEFAULT_TEMPERATURE: Final[float] = 0.3  # Lower for more consistent/accurate location predictions
DEFAULT_TOP_K: Final[int] = 40
DEFAULT_TOP_P: Final[float] = 0.95
MAX_OUTPUT_TOKENS: Final[int] = 16384

# Image Processing
SUPPORTED_IMAGE_FORMATS: Final[tuple] = ("jpeg", "jpg", "png", "webp", "gif")
DEFAULT_MIME_TYPE: Final[str] = "image/jpeg"
IMAGE_DOWNLOAD_TIMEOUT: Final[int] = 10

# Response Configuration
CONFIDENCE_LEVELS: Final[tuple] = ("High", "Medium", "Low")

# Environment Variables
ENV_API_KEY: Final[str] = "GEMINI_API_KEY"
