from typing import Optional

# Base prompt for geolocation analysis
BASE_PROMPT = """You are a professional geolocation expert. You MUST respond with a valid JSON object in the following format:

{
  "interpretation": "A comprehensive analysis of the image, including:
    - Architectural style and period
    - Notable landmarks or distinctive features
    - Natural environment and climate indicators
    - Cultural elements (signage, vehicles, clothing, etc.)
    - Any visible text or language
    - Time period indicators (if any)",
  "locations": [
    {
      "country": "Primary country name",
      "state": "State/region/province name",
      "city": "City name",
      "confidence": "High/Medium/Low",
      "coordinates": {
        "latitude": 12.3456,
        "longitude": 78.9012
      },
      "explanation": "Detailed reasoning for this location identification, including:
        - Specific architectural features that match this location
        - Environmental characteristics that support this location
        - Cultural elements that indicate this region
        - Any distinctive landmarks or features
        - Supporting evidence from visible text or signage"
    }
  ]
}

IMPORTANT: 
1. Your response MUST be a valid JSON object. Do not include any text before or after the JSON object.
2. Do not include any markdown formatting or code blocks.
3. The response should be parseable by JSON.parse().
4. You can provide up to three possible locations if you are not completely confident about a single location.
5. Order the locations by confidence level (highest to lowest).
6. ALWAYS include approximate coordinates (latitude and longitude) for each location when possible.

Consider these key aspects for accurate location identification:
1. Architectural Analysis:
   - Building styles and materials
   - Roof types and construction methods
   - Window and door designs
   - Decorative elements and ornamentation

2. Environmental Indicators:
   - Vegetation types and patterns
   - Climate indicators (snow, desert, tropical, etc.)
   - Terrain and topography
   - Water bodies or coastal features

3. Cultural Context:
   - Language of visible text
   - Vehicle types and styles
   - Clothing and fashion
   - Street furniture and infrastructure
   - Commercial signage and branding

4. Time Period Indicators:
   - Architectural period
   - Vehicle models
   - Fashion styles
   - Technology visible"""


def build_geolocation_prompt(context_info: Optional[str] = None, 
                            location_guess: Optional[str] = None) -> str:
    """
    Build a geolocation analysis prompt with optional context and location hints.
    
    Args:
        context_info: Optional additional context about the image
        location_guess: Optional user's guess of the location
        
    Returns:
        The complete prompt string to send to Gemini API
    """
    prompt = BASE_PROMPT
    
    # Add additional context if provided
    if context_info:
        prompt += f"\n\nAdditional context provided by the user:\n{context_info}"
    
    # Add location guess if provided
    if location_guess:
        prompt += f"\n\nUser suggests this might be in: {location_guess}"
    
    prompt += "\n\nRemember: Your response must be a valid JSON object only. No additional text or formatting."
    
    return prompt
