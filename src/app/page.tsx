import Link from 'next/link'

export default function Home() {
  return (
    <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
        Welcome to DovvyBuddy
      </h1>
      <p style={{ fontSize: '1.125rem', marginBottom: '2rem', color: '#666' }}>
        Your AI diving assistant for certification guidance and trip planning
      </p>

      <div
        style={{
          padding: '1.5rem',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          marginBottom: '2rem',
        }}
      >
        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
          What we can help with:
        </h2>
        <ul style={{ paddingLeft: '1.5rem', lineHeight: '2' }}>
          <li>Understanding Open Water certification pathways</li>
          <li>Comparing PADI vs SSI certifications</li>
          <li>Planning your next advanced certification</li>
          <li>Researching dive destinations and sites</li>
          <li>Connecting with reputable dive shops and instructors</li>
        </ul>
      </div>

      <Link
        href="/chat"
        style={{
          display: 'inline-block',
          padding: '0.75rem 2rem',
          backgroundColor: '#0070f3',
          color: 'white',
          borderRadius: '6px',
          fontSize: '1.125rem',
          fontWeight: '500',
        }}
      >
        Start Chat
      </Link>

      <footer
        style={{
          marginTop: '4rem',
          paddingTop: '2rem',
          borderTop: '1px solid #e5e5e5',
        }}
      >
        <p style={{ fontSize: '0.875rem', color: '#999' }}>
          DovvyBuddy V1 - Web Chat Only | Guest Sessions (24h)
        </p>
      </footer>
    </main>
  )
}
