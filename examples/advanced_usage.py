#!/usr/bin/env python3
"""
Advanced example showing best practices for using GeoIntel as a library.

This example demonstrates:
- Proper error handling
- Logging configuration
- Using custom exceptions
- Working with multiple images
- Batch processing
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from geointel import GeoIntel, GeoIntelError, APIError, ImageProcessingError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def analyze_single_image(geointel: GeoIntel, image_path: str, 
                        context: str = None, guess: str = None) -> Dict[str, Any]:
    """
    Analyze a single image with proper error handling.
    
    Args:
        geointel: GeoIntel instance
        image_path: Path to image or URL
        context: Optional context information
        guess: Optional location guess
        
    Returns:
        Analysis results or error information
    """
    try:
        logger.info(f"Analyzing: {image_path}")
        result = geointel.locate(
            image_path=image_path,
            context_info=context,
            location_guess=guess
        )
        
        if "error" in result:
            logger.error(f"Analysis failed: {result['error']}")
            return result
        
        # Log summary
        locations = result.get("locations", [])
        if locations:
            top_location = locations[0]
            logger.info(
                f"Top match: {top_location.get('city')}, "
                f"{top_location.get('country')} "
                f"(Confidence: {top_location.get('confidence')})"
            )
        
        return result
        
    except ImageProcessingError as e:
        logger.error(f"Image processing error: {e}")
        return {"error": str(e)}
    except APIError as e:
        logger.error(f"API error: {e}")
        return {"error": str(e)}
    except GeoIntelError as e:
        logger.error(f"GeoIntel error: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.exception("Unexpected error")
        return {"error": str(e)}


def batch_analyze_images(geointel: GeoIntel, image_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Analyze multiple images in batch.
    
    Args:
        geointel: GeoIntel instance
        image_paths: List of image paths or URLs
        
    Returns:
        List of analysis results
    """
    results = []
    
    for i, image_path in enumerate(image_paths, 1):
        logger.info(f"Processing image {i}/{len(image_paths)}")
        result = analyze_single_image(geointel, image_path)
        results.append({
            "image_path": image_path,
            "result": result
        })
    
    return results


def save_results(results: Dict[str, Any], output_path: str) -> bool:
    """
    Save results to a JSON file.
    
    Args:
        results: Analysis results
        output_path: Path to save file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {output_path}")
        return True
    except IOError as e:
        logger.error(f"Failed to save results: {e}")
        return False


def main():
    """Main example function."""
    # Initialize GeoIntel with API key from environment
    try:
        geointel = GeoIntel()  # Will use GEMINI_API_KEY from environment
        logger.info("GeoIntel initialized successfully")
    except ValueError as e:
        logger.error(f"Failed to initialize: {e}")
        logger.info("Please set GEMINI_API_KEY environment variable")
        return
    
    # Example 1: Analyze a single image
    logger.info("=" * 50)
    logger.info("Example 1: Single Image Analysis")
    logger.info("=" * 50)
    
    image_path = os.path.join(Path(__file__).parent.parent, "kule.jpg")
    
    if os.path.exists(image_path):
        result = analyze_single_image(
            geointel,
            image_path,
            context="Historic tower in an urban setting",
            guess="Turkey"
        )
        
        if "error" not in result:
            # Display results
            print("\nAnalysis Results:")
            print(f"Interpretation: {result.get('interpretation', 'N/A')[:100]}...")
            print(f"\nTop Locations:")
            for i, location in enumerate(result.get('locations', [])[:3], 1):
                print(f"\n{i}. {location.get('city')}, {location.get('country')}")
                print(f"   Confidence: {location.get('confidence')}")
                coords = location.get('coordinates', {})
                print(f"   Coordinates: {coords.get('latitude')}, {coords.get('longitude')}")
            
            # Save results
            save_results(result, "single_image_result.json")
    else:
        logger.warning(f"Image not found: {image_path}")
    
    # Example 2: Analyze from URL
    logger.info("\n" + "=" * 50)
    logger.info("Example 2: URL Image Analysis")
    logger.info("=" * 50)
    
    url = "https://example.com/image.jpg"  # Replace with actual URL
    # result = analyze_single_image(geointel, url)
    logger.info(f"To analyze from URL, use: analyze_single_image(geointel, '{url}')")
    
    # Example 3: Batch processing
    logger.info("\n" + "=" * 50)
    logger.info("Example 3: Batch Processing")
    logger.info("=" * 50)
    
    # Collect all images from a directory
    # image_dir = Path("./images")
    # if image_dir.exists():
    #     image_paths = [str(p) for p in image_dir.glob("*.jpg")]
    #     batch_results = batch_analyze_images(geointel, image_paths)
    #     save_results({"batch_results": batch_results}, "batch_results.json")
    
    logger.info("Example completed!")


if __name__ == "__main__":
    main()

