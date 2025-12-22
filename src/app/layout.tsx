import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'DovvyBuddy - AI Diving Assistant',
  description:
    'Certification guidance and dive trip planning for recreational divers',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
