'use client';

import { useState, useEffect, useRef } from 'react';
import { GeoIntel } from './services/geointel';
import { GeoIntelResponse } from './types/geointel';

export default function Home() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<GeoIntelResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [contextInfo, setContextInfo] = useState('');
  const [locationGuess, setLocationGuess] = useState('');
  const [showApiModal, setShowApiModal] = useState(false);
  const [showMapsApiModal, setShowMapsApiModal] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [mapsApiKey, setMapsApiKey] = useState('');
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'results' | 'similar'>('results');
  const [dragActive, setDragActive] = useState(false);
  const [mapLoaded, setMapLoaded] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markerRef = useRef<any>(null);

  useEffect(() => {
    const storedApiKey = localStorage.getItem('geointel_gemini_api_key');
    const storedMapsApiKey = localStorage.getItem('geointel_maps_api_key');
    if (storedApiKey) setApiKey(storedApiKey);
    if (storedMapsApiKey) {
      setMapsApiKey(storedMapsApiKey);
      loadGoogleMaps(storedMapsApiKey);
    }
  }, []);

  const loadGoogleMaps = (apiKey: string) => {
    if (mapLoaded || !apiKey) return;

    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap`;
    script.async = true;
    script.defer = true;
    script.onerror = () => {
      console.error('Failed to load Google Maps');
      setError('Failed to load Google Maps. Please check your API key.');
    };

    (window as any).initMap = () => {
      initializeMap();
    };

    document.head.appendChild(script);
  };

  const initializeMap = () => {
    if (!mapRef.current) return;

    try {
      const mapOptions = {
        center: { lat: 20, lng: 0 },
        zoom: 2,
        mapTypeId: 'satellite',
        styles: [
          { elementType: "geometry", stylers: [{ color: "#1e293b" }] },
          { elementType: "labels.text.stroke", stylers: [{ color: "#0f172a" }] },
          { elementType: "labels.text.fill", stylers: [{ color: "#94a3b8" }] },
          {
            featureType: "administrative.locality",
            elementType: "labels.text.fill",
            stylers: [{ color: "#06b6d4" }],
          },
          {
            featureType: "poi",
            elementType: "labels.text.fill",
            stylers: [{ color: "#94a3b8" }],
          },
          {
            featureType: "poi.park",
            elementType: "geometry",
            stylers: [{ color: "#1e3a2e" }],
          },
          {
            featureType: "road",
            elementType: "geometry",
            stylers: [{ color: "#334155" }],
          },
          {
            featureType: "road",
            elementType: "geometry.stroke",
            stylers: [{ color: "#1e293b" }],
          },
          {
            featureType: "road.highway",
            elementType: "geometry",
            stylers: [{ color: "#475569" }],
          },
          {
            featureType: "water",
            elementType: "geometry",
            stylers: [{ color: "#0c1e2e" }],
          },
          {
            featureType: "water",
            elementType: "labels.text.fill",
            stylers: [{ color: "#64748b" }],
          },
        ],
        disableDefaultUI: false,
        zoomControl: true,
        mapTypeControl: false,
        streetViewControl: false,
        rotateControl: true,
        tiltControl: true,
      };

      mapInstanceRef.current = new (window as any).google.maps.Map(mapRef.current, mapOptions);
      setMapLoaded(true);
      console.log('Google Maps initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Google Maps:', error);
      setError('Failed to initialize Google Maps');
    }
  };

  // Update map when results are available
  useEffect(() => {
    if (results && results.locations.length > 0 && mapInstanceRef.current) {
      const location = results.locations[0];
      const position = {
        lat: location.coordinates.latitude,
        lng: location.coordinates.longitude
      };

      // Center map on location
      mapInstanceRef.current.setCenter(position);
      mapInstanceRef.current.setZoom(15);

      // Remove existing marker
      if (markerRef.current) {
        markerRef.current.setMap(null);
      }

      // Add new marker
      markerRef.current = new (window as any).google.maps.Marker({
        position: position,
        map: mapInstanceRef.current,
        title: `${location.city}, ${location.country}`,
        animation: (window as any).google.maps.Animation.DROP,
      });

      // Add info window
      const infoWindow = new (window as any).google.maps.InfoWindow({
        content: `
          <div style="color: #1f2937; padding: 8px;">
            <h3 style="margin: 0 0 8px 0; font-weight: bold;">${location.city}</h3>
            <p style="margin: 0; color: #6b7280;">${location.country}</p>
            <p style="margin: 4px 0 0 0; font-size: 12px; color: #9ca3af;">
              Confidence: ${location.confidence}
            </p>
          </div>
        `
      });

      markerRef.current.addListener('click', () => {
        infoWindow.open(mapInstanceRef.current, markerRef.current);
      });
    }
  }, [results]);

  // Update Maps API key and reload map
  const saveMapsApiKey = () => {
    localStorage.setItem('geointel_maps_api_key', mapsApiKey);
    setShowMapsApiModal(false);
    if (mapsApiKey && !mapLoaded) {
      loadGoogleMaps(mapsApiKey);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!apiKey) {
      setShowApiModal(true);
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setResults(null);

    // Create preview URL
    const url = URL.createObjectURL(file);
    setUploadedImage(url);

    try {
      const geoIntel = new GeoIntel(apiKey);
      const result = await geoIntel.locate(
        file,
        contextInfo.trim() || undefined,
        locationGuess.trim() || undefined
      );
      setResults(result);
    } catch (err) {
      console.error('GeoIntel analysis failed:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const saveApiKey = () => {
    localStorage.setItem('geointel_gemini_api_key', apiKey);
    setShowApiModal(false);
  };


  const clearFields = () => {
    setContextInfo('');
    setLocationGuess('');
  };

  return (
    <div className="bg-slate-900 text-gray-100 antialiased min-h-screen">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 h-16 sticky top-0 z-50 shadow-lg">
        <div className="h-full px-6 flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2">
              <i className="fas fa-map-marked-alt text-cyan-500 text-2xl"></i>
              <span className="text-xl font-bold text-white">GeoIntel</span>
            </div>
            <nav className="hidden md:flex items-center space-x-6">
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="text-gray-300 hover:text-white transition"
              >
                Quick Search
              </button>
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            <button 
              onClick={() => setShowApiModal(true)}
              className="p-2 rounded-lg hover:bg-slate-700 transition" 
              title="Configure Gemini API Key"
            >
              <i className="fas fa-key text-gray-300"></i>
            </button>
            <button 
              onClick={() => setShowMapsApiModal(true)}
              className="p-2 rounded-lg hover:bg-slate-700 transition" 
              title="Configure Google Maps API Key"
            >
              <i className="fas fa-map-marked-alt text-gray-300"></i>
            </button>
          </div>
        </div>
      </header>

      {/* API Key Modal */}
      {showApiModal && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-8 max-w-md w-full mx-4 border border-slate-700 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white flex items-center">
                <i className="fas fa-key text-cyan-500 mr-3"></i>
                Gemini API Key
              </h2>
              <button 
                onClick={() => setShowApiModal(false)}
                className="text-gray-400 hover:text-white transition"
              >
                <i className="fas fa-times text-xl"></i>
              </button>
            </div>
            <div className="mb-6">
              <p className="text-gray-300 mb-4">Enter your Google Gemini API key to enable AI-powered location analysis.</p>
              <div className="bg-slate-700 rounded-lg p-3 mb-4">
                <p className="text-sm text-gray-400 mb-2">
                  <i className="fas fa-info-circle text-cyan-500 mr-2"></i>
                  Don't have an API key?
                </p>
                <a 
                  href="https://makersuite.google.com/app/apikey" 
                  target="_blank"
                  className="text-cyan-500 hover:text-cyan-400 text-sm flex items-center"
                >
                  Get one from Google AI Studio
                  <i className="fas fa-external-link-alt ml-2 text-xs"></i>
                </a>
              </div>
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">API Key</label>
              <input 
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your Gemini API key..."
                className="w-full bg-slate-700 text-white px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
              />
            </div>
            <div className="flex space-x-3">
              <button 
                onClick={saveApiKey}
                className="flex-1 bg-cyan-500 hover:bg-cyan-600 text-white py-3 rounded-lg font-medium transition"
              >
                <i className="fas fa-save mr-2"></i>Save Key
              </button>
              <button 
                onClick={() => setShowApiModal(false)}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-white py-3 rounded-lg font-medium transition"
              >
                Cancel
              </button>
            </div>
            <div className="mt-4 text-xs text-gray-500">
              <i className="fas fa-lock mr-1"></i>
              Your API key is stored locally in your browser and never sent to our servers.
            </div>
          </div>
        </div>
      )}

      {/* Maps API Key Modal */}
      {showMapsApiModal && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-8 max-w-md w-full mx-4 border border-slate-700 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white flex items-center">
                <i className="fas fa-map-marked-alt text-cyan-500 mr-3"></i>
                Google Maps API Key
              </h2>
              <button 
                onClick={() => setShowMapsApiModal(false)}
                className="text-gray-400 hover:text-white transition"
              >
                <i className="fas fa-times text-xl"></i>
              </button>
            </div>
            <div className="mb-6">
              <p className="text-gray-300 mb-4">Enter your Google Maps API key to enable map features.</p>
              <div className="bg-slate-700 rounded-lg p-3 mb-4">
                <p className="text-sm text-gray-400 mb-2">
                  <i className="fas fa-info-circle text-cyan-500 mr-2"></i>
                  Don't have an API key?
                </p>
                <a 
                  href="https://console.cloud.google.com/google/maps-apis" 
                  target="_blank"
                  className="text-cyan-500 hover:text-cyan-400 text-sm flex items-center"
                >
                  Get one from Google Cloud Console
                  <i className="fas fa-external-link-alt ml-2 text-xs"></i>
                </a>
              </div>
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">Google Maps API Key</label>
              <input 
                type="password"
                value={mapsApiKey}
                onChange={(e) => setMapsApiKey(e.target.value)}
                placeholder="Enter your Google Maps API key..."
                className="w-full bg-slate-700 text-white px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
              />
            </div>
            <div className="flex space-x-3">
              <button 
                onClick={saveMapsApiKey}
                className="flex-1 bg-cyan-500 hover:bg-cyan-600 text-white py-3 rounded-lg font-medium transition"
              >
                <i className="fas fa-save mr-2"></i>Save Key
              </button>
              <button 
                onClick={() => setShowMapsApiModal(false)}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-white py-3 rounded-lg font-medium transition"
              >
                Cancel
              </button>
            </div>
            <div className="mt-4 text-xs text-gray-500">
              <i className="fas fa-lock mr-1"></i>
              Your API key is stored locally in your browser and never sent to our servers.
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex flex-col lg:flex-row h-[calc(100vh-64px)]">
        {/* Left Column - Map/Upload Area */}
        <div className="w-full lg:w-[65%] relative bg-slate-900">
          <div className="h-full relative">
            <div ref={mapRef} className="w-full h-full bg-slate-800"></div>

            {/* Upload Overlay */}
            {!results && !isAnalyzing && (
              <div 
                className="absolute inset-0 flex items-center justify-center bg-slate-900 bg-opacity-90 z-10"
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <div className="text-center max-w-md">
                  <div 
                    className={`w-32 h-32 mx-auto mb-6 border-4 border-dashed rounded-full flex items-center justify-center hover:bg-cyan-500 hover:bg-opacity-10 transition cursor-pointer ${
                      dragActive ? 'border-cyan-500 bg-cyan-500 bg-opacity-10' : 'border-cyan-500'
                    }`}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <i className="fas fa-cloud-upload-alt text-5xl text-cyan-500"></i>
                  </div>
                  <h2 className="text-2xl font-semibold mb-2">Upload an Image</h2>
                  <p className="text-gray-400 mb-6">Drag & drop or click to browse</p>
                  
                  <div className="flex flex-col space-y-3 mb-6">
                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-cyan-500 hover:bg-cyan-600 text-white px-6 py-3 rounded-lg font-medium transition"
                    >
                      <i className="fas fa-folder-open mr-2"></i>Browse Files
                    </button>
                  </div>

                  {/* Context Fields */}
                  <div className="w-full space-y-3 mb-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        <i className="fas fa-info-circle mr-1"></i>Additional Context (Optional)
                      </label>
                      <textarea 
                        value={contextInfo}
                        onChange={(e) => setContextInfo(e.target.value)}
                        placeholder="Any additional information about the image"
                        className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 transition resize-none"
                        rows={2}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        <i className="fas fa-map-marker-alt mr-1"></i>Location Guess (Optional)
                      </label>
                      <input 
                        type="text"
                        value={locationGuess}
                        onChange={(e) => setLocationGuess(e.target.value)}
                        placeholder="Your guess of where this might be"
                        className="w-full bg-slate-700 text-white px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 transition"
                      />
                    </div>
                    <div className="flex justify-end">
                      <button 
                        onClick={clearFields}
                        className="text-xs text-gray-400 hover:text-gray-300 transition"
                      >
                        <i className="fas fa-times mr-1"></i>Clear fields
                      </button>
                    </div>
                  </div>

                  <input 
                    ref={fileInputRef}
                    type="file" 
                    accept="image/*" 
                    className="hidden"
                    onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                  />
                  
                  <div className="text-xs text-gray-500 mt-4">
                    <i className="fas fa-info-circle mr-1"></i>
                    Make sure to configure your Gemini API key in settings
                  </div>
                </div>
              </div>
            )}

            {/* Processing Overlay */}
            {isAnalyzing && (
              <div className="absolute inset-0 flex items-center justify-center bg-slate-900 bg-opacity-90 z-10">
                <div className="text-center">
                  <div className="w-10 h-10 border-3 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-xl font-medium">Analyzing image...</p>
                  <p className="text-gray-400 mt-2">AI is identifying the location</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Results Panel */}
        <div className="w-full lg:w-[35%] bg-slate-800 border-l border-slate-700 overflow-y-auto">
          {/* Tabs */}
          <div className="border-b border-slate-700 flex">
            <button 
              onClick={() => setActiveTab('results')}
              className={`flex-1 px-6 py-4 font-medium transition ${
                activeTab === 'results' 
                  ? 'border-b-2 border-cyan-500 text-cyan-500' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Results
            </button>
            <button 
              onClick={() => setActiveTab('similar')}
              className={`flex-1 px-6 py-4 font-medium transition ${
                activeTab === 'similar' 
                  ? 'border-b-2 border-cyan-500 text-cyan-500' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Similar Images
            </button>
          </div>

          {/* Results Content */}
          {activeTab === 'results' && (
            <div className="p-6 space-y-6">
              {!results && !error && !isAnalyzing && (
                <div className="text-center py-12">
                  <i className="fas fa-image text-6xl text-gray-600 mb-4"></i>
                  <p className="text-gray-400 text-lg">Upload an image to begin analysis</p>
                </div>
              )}

              {error && (
                <div className="bg-red-900 bg-opacity-50 border border-red-700 rounded-lg p-4">
                  <div className="flex items-center">
                    <i className="fas fa-exclamation-triangle text-red-400 mr-2"></i>
                    <h3 className="font-medium text-red-300">Analysis Error</h3>
                  </div>
                  <p className="text-red-200 mt-2">{error}</p>
                </div>
              )}

              {results && (
                <div className="space-y-6">
                  {/* Uploaded Image Preview */}
                  {uploadedImage && (
                    <div className="bg-slate-700 rounded-lg overflow-hidden">
                      <img src={uploadedImage} alt="Uploaded" className="w-full h-48 object-cover" />
                    </div>
                  )}

                  {/* AI Analysis */}
                  {results.interpretation && (
                    <div className="bg-slate-700 rounded-lg p-5">
                      <div className="flex items-start space-x-3 mb-3">
                        <i className="fas fa-brain text-cyan-500 text-xl mt-1"></i>
                        <h3 className="font-semibold text-lg">AI Analysis</h3>
                      </div>
                      <p className="text-gray-300 leading-relaxed">{results.interpretation}</p>
                    </div>
                  )}

                  {/* Location Details */}
                  {results.locations.map((location, index) => (
                    <div key={index} className="bg-slate-700 rounded-lg p-5">
                      <h3 className="font-semibold text-lg mb-4">Location Details #{index + 1}</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">Confidence:</span>
                          <span className={`px-2 py-1 rounded text-sm ${
                            location.confidence === 'High' ? 'bg-green-900 text-green-300' :
                            location.confidence === 'Medium' ? 'bg-yellow-900 text-yellow-300' :
                            'bg-red-900 text-red-300'
                          }`}>
                            {location.confidence}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">City:</span>
                          <span className="font-medium">{location.city}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">Country:</span>
                          <span className="font-medium">{location.country}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-gray-400">Coordinates:</span>
                          <span className="font-mono text-sm">
                            {location.coordinates.latitude.toFixed(6)}, {location.coordinates.longitude.toFixed(6)}
                          </span>
                        </div>
                        {location.explanation && (
                          <div>
                            <span className="text-gray-400 block mb-1">Explanation:</span>
                            <p className="text-gray-300 text-sm leading-relaxed">{location.explanation}</p>
                          </div>
                        )}
                        <a
                          href={`https://www.google.com/maps?q=${location.coordinates.latitude},${location.coordinates.longitude}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-3 py-2 text-sm font-medium text-cyan-400 bg-cyan-900 bg-opacity-30 rounded-md hover:bg-opacity-50 transition-colors"
                        >
                          <i className="fas fa-map-marker-alt mr-2"></i>
                          View on Google Maps
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'similar' && (
            <div className="p-6">
              <div className="text-center py-12">
                <i className="fas fa-images text-6xl text-gray-600 mb-4"></i>
                <p className="text-gray-400 text-lg mb-4">Reverse image search results will appear here</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <footer className="bg-slate-800 border-t border-slate-700 py-8">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <i className="fas fa-info-circle text-cyan-500 mr-2"></i>
                About GeoIntel
              </h3>
              <p className="text-gray-300 text-sm leading-relaxed">
                Advanced AI-powered geolocation analysis using pixel-level visual analysis and contextual reasoning. 
                Powered by Google Gemini AI for accurate location identification.
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <i className="fab fa-github text-cyan-500 mr-2"></i>
                Open Source
              </h3>
              <div className="space-y-3">
                <a
                  href="https://github.com/atiilla/GeoIntel"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-gray-300 hover:text-cyan-400 transition-colors"
                >
                  <i className="fas fa-star text-yellow-400 mr-2"></i>
                  <span className="text-sm">Star this repository</span>
                </a>
                <a
                  href="https://github.com/atiilla/GeoIntel/fork"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-gray-300 hover:text-cyan-400 transition-colors"
                >
                  <i className="fas fa-code-branch text-cyan-400 mr-2"></i>
                  <span className="text-sm">Fork & contribute</span>
                </a>
                <a
                  href="https://github.com/atiilla/GeoIntel/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-gray-300 hover:text-cyan-400 transition-colors"
                >
                  <i className="fas fa-bug text-red-400 mr-2"></i>
                  <span className="text-sm">Report issues</span>
                </a>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <i className="fas fa-user text-cyan-500 mr-2"></i>
                Author
              </h3>
              <div className="space-y-3">
                <a
                  href="https://github.com/atiilla"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center text-gray-300 hover:text-cyan-400 transition-colors"
                >
                  <i className="fab fa-github mr-2"></i>
                  <span className="text-sm">@atiilla</span>
                </a>
                <p className="text-gray-400 text-xs">
                  <i className="fas fa-heart text-red-400 mr-1"></i>
                  Contributions are welcomed!
                </p>
              </div>
            </div>
          </div>

          <div className="border-t border-slate-700 mt-8 pt-6 flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-4 mb-4 md:mb-0">
              <span className="text-gray-400 text-sm">
                © 2025 GeoIntel. Open source project.
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="https://github.com/atiilla/GeoIntel"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center"
              >
                <i className="fab fa-github mr-2"></i>
                View on GitHub
              </a>
              <a
                href="https://github.com/atiilla/GeoIntel"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-cyan-500 hover:bg-cyan-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center"
              >
                <i className="fas fa-star mr-2"></i>
                Give us a Star
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
