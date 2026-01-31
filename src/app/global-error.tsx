'use client'

import * as Sentry from '@sentry/nextjs'
import { useEffect } from 'react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to Sentry
    Sentry.captureException(error)
  }, [error])

  return (
    <html>
      <body>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          padding: '20px',
          fontFamily: 'system-ui, -apple-system, sans-serif',
        }}>
          <div style={{
            maxWidth: '600px',
            textAlign: 'center',
          }}>
            <h1 style={{ fontSize: '24px', marginBottom: '16px', color: '#111' }}>
              Something went wrong!
            </h1>
            <p style={{ fontSize: '16px', marginBottom: '24px', color: '#666' }}>
              We apologize for the inconvenience. Our team has been notified and is working on fixing the issue.
            </p>
            <button
              onClick={() => reset()}
              style={{
                padding: '12px 24px',
                fontSize: '16px',
                backgroundColor: '#0077BE',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '500',
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#005f9a'
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = '#0077BE'
              }}
            >
              Try again
            </button>
          </div>
        </div>
      </body>
    </html>
  )
}
