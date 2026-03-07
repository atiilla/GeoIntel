import os
import base64
import binascii
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from .geointel import GeoIntel
from .exceptions import GeoIntelError, InvalidImageError
from .image_processor import ImageProcessor
from .logger import logger


def create_app() -> Flask:
   
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent.parent / "geointel_ui_template"),
        static_folder=str(Path(__file__).parent.parent / "geointel_ui_template")
    )
    CORS(app)

    # Configure app
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

    return app


app = create_app()


def decode_uploaded_image(
    image_data: str,
    mime_type: Optional[str] = None
) -> Tuple[str, bytes]:
    if not isinstance(image_data, str):
        raise InvalidImageError("Image data must be a base64 string")

    if image_data.startswith(("http://", "https://")):
        raise InvalidImageError(
            "Image URLs are not supported in web mode. Upload the image file directly."
        )

    detected_mime_type, encoded_image_data = ImageProcessor.parse_data_url(image_data)
    normalized_mime_type = detected_mime_type or ImageProcessor.normalize_mime_type(mime_type)
    if not normalized_mime_type:
        raise InvalidImageError(
            "Unsupported image format. Upload a JPEG, PNG, WebP, or GIF image."
        )

    try:
        image_bytes = base64.b64decode(encoded_image_data, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise InvalidImageError(f"Invalid image data: {exc}") from exc

    return normalized_mime_type, image_bytes


@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.template_folder, filename)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'GeoIntel Web API is running'})


@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    temp_file_path = None
    try:
        # Parse request data
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'No data provided',
                'details': 'Request body must be JSON'
            }), 400

        # Extract parameters
        image_data = data.get('image')
        api_key = data.get('api_key')
        context_info = data.get('context')
        location_guess = data.get('guess')
        mime_type = data.get('mime_type')

        # Validate required fields
        if not image_data:
            return jsonify({
                'error': 'Image data required',
                'details': 'Provide a base64-encoded image upload'
            }), 400

        if not api_key:
            return jsonify({
                'error': 'API key required',
                'details': 'Gemini API key must be provided'
            }), 400

        logger.info("Processing image analysis request")

        upload_mime_type, image_bytes = decode_uploaded_image(
            image_data=image_data,
            mime_type=mime_type,
        )

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=ImageProcessor.get_file_suffix(upload_mime_type),
            dir=app.config['UPLOAD_FOLDER']
        )
        temp_file.write(image_bytes)
        temp_file.close()

        temp_file_path = temp_file.name
        logger.info(f"Saved uploaded image to: {temp_file_path}")

        # Initialize GeoIntel with provided API key
        geointel = GeoIntel(api_key=api_key)

        # Perform analysis
        result = geointel.locate(
            image_path=temp_file_path,
            context_info=context_info,
            location_guess=location_guess,
            mime_type_override=upload_mime_type,
        )

        # Check for errors in result
        if 'error' in result:
            return jsonify(result), 400

        logger.info("Image analysis completed successfully")
        return jsonify(result)

    except GeoIntelError as e:
        logger.error(f"GeoIntel error: {e}")
        return jsonify({
            'error': str(e),
            'details': type(e).__name__
        }), 400

    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500
    finally:
        if temp_file_path:
            try:
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except OSError as e:
                logger.warning(f"Failed to clean up temporary file: {e}")


@app.errorhandler(413)
def file_too_large(e):
    return jsonify({
        'error': 'File too large',
        'details': 'Maximum file size is 16MB'
    }), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Not found',
        'details': 'The requested resource was not found'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'error': 'Internal server error',
        'details': 'An unexpected error occurred'
    }), 500


def run_server(host: str = '127.0.0.1', port: int = 5000, debug: bool = False) -> None:
    logger.info(f"Starting GeoIntel web server on http://{host}:{port}")
    print(f"\n{'='*60}")
    print(f"  GeoIntel Web Interface")
    print(f"{'='*60}")
    print(f"  Server running at: http://{host}:{port}")
    print(f"  Press Ctrl+C to stop the server")
    print(f"{'='*60}\n")

    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\n\nServer stopped.")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        print(f"\nError starting server: {e}")
        raise


if __name__ == '__main__':
    run_server(debug=True)
