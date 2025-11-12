'use client';

import { GeoIntelResponse, Location } from '../types/geointel';

interface GeoIntelResultsProps {
  results: GeoIntelResponse | null;
  error: string | null;
  className?: string;
}

function ConfidenceBadge({ confidence }: { confidence: string }) {
  const getConfidenceColor = (conf: string) => {
    switch (conf.toLowerCase()) {
      case 'high':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getConfidenceColor(confidence)}`}>
      {confidence}
    </span>
  );
}

function LocationCard({ location, index }: { location: Location; index: number }) {
  const { country, state, city, confidence, coordinates, explanation } = location;

  const googleMapsUrl = `https://www.google.com/maps?q=${coordinates.latitude},${coordinates.longitude}`;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-lg font-semibold text-gray-900">#{index + 1}</span>
          <ConfidenceBadge confidence={confidence} />
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {city}
            {state && `, ${state}`}
          </h3>
          <p className="text-gray-600">{country}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Latitude:</span>
            <p className="text-gray-600">{coordinates.latitude.toFixed(6)}</p>
          </div>
          <div>
            <span className="font-medium text-gray-700">Longitude:</span>
            <p className="text-gray-600">{coordinates.longitude.toFixed(6)}</p>
          </div>
        </div>

        {explanation && (
          <div>
            <span className="font-medium text-gray-700 block mb-1">Analysis:</span>
            <p className="text-gray-600 text-sm leading-relaxed">{explanation}</p>
          </div>
        )}

        <div className="pt-3 border-t border-gray-100">
          <a
            href={googleMapsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            View on Google Maps
          </a>
        </div>
      </div>
    </div>
  );
}

export default function GeoIntelResults({ results, error, className = '' }: GeoIntelResultsProps) {
  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
        <div className="flex items-center">
          <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-medium text-red-800">Analysis Error</h3>
        </div>
        <p className="mt-2 text-red-700">{error}</p>
      </div>
    );
  }

  if (!results) {
    return null;
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Interpretation Section */}
      {results.interpretation && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-blue-900 mb-3 flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Image Analysis
          </h2>
          <p className="text-blue-800 leading-relaxed">{results.interpretation}</p>
        </div>
      )}

      {/* Locations Section */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Possible Locations ({results.locations.length})
        </h2>
        
        <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
          {results.locations.map((location, index) => (
            <LocationCard key={index} location={location} index={index} />
          ))}
        </div>
      </div>
    </div>
  );
}
