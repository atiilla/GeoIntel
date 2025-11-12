# 🌍 GeoIntel Web Application

A Next.js web application that integrates the GeoIntel geolocation analysis software. Upload images and discover where they were taken using advanced AI-powered pixel-level visual analysis and contextual reasoning.

## Features

- **🖼️ Image Upload**: Drag-and-drop or click to upload images
- **🔍 AI Analysis**: Powered by Google Gemini AI for detailed geolocation analysis
- **📍 Multiple Locations**: Get up to 3 possible locations with confidence levels
- **🗺️ Google Maps Integration**: Direct links to view locations on Google Maps
- **📝 Context Support**: Add additional context or location guesses to improve accuracy
- **📱 Responsive Design**: Works on desktop and mobile devices
- **⚡ Client-Side Processing**: All requests run from the user's browser

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- GIF (.gif)

## Setup

### Prerequisites

- Node.js 18+ 
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd geointelts
```

2. Install dependencies:
```bash
npm install
```

3. Get API keys:
   - **Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **Google Maps API Key**: Visit [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)
   
   **Note**: API keys are configured directly in the application UI and stored in your browser's localStorage. No environment variables needed!

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

### Production

Build and start the production server:

```bash
npm run build
npm start
```

## Usage

1. **Configure API Keys**: Click the key icons in the header to set up your Gemini and Google Maps API keys
2. **Upload an Image**: Drag and drop an image file or click to browse
3. **Add Context (Optional)**: Provide additional information about the image
4. **Add Location Guess (Optional)**: Share your best guess of the location
5. **Analyze**: The AI will analyze the image and provide possible locations
6. **View Results**: See detailed analysis and location suggestions with confidence levels
7. **Explore**: Click "View on Google Maps" to see locations on the map

## Architecture

### Client-Side Components

- **`app/page.tsx`**: Main application interface
- **`app/components/ImageUpload.tsx`**: Image upload component with drag-and-drop
- **`app/components/GeoIntelResults.tsx`**: Results display component
- **`app/services/geointel.ts`**: GeoIntel service class for API interactions
- **`app/types/geointel.ts`**: TypeScript interfaces and types

### Key Features

- **100% Client-Side**: All API requests are made directly from the browser
- **LocalStorage API Keys**: No environment variables needed - configure keys in the UI
- **Dark Theme UI**: Modern dark interface matching the template design
- **Error Handling**: Comprehensive error handling for network, API, and parsing errors
- **TypeScript**: Full type safety throughout the application
- **Responsive UI**: Mobile-friendly design with Tailwind CSS
- **Real-time Feedback**: Loading states and progress indicators

## API Integration

The application integrates with the Google Gemini API for image analysis:

- **Model**: Gemini 2.5 Flash
- **Input**: Base64-encoded images with text prompts
- **Output**: Structured JSON with location predictions and analysis
- **Security**: API key is exposed client-side (use environment restrictions)

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_GEMINI_API_KEY` | Google Gemini API key | Yes |
| `NEXT_PUBLIC_GEMINI_MODEL` | Gemini model to use | No (default: gemini-2.5-flash) |
| `NEXT_PUBLIC_API_TIMEOUT` | API request timeout in ms | No (default: 30000) |
| `NEXT_PUBLIC_MAX_OUTPUT_TOKENS` | Maximum output tokens | No (default: 8192) |

## Security Considerations

- The Gemini API key is exposed client-side as `NEXT_PUBLIC_GEMINI_API_KEY`
- Consider using API key restrictions in Google Cloud Console:
  - Restrict to specific domains/URLs
  - Limit to Gemini API only
  - Set usage quotas

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Add environment variables in Vercel dashboard
4. Deploy

### Other Platforms

The application can be deployed to any platform that supports Next.js:

- Netlify
- AWS Amplify
- Railway
- Render

## Troubleshooting

### Common Issues

1. **"API Key Required" warning**: 
   - Ensure `NEXT_PUBLIC_GEMINI_API_KEY` is set in `.env.local`
   - Restart the development server after adding environment variables

2. **API request failures**:
   - Check your API key is valid and has Gemini API access
   - Verify your API key restrictions allow requests from your domain
   - Check browser console for detailed error messages

3. **Image upload issues**:
   - Ensure image format is supported (JPEG, PNG, WebP, GIF)
   - Check file size is under 10MB
   - Verify browser supports FileReader API

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
