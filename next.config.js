/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  eslint: {
    dirs: ['src'],
  },
  typescript: {
    ignoreBuildErrors: false,
  },

  // API rewrites for Python backend
  // All /api/* requests are proxied to the Python FastAPI backend
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL;

    if (!backendUrl) {
      console.error('ERROR: BACKEND_URL environment variable is not set. Python backend is required.');
      throw new Error('BACKEND_URL must be set to the Python backend URL (e.g., http://localhost:8000)');
    }

    return [
      {
        source: '/api/chat',
        destination: `${backendUrl}/api/chat`,
      },
      {
        source: '/api/session/:path*',
        destination: `${backendUrl}/api/session/:path*`,
      },
      {
        source: '/api/lead',
        destination: `${backendUrl}/api/lead`,
      },
    ];
  },
}

module.exports = nextConfig
