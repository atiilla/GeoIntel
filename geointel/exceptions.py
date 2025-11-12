
class GeoIntelError(Exception):
    pass


class ImageProcessingError(GeoIntelError):
    pass


class APIError(GeoIntelError):
    pass


class APIKeyError(GeoIntelError):
    pass


class ResponseParsingError(GeoIntelError):
    pass


class InvalidImageError(GeoIntelError):
    pass


class NetworkError(GeoIntelError):
    pass
