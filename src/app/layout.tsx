'use client'

import { useEffect } from 'react'
import { Analytics } from '@vercel/analytics/react'
import ErrorBoundary from '@/components/ErrorBoundary'
import { initAnalytics } from '@/lib/analytics'
import { initErrorMonitoring } from '@/lib/monitoring'
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  useEffect(() => {
    // Initialize analytics and error monitoring on mount
    initAnalytics()
    initErrorMonitoring()
  }, [])

  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        
        {/* Primary Meta Tags */}
        <title>DovvyBuddy - Your AI Diving Companion</title>
        <meta
          name="title"
          content="DovvyBuddy - Your AI Diving Companion"
        />
        <meta
          name="description"
          content="Get judgment-free guidance on dive certifications, destinations, and trip planning. Built by divers, for divers."
        />
        <meta
          name="keywords"
          content="diving, scuba diving, PADI, SSI, dive certification, dive sites, dive trip planning, recreational diving"
        />

        {/* Open Graph / Facebook */}
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://dovvybuddy.com/" />
        <meta
          property="og:title"
          content="DovvyBuddy - Your AI Diving Companion"
        />
        <meta
          property="og:description"
          content="Get judgment-free guidance on dive certifications, destinations, and trip planning. Built by divers, for divers."
        />
        <meta
          property="og:image"
          content="https://dovvybuddy.com/og-image.png"
        />

        {/* Twitter */}
        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:url" content="https://dovvybuddy.com/" />
        <meta
          property="twitter:title"
          content="DovvyBuddy - Your AI Diving Companion"
        />
        <meta
          property="twitter:description"
          content="Get judgment-free guidance on dive certifications, destinations, and trip planning. Built by divers, for divers."
        />
        <meta
          property="twitter:image"
          content="https://dovvybuddy.com/og-image.png"
        />

        {/* Favicon */}
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
      </head>
      <body>
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
        <Analytics />
      </body>
    </html>
  )
}
