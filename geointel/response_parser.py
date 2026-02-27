import json
import re
from typing import Dict, Any, Optional


def parse_geolocation_response(api_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and normalize the Gemini API response into the standard geolocation format.
    
    Args:
        api_response: The raw JSON response from the Gemini API
        
    Returns:
        A normalized dictionary with interpretation and locations
        
    Raises:
        ValueError: If the response structure is missing required fields
        json.JSONDecodeError: If the response cannot be parsed as valid JSON
    """
    # Validate response structure
    if "candidates" not in api_response:
        raise ValueError("API response missing 'candidates' field")
    
    candidates = api_response["candidates"]
    if not candidates or not isinstance(candidates, list):
        raise ValueError("API response 'candidates' is empty or not a list")
    
    candidate = candidates[0]
    if "content" not in candidate:
        raise ValueError("Candidate response missing 'content' field")
    
    content = candidate["content"]
    if "parts" not in content:
        raise ValueError("Candidate content missing 'parts' field")
    
    parts = content["parts"]
    if not parts or not isinstance(parts, list):
        raise ValueError("Candidate content 'parts' is empty or not a list")
    
    part = parts[0]
    if "text" not in part:
        raise ValueError("Candidate part missing 'text' field")
    
    raw_text = part["text"]
    if not raw_text or not isinstance(raw_text, str):
        raise ValueError("Candidate part 'text' is empty or not a string")
    
    # Strip any markdown code block (case-insensitive, any language tag)
    json_string = re.sub(r'```[\w]*\n?', '', raw_text, flags=re.IGNORECASE).strip()
    
    # Parse the JSON string
    parsed_result = json.loads(json_string)
    
    # Handle potential single location format where the location is not in an array
    if "city" in parsed_result and "locations" not in parsed_result:
        return {
            "interpretation": parsed_result.get("interpretation", ""),
            "locations": [_normalize_location(parsed_result)]
        }
    
    # Validate top-level structure
    if not isinstance(parsed_result.get("locations"), list):
        raise ValueError("Parsed response missing 'locations' list")
    
    parsed_result.setdefault("interpretation", "")
    parsed_result["locations"] = [_normalize_location(loc) for loc in parsed_result["locations"]]
    
    return parsed_result


def _normalize_location(location: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure a location dict has all required fields with safe defaults."""
    coords = location.get("coordinates")
    if not isinstance(coords, dict):
        coords = {"latitude": 0, "longitude": 0}
    else:
        coords.setdefault("latitude", 0)
        coords.setdefault("longitude", 0)
    
    return {
        "country": location.get("country", ""),
        "state": location.get("state", ""),
        "city": location.get("city", ""),
        "confidence": location.get("confidence", "Medium"),
        "coordinates": coords,
        "explanation": location.get("explanation", ""),
    }
