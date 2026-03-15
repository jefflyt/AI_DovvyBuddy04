// @ts-check
const { withSentryConfig } = require('@sentry/nextjs')
const { resolveBackendUrl } = require('./backend-target')

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

  // Enable instrumentation for Sentry
  experimental: {
    instrumentationHook: true,
  },

  // API rewrites for Python backend
  // All /api/* requests are proxied to the Python FastAPI backend
  async rewrites() {
    const backendUrl = resolveBackendUrl()

    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ]
  },
}

module.exports = withSentryConfig(nextConfig, {
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
  silent: !process.env.CI,
  widenClientFileUpload: true,
  reactComponentAnnotation: {
    enabled: true,
  },
  tunnelRoute: '/monitoring',
  hideSourceMaps: true,
  disableLogger: true,
  automaticVercelMonitors: true,
})
