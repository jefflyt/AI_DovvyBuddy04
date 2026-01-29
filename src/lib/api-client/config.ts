/**
 * API Client Configuration
 * Centralized configuration for API client
 */

export interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  credentials: RequestCredentials;
}

/**
 * Get API base URL from environment
 * Server-side: direct connection to Python backend
 * Client-side: proxied through Next.js (/api routes)
 */
function getBaseURL(): string {
  if (typeof window === 'undefined') {
    // Server-side: use BACKEND_URL env var (direct connection to Python backend)
    return process.env.BACKEND_URL || 'http://localhost:8000';
  }
  
  // Client-side: use proxied API URL (handled by Next.js rewrites)
  return process.env.NEXT_PUBLIC_API_URL || '/api';
}

/**
 * Default API client configuration
 */
export const API_CONFIG: ApiClientConfig = {
  baseURL: getBaseURL(),
  timeout: 30000, // 30 seconds
  retryAttempts: 3,
  retryDelay: 1000, // 1 second base delay (exponential backoff)
  credentials: 'include', // Include cookies for session management
};

/**
 * API endpoints
 */
export const API_ENDPOINTS = {
  chat: '/chat',
  session: (sessionId: string) => `/session/${sessionId}`,
  lead: '/leads',
} as const;
