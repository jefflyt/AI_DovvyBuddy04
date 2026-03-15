const DEFAULT_LOCAL_BACKEND_URL = 'http://localhost:8000'

function resolveBackendUrl({
  backendUrl = process.env.BACKEND_URL,
  nodeEnv = process.env.NODE_ENV,
} = {}) {
  if (backendUrl) {
    return backendUrl.replace(/\/+$/, '')
  }

  if (nodeEnv !== 'production') {
    console.warn(
      `WARN: BACKEND_URL is not set. Falling back to ${DEFAULT_LOCAL_BACKEND_URL} for local proxying.`
    )
    return DEFAULT_LOCAL_BACKEND_URL
  }

  throw new Error(
    'BACKEND_URL is required for production builds so /api requests have a backend target.'
  )
}

module.exports = {
  DEFAULT_LOCAL_BACKEND_URL,
  resolveBackendUrl,
}
