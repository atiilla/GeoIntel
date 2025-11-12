import json
from typing import Any, Dict

from .config import CONFIDENCE_LEVELS
from .exceptions import ResponseParsingError
from .logger import logger


class ResponseParser:

    @staticmethod
    def clean_json_string(text: str) -> str:
      
        return text.replace("```json", "").replace("```", "").strip()

    @staticmethod
    def validate_location(location: Dict[str, Any]) -> bool:
     
        required_fields = ["country", "city", "confidence"]
        return all(field in location for field in required_fields)

    @staticmethod
    def normalize_confidence(confidence: str) -> str:
       
        confidence = confidence.strip().capitalize()
        return confidence if confidence in CONFIDENCE_LEVELS else "Medium"

    @staticmethod
    def normalize_location(location: Dict[str, Any]) -> Dict[str, Any]:
       
        return {
            "country": location.get("country", "Unknown"),
            "state": location.get("state", ""),
            "city": location.get("city", "Unknown"),
            "confidence": ResponseParser.normalize_confidence(
                location.get("confidence", "Medium")
            ),
            "coordinates": location.get("coordinates", {
                "latitude": 0.0,
                "longitude": 0.0
            }),
            "explanation": location.get("explanation", "")
        }

    @staticmethod
    def _attempt_json_repair(raw_response: str) -> Dict[str, Any]:
        """
        Attempt to repair truncated JSON by closing incomplete structures.
        """
        json_string = ResponseParser.clean_json_string(raw_response)
        
        # Try to find where the JSON was truncated and attempt basic repairs
        if json_string.endswith('"'):
            # If it ends with a quote, try adding closing braces
            for closing in ['"}]}', '"}]', '"}', '}]}', '}]', '}']:
                try:
                    repaired = json_string + closing
                    data = json.loads(repaired)
                    # Validate the repaired data has required structure
                    if "locations" in data and data["locations"]:
                        return {
                            "interpretation": data.get("interpretation", "Analysis was truncated"),
                            "locations": [
                                ResponseParser.normalize_location(loc)
                                for loc in data["locations"]
                                if ResponseParser.validate_location(loc)
                            ]
                        }
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # Try to extract partial location data even if incomplete
        try:
            # Look for partial location data patterns
            import re
            
            # Extract interpretation if available
            interp_match = re.search(r'"interpretation":\s*"([^"]*)"', json_string)
            interpretation = interp_match.group(1) if interp_match else "Analysis was truncated"
            
            # Extract any complete location objects
            location_pattern = r'"country":\s*"([^"]*)"[^}]*"city":\s*"([^"]*)"[^}]*"confidence":\s*"([^"]*)"'
            locations = []
            
            for match in re.finditer(location_pattern, json_string):
                country, city, confidence = match.groups()
                locations.append({
                    "country": country,
                    "city": city,
                    "state": "",
                    "confidence": ResponseParser.normalize_confidence(confidence),
                    "coordinates": {"latitude": 0.0, "longitude": 0.0},
                    "explanation": "Location extracted from truncated response"
                })
            
            if locations:
                return {
                    "interpretation": interpretation,
                    "locations": locations
                }
        except Exception:
            pass
        
        return None

    @staticmethod
    def parse_legacy_format(data: Dict[str, Any]) -> Dict[str, Any]:
      
        logger.debug("Parsing legacy format response")
        return {
            "interpretation": data.get("interpretation", ""),
            "locations": [ResponseParser.normalize_location(data)]
        }

    @classmethod
    def parse_response(cls, raw_response: str) -> Dict[str, Any]:
       
        try:
            # Clean and parse JSON
            json_string = cls.clean_json_string(raw_response)
            logger.debug("Parsing JSON response")
            data = json.loads(json_string)

            # Check for legacy format (single location not in array)
            if "city" in data and "locations" not in data:
                return cls.parse_legacy_format(data)

            # Validate standard format
            if "locations" not in data:
                raise ResponseParsingError("Response missing 'locations' field")

            # Normalize locations
            normalized_locations = [
                cls.normalize_location(loc)
                for loc in data.get("locations", [])
                if cls.validate_location(loc)
            ]

            if not normalized_locations:
                raise ResponseParsingError("No valid locations found in response")

            return {
                "interpretation": data.get("interpretation", ""),
                "locations": normalized_locations
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            
            # Check if this might be a truncated response
            if "Unterminated string" in str(e) or "Expecting" in str(e):
                logger.error("Response appears to be truncated. Attempting to repair JSON...")
                
                # Try to repair truncated JSON
                try:
                    repaired_json = cls._attempt_json_repair(raw_response)
                    if repaired_json:
                        logger.info("Successfully repaired truncated JSON")
                        return repaired_json
                except Exception as repair_error:
                    logger.error(f"JSON repair failed: {repair_error}")
                
                logger.error("Consider increasing MAX_OUTPUT_TOKENS.")
                raise ResponseParsingError(
                    f"API response was truncated (incomplete JSON). "
                    f"The response may have exceeded the token limit. "
                    f"Original error: {e}"
                )
            else:
                raise ResponseParsingError(
                    f"Failed to parse API response as JSON: {e}"
                )
        except Exception as e:
            logger.error(f"Unexpected error during parsing: {e}")
            raise ResponseParsingError(f"Unexpected parsing error: {e}")
