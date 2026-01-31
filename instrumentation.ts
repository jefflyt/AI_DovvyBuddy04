// Instrumentation file for Next.js
// https://nextjs.org/docs/app/building-your-application/optimizing/instrumentation

export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    // Server-side instrumentation
    const { captureException } = await import('@sentry/nextjs')
    
    // Global error handler for uncaught exceptions
    process.on('unhandledRejection', (reason) => {
      console.error('Unhandled Rejection:', reason)
      captureException(reason)
    })

    process.on('uncaughtException', (error) => {
      console.error('Uncaught Exception:', error)
      captureException(error)
    })
  }

  if (process.env.NEXT_RUNTIME === 'edge') {
    // Edge runtime instrumentation
    const { captureException } = await import('@sentry/nextjs')
    
    // Global error handler for edge runtime
    globalThis.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled Rejection (Edge):', event.reason)
      captureException(event.reason)
    })
  }
}
