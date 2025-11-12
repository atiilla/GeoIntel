import {
  GeoIntelResponse,
  GeoIntelError as IGeoIntelError,
  GeoIntelRequest,
  GeminiRequestPayload,
  GeminiResponse,
  Location,
  ConfidenceLevel,
  GEOINTEL_CONFIG
} from '../types/geointel';

export class GeoIntelError extends Error {
  constructor(public message: string, public details?: string) {
    super(message);
    this.name = 'GeoIntelError';
  }
}

export class APIError extends GeoIntelError {
  constructor(message: string, details?: string) {
    super(message, details);
    this.name = 'APIError';
  }
}

export class APIKeyError extends GeoIntelError {
  constructor(message: string, details?: string) {
    super(message, details);
    this.name = 'APIKeyError';
  }
}

export class ImageProcessingError extends GeoIntelError {
  constructor(message: string, details?: string) {
    super(message, details);
    this.name = 'ImageProcessingError';
  }
}

export class NetworkError extends GeoIntelError {
  constructor(message: string, details?: string) {
    super(message, details);
    this.name = 'NetworkError';
  }
}

export class ResponseParsingError extends GeoIntelError {
  constructor(message: string, details?: string) {
    super(message, details);
    this.name = 'ResponseParsingError';
  }
}

export class ImageProcessor {
  static validateImageFormat(file: File): void {
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (!extension || !GEOINTEL_CONFIG.SUPPORTED_IMAGE_FORMATS.includes(extension as any)) {
      throw new ImageProcessingError(
        `Unsupported image format: ${extension}. Supported formats: ${GEOINTEL_CONFIG.SUPPORTED_IMAGE_FORMATS.join(', ')}`
      );
    }
  }

  static async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // Remove data URL prefix (e.g., "data:image/jpeg;base64,")
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = () => reject(new ImageProcessingError('Failed to read image file'));
      reader.readAsDataURL(file);
    });
  }

  static async processImage(file: File): Promise<string> {
    this.validateImageFormat(file);
    return await this.fileToBase64(file);
  }

  static getMimeType(file: File): string {
    return file.type || GEOINTEL_CONFIG.DEFAULT_MIME_TYPE;
  }
}

export class ResponseParser {
  static cleanJsonString(text: string): string {
    return text.replace(/```json/g, '').replace(/```/g, '').trim();
  }

  static validateLocation(location: any): boolean {
    const requiredFields = ['country', 'city', 'confidence'];
    return requiredFields.every(field => field in location);
  }

  static normalizeConfidence(confidence: string): ConfidenceLevel {
    const normalized = confidence.trim();
    const capitalized = normalized.charAt(0).toUpperCase() + normalized.slice(1).toLowerCase();
    return GEOINTEL_CONFIG.CONFIDENCE_LEVELS.includes(capitalized as ConfidenceLevel) 
      ? capitalized as ConfidenceLevel 
      : 'Medium';
  }

  static normalizeLocation(location: any): Location {
    return {
      country: location.country || 'Unknown',
      state: location.state || '',
      city: location.city || 'Unknown',
      confidence: this.normalizeConfidence(location.confidence || 'Medium'),
      coordinates: location.coordinates || { latitude: 0.0, longitude: 0.0 },
      explanation: location.explanation || ''
    };
  }

  static parseResponse(rawResponse: string): GeoIntelResponse {
    try {
      const jsonString = this.cleanJsonString(rawResponse);
      const data = JSON.parse(jsonString);

      // Check for legacy format (single location not in array)
      if ('city' in data && !('locations' in data)) {
        return {
          interpretation: data.interpretation || '',
          locations: [this.normalizeLocation(data)]
        };
      }

      // Validate standard format
      if (!('locations' in data)) {
        throw new ResponseParsingError("Response missing 'locations' field");
      }

      // Normalize locations
      const normalizedLocations = data.locations
        .filter((loc: any) => this.validateLocation(loc))
        .map((loc: any) => this.normalizeLocation(loc));

      if (normalizedLocations.length === 0) {
        throw new ResponseParsingError('No valid locations found in response');
      }

      return {
        interpretation: data.interpretation || '',
        locations: normalizedLocations
      };

    } catch (error) {
      if (error instanceof SyntaxError) {
        throw new ResponseParsingError(`Failed to parse API response as JSON: ${error.message}`);
      }
      throw error;
    }
  }
}

export class GeminiClient {
  private apiKey: string;

  constructor(apiKey?: string) {
    this.apiKey = apiKey || '';
    if (!this.apiKey || this.apiKey === 'your_api_key_here') {
      throw new APIKeyError(
        'API key required. Please configure your Gemini API key in the settings.'
      );
    }
  }

  private buildEndpointUrl(): string {
    return `${GEOINTEL_CONFIG.GEMINI_API_BASE_URL}/${GEOINTEL_CONFIG.GEMINI_MODEL}:generateContent?key=${this.apiKey}`;
  }

  private buildRequestPayload(prompt: string, imageBase64: string, mimeType: string): GeminiRequestPayload {
    return {
      contents: [
        {
          parts: [
            { text: prompt },
            {
              inline_data: {
                mime_type: mimeType,
                data: imageBase64
              }
            }
          ]
        }
      ],
      generationConfig: {
        temperature: GEOINTEL_CONFIG.DEFAULT_TEMPERATURE,
        topK: GEOINTEL_CONFIG.DEFAULT_TOP_K,
        topP: GEOINTEL_CONFIG.DEFAULT_TOP_P,
        maxOutputTokens: GEOINTEL_CONFIG.MAX_OUTPUT_TOKENS
      }
    };
  }

  private extractResponseText(responseData: GeminiResponse): string {
    try {
      if (!responseData.candidates || responseData.candidates.length === 0) {
        throw new APIError('No candidates in API response');
      }

      const candidate = responseData.candidates[0];
      if (!candidate.content || !candidate.content.parts || candidate.content.parts.length === 0) {
        throw new APIError('No content parts in API response');
      }

      const part = candidate.content.parts[0];
      if (!part.text) {
        throw new APIError('No text in content part');
      }

      return part.text;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(`Invalid API response structure: ${error}`);
    }
  }

  async generateContent(prompt: string, imageBase64: string, mimeType: string = GEOINTEL_CONFIG.DEFAULT_MIME_TYPE): Promise<string> {
    const endpointUrl = this.buildEndpointUrl();
    const payload = this.buildRequestPayload(prompt, imageBase64, mimeType);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), GEOINTEL_CONFIG.API_TIMEOUT);

      const response = await fetch(endpointUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new APIError(`API request failed with status ${response.status}: ${errorText}`);
      }

      const responseData: GeminiResponse = await response.json();
      return this.extractResponseText(responseData);

    } catch (error: unknown) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw new NetworkError('API request timed out');
      }
      if (error instanceof APIError || error instanceof NetworkError) {
        throw error;
      }
      throw new NetworkError(`API request failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}

export function getGeolocationPrompt(contextInfo?: string, locationGuess?: string): string {
  let basePrompt = `You are a professional geolocation expert specializing in extremely detailed, pixel-level visual analysis.
You MUST respond with a valid JSON object in the following format:

{
  "interpretation": "A comprehensive, pixel-level analysis of the image, including: architectural style and period, notable landmarks or distinctive features, micro and macro environmental indicators (mountain shapes, vegetation density, soil color, etc.), natural environment and climate indicators, cultural elements (signage, vehicles, clothing, etc.), any visible text or language, time period indicators (if any), small visual cues (shadows, reflections, terrain contours, horizon lines, distant silhouettes)",
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
      "explanation": "Detailed reasoning for this location identification, including: pixel-level feature matching (e.g., mountain profiles, vegetation tone, soil texture, cloud pattern), architectural, environmental, and cultural consistencies, evidence from micro-details such as reflections, terrain gradients, or distant objects, contextual validation with geographic and climatic compatibility, supporting evidence from visible text or signage"
    }
  ]
}

IMPORTANT:
1. Your response MUST be a valid JSON object only. Do not include any text before or after the JSON.
2. Do not include any markdown formatting or code blocks.
3. The response should be parseable by JSON.parse().
4. You can provide up to three possible locations if uncertain.
5. Order the locations by confidence level (highest to lowest).
6. ALWAYS include approximate coordinates (latitude and longitude) for each location.

For maximum accuracy, perform a pixel-level inspection:
1. Analyze every visible pixel, including background, reflections, and low-contrast regions.
2. Consider faint background shapes (mountains, skylines, vegetation gradients, etc.).
3. Compare color gradients, shadow directions, and atmospheric haze to infer climate and region.
4. Evaluate micro-patterns: terrain texture, road markings, signage fonts, vegetation structure.
5. Note any artifacts of culture, climate, or architecture — even if subtle or partially visible.

Your analysis should balance **pixel-level visual evidence** with **contextual geographic reasoning** for the most accurate match possible.`;

  if (contextInfo) {
    basePrompt += `\n\nAdditional context provided by the user:\n${contextInfo}`;
  }

  if (locationGuess) {
    basePrompt += `\n\nUser suggests this might be in: ${locationGuess}`;
  }

  basePrompt += '\n\nRemember: Your response must be a valid JSON object only. No additional text or formatting. Keep explanations concise but detailed (aim for 2-3 sentences per explanation).';

  return basePrompt;
}

export class GeoIntel {
  private apiClient: GeminiClient;

  constructor(apiKey?: string) {
    this.apiClient = new GeminiClient(apiKey);
  }

  async locate(
    file: File,
    contextInfo?: string,
    locationGuess?: string
  ): Promise<GeoIntelResponse> {
    try {
      // Process image
      const imageBase64 = await ImageProcessor.processImage(file);
      const mimeType = ImageProcessor.getMimeType(file);

      // Generate prompt
      const prompt = getGeolocationPrompt(contextInfo, locationGuess);

      // Call API
      const rawResponse = await this.apiClient.generateContent(prompt, imageBase64, mimeType);

      // Parse response
      const result = ResponseParser.parseResponse(rawResponse);

      return result;
    } catch (error) {
      if (error instanceof GeoIntelError) {
        throw error;
      }
      throw new GeoIntelError('An unexpected error occurred', error instanceof Error ? error.message : String(error));
    }
  }
}
