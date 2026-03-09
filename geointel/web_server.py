import os
import base64
import re
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from .config import AVAILABLE_MODELS
from .geointel import GeoIntel
from .exceptions import GeoIntelError
from .logger import logger


def create_app() -> Flask:
   
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent.parent / "geointel_ui_template"),
        static_folder=str(Path(__file__).parent.parent / "geointel_ui_template")
    )
    CORS(app, origins=["http://127.0.0.1:5000", "http://localhost:5000"])

    # Configure app
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

    return app


app = create_app()

MAX_CONTEXT_LENGTH = 500


@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')


ALLOWED_STATIC_EXTENSIONS = re.compile(r'\.(html|css|js|ico|png|jpg|jpeg|svg|woff|woff2|ttf|map)$', re.IGNORECASE)


@app.route('/<path:filename>')
def serve_static(filename):
    if not ALLOWED_STATIC_EXTENSIONS.search(filename):
        return jsonify({'error': 'Not found'}), 404
    return send_from_directory(app.template_folder, filename)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'GeoIntel Web API is running'})


@app.route('/api/models', methods=['GET'])
def list_models():
    return jsonify({'models': AVAILABLE_MODELS})


@app.route('/api/analyze', methods=['POST'])
def analyze_image():
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
        model = data.get('model')
        context_raw = data.get('context')
        guess_raw = data.get('guess')
        context_info = str(context_raw)[:MAX_CONTEXT_LENGTH] if context_raw else None
        location_guess = str(guess_raw)[:MAX_CONTEXT_LENGTH] if guess_raw else None

        # Validate required fields
        if not image_data:
            return jsonify({
                'error': 'Image data required',
                'details': 'Provide either base64 image data or image URL'
            }), 400

        if not api_key:
            return jsonify({
                'error': 'API key required',
                'details': 'Gemini API key must be provided'
            }), 400

        logger.info("Processing image analysis request")

        # Determine if image_data is URL or base64
        if image_data.startswith(('http://', 'https://')):
            image_path = image_data

            # Initialize GeoIntel with provided API key and model
            geointel = GeoIntel(api_key=api_key, model=model)

            # Perform analysis
            result = geointel.locate(
                image_path=image_path,
                context_info=context_info,
                location_guess=location_guess
            )
        else:
            # Save base64 image to temporary file
            try:
                # Remove data URI prefix if present and detect format
                suffix = '.jpg'
                if ',' in image_data:
                    header, image_data = image_data.split(',', 1)
                    # Extract MIME type from data URI (e.g. data:image/png;base64)
                    if 'image/png' in header:
                        suffix = '.png'
                    elif 'image/webp' in header:
                        suffix = '.webp'
                    elif 'image/gif' in header:
                        suffix = '.gif'

                image_bytes = base64.b64decode(image_data)

            except Exception as e:
                logger.error(f"Failed to process image data: {e}")
                return jsonify({
                    'error': 'Invalid image data',
                    'details': str(e)
                }), 400

            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                    dir=app.config['UPLOAD_FOLDER']
                ) as f:
                    f.write(image_bytes)
                    temp_path = f.name
                logger.info(f"Saved uploaded image to: {temp_path}")

                image_path = temp_path

                # Initialize GeoIntel with provided API key and model
                geointel = GeoIntel(api_key=api_key, model=model)

                # Perform analysis
                result = geointel.locate(
                    image_path=image_path,
                    context_info=context_info,
                    location_guess=location_guess
                )
            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                        logger.info(f"Cleaned up temporary file: {temp_path}")
                    except OSError as e:
                        logger.warning(f"Failed to clean up temporary file {temp_path}: {e}")

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


@app.route('/api/reverse-image-search', methods=['POST'])
def reverse_image_search():
    try:
        data = request.get_json()

        if not data or 'image' not in data:
            return jsonify({
                'error': 'Image data required'
            }), 400

        # For Google reverse image search, we'll return the URL pattern
        # The client can open this in a new tab
        # Google Images supports searching by uploading, but we'll provide
        # the lens URL pattern that can be used

        return jsonify({
            'search_url': 'https://lens.google.com/uploadbyurl',
            'message': 'Upload the image to Google Lens for reverse image search'
        })

    except Exception as e:
        logger.error(f"Error in reverse image search: {e}")
        return jsonify({
            'error': 'Failed to generate search URL',
            'details': str(e)
        }), 500


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
    run_server(debug=False)
