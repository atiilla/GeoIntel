// GeoSense Configuration File
// Customize your application settings here

const GEOSENSE_CONFIG = {
    // Application Settings
    app: {
        name: 'GeoSense',
        tagline: 'AI Location Intelligence',
        defaultTheme: 'dark', // 'dark' or 'light'
    },

    // Branding & Colors
    branding: {
        accentColor: '#06b6d4', // Cyan - change to your brand color
        logo: {
            type: 'icon', // 'icon' or 'image'
            iconClass: 'fas fa-globe-americas', // Font Awesome icon class
            imagePath: '', // Path to logo image if type is 'image'
        }
    },

    // Map Settings
    map: {
        provider: 'google', // Currently only 'google' supported
        apiKey: 'YOUR_API_KEY', // Replace with your Google Maps API key
        initialView: {
            lat: 20,
            lng: 0,
            zoom: 2
        },
        resultView: {
            zoom: 15 // Zoom level when showing results
        }
    },

    // Demo/Sample Data (for testing without backend)
    demo: {
        enabled: true,
        processingDelay: 2000, // ms - simulated AI processing time
        sampleLocation: {
            lat: 52.5163,
            lng: 13.4049,
            city: 'Berlin',
            country: 'Germany',
            explanation: 'The street signs, architecture, and vegetation point to Berlin, Germany. The distinctive TV tower (Fernsehturm) visible in the background, along with characteristic East German-era buildings and the specific style of street furniture, confirms this location near Alexanderplatz.'
        }
    },

    // API Endpoints (for production)
    api: {
        enabled: false, // Set to true when connecting to backend
        endpoints: {
            analyze: '/api/analyze',
            similarImages: '/api/similar',
            export: '/api/export',
            feedback: '/api/feedback'
        },
        baseURL: 'https://your-api-domain.com'
    },

    // Feature Flags
    features: {
        streetView: true,
        similarImages: true,
        pdfExport: true,
        sharing: true,
        feedback: true,
        projectHistory: true,
        themeToggle: true
    },

    // UI Settings
    ui: {
        animations: {
            pinDrop: true,
            tabTransitions: true,
            fadeEffects: true
        },
        uploadMethods: {
            browse: true,
            dragDrop: true,
            quickSearch: true
        }
    },

    // Analytics (optional)
    analytics: {
        enabled: false,
        googleAnalyticsId: '',
        trackEvents: true
    }
};

// Export for use in application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GEOSENSE_CONFIG;
}
