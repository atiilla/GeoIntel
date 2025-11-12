// GeoIntel TypeScript interfaces based on Python implementation

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface Location {
  country: string;
  state: string;
  city: string;
  confidence: 'High' | 'Medium' | 'Low';
  coordinates: Coordinates;
  explanation: string;
}

export interface GeoIntelResponse {
  interpretation: string;
  locations: Location[];
}

export interface GeoIntelError {
  error: string;
  details: string;
}

export interface GeoIntelRequest {
  imageBase64: string;
  mimeType?: string;
  contextInfo?: string;
  locationGuess?: string;
}

export interface GeminiGenerationConfig {
  temperature: number;
  topK: number;
  topP: number;
  maxOutputTokens: number;
}

export interface GeminiRequestPayload {
  contents: Array<{
    parts: Array<{
      text?: string;
      inline_data?: {
        mime_type: string;
        data: string;
      };
    }>;
  }>;
  generationConfig: GeminiGenerationConfig;
}

export interface GeminiResponse {
  candidates: Array<{
    content: {
      parts: Array<{
        text: string;
      }>;
    };
  }>;
}

// Configuration constants
export const GEOINTEL_CONFIG = {
  GEMINI_API_BASE_URL: 'https://generativelanguage.googleapis.com/v1/models',
  GEMINI_MODEL: 'gemini-2.5-flash',
  API_TIMEOUT: 30000,
  DEFAULT_TEMPERATURE: 0.3,
  DEFAULT_TOP_K: 40,
  DEFAULT_TOP_P: 0.95,
  MAX_OUTPUT_TOKENS: 8192,
  SUPPORTED_IMAGE_FORMATS: ['jpeg', 'jpg', 'png', 'webp', 'gif'],
  DEFAULT_MIME_TYPE: 'image/jpeg',
  IMAGE_DOWNLOAD_TIMEOUT: 10000,
  MAX_LOCATIONS: 3,
  CONFIDENCE_LEVELS: ['High', 'Medium', 'Low'] as const,
} as const;

export type ConfidenceLevel = typeof GEOINTEL_CONFIG.CONFIDENCE_LEVELS[number];
export type SupportedImageFormat = typeof GEOINTEL_CONFIG.SUPPORTED_IMAGE_FORMATS[number];
