import os
import base64
import tempfile
from pathlib import Path
from typing import Optional
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

from .geointel import GeoIntel
from .exceptions import GeoIntelError
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
        else:
            # Save base64 image to temporary file
            try:
                # Remove data URI prefix if present
                if ',' in image_data:
                    image_data = image_data.split(',', 1)[1]

                image_bytes = base64.b64decode(image_data)

                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix='.jpg',
                    dir=app.config['UPLOAD_FOLDER']
                )
                temp_file.write(image_bytes)
                temp_file.close()

                image_path = temp_file.name
                logger.info(f"Saved uploaded image to: {image_path}")

            except Exception as e:
                logger.error(f"Failed to process image data: {e}")
                return jsonify({
                    'error': 'Invalid image data',
                    'details': str(e)
                }), 400

        # Initialize GeoIntel with provided API key
        geointel = GeoIntel(api_key=api_key)

        # Perform analysis
        result = geointel.locate(
            image_path=image_path,
            context_info=context_info,
            location_guess=location_guess
        )

        # Clean up temporary file if created
        if not image_data.startswith(('http://', 'https://')):
            try:
                os.unlink(image_path)
                logger.info(f"Cleaned up temporary file: {image_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")

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
    run_server(debug=True)
