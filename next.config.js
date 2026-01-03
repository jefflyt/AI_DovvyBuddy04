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

  // API rewrites for Python backend integration
  // Proxy /api/* requests to Python backend if BACKEND_URL is set
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL;
    const usePythonBackend = process.env.USE_PYTHON_BACKEND !== 'false';

    // Only rewrite if Python backend is enabled and URL is provided
    if (!usePythonBackend || !backendUrl) {
      return [];
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
