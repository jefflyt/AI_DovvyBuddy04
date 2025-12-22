export default function ChatPage() {
  return (
    <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          height: 'calc(100vh - 4rem)',
          border: '1px solid #e5e5e5',
          borderRadius: '8px',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '1rem 1.5rem',
            borderBottom: '1px solid #e5e5e5',
            backgroundColor: '#f9f9f9',
          }}
        >
          <h1 style={{ fontSize: '1.5rem', fontWeight: '600' }}>
            DovvyBuddy Chat
          </h1>
          <p
            style={{
              fontSize: '0.875rem',
              color: '#666',
              marginTop: '0.25rem',
            }}
          >
            Chat interface coming soon - PR0 bootstrap only
          </p>
        </div>

        {/* Messages area (placeholder) */}
        <div
          style={{
            flex: 1,
            padding: '1.5rem',
            overflowY: 'auto',
            backgroundColor: '#ffffff',
          }}
        >
          <div
            style={{
              padding: '1rem',
              backgroundColor: '#f0f7ff',
              borderRadius: '8px',
              border: '1px solid #b3d9ff',
            }}
          >
            <p style={{ fontSize: '0.875rem', color: '#0066cc' }}>
              👋 <strong>Welcome!</strong> This is a placeholder for the chat
              interface.
              <br />
              <br />
              The actual chat functionality (message handling, RAG retrieval,
              LLM integration, and session management) will be implemented in
              future PRs.
            </p>
          </div>
        </div>

        {/* Input area (placeholder) */}
        <div
          style={{
            padding: '1rem 1.5rem',
            borderTop: '1px solid #e5e5e5',
            backgroundColor: '#f9f9f9',
          }}
        >
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              placeholder="Message input (not functional yet)"
              disabled
              style={{
                flex: 1,
                padding: '0.75rem',
                border: '1px solid #e5e5e5',
                borderRadius: '6px',
                backgroundColor: '#f5f5f5',
              }}
            />
            <button
              disabled
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#cccccc',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'not-allowed',
              }}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}
