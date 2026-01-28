'use client';

import { useState, useRef, useEffect } from 'react';
import { apiClient, ApiClientError, type ChatResponse } from '@/lib/api-client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      // Call API
      console.log('Calling API with message:', userMessage.content);
      const response: ChatResponse = await apiClient.chat({
        sessionId: sessionId || undefined,
        message: userMessage.content,
      });
      console.log('API Response:', response);

      // Store session ID if this is first message
      if (!sessionId && response.sessionId) {
        setSessionId(response.sessionId);
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
      };
      console.log('Adding assistant message:', assistantMessage);

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      // Handle error
      let errorMessage = 'An unexpected error occurred. Please try again.';

      if (err instanceof ApiClientError) {
        errorMessage = err.userMessage;

        // Log details in development
        if (process.env.NODE_ENV === 'development') {
          console.error('API Error:', {
            code: err.code,
            statusCode: err.statusCode,
            message: err.message,
            details: err.details,
          });
        }
      }

      setError(errorMessage);

      // Remove user message on error (optimistic update rollback)
      setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

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
            Ask me anything about diving certifications and destinations
            {sessionId && (
              <span style={{ marginLeft: '0.5rem', color: '#999' }}>
                (Session: {sessionId.slice(0, 8)}...)
              </span>
            )}
          </p>
        </div>

        {/* Messages area */}
        <div
          style={{
            flex: 1,
            padding: '1.5rem',
            overflowY: 'auto',
            backgroundColor: '#ffffff',
          }}
        >
          {messages.length === 0 && (
            <div
              style={{
                padding: '1rem',
                backgroundColor: '#f0f7ff',
                borderRadius: '8px',
                border: '1px solid #b3d9ff',
              }}
            >
              <div style={{ fontSize: '0.875rem', color: '#0066cc' }}>
                <p>
                  👋 <strong>Welcome!</strong> I&apos;m your AI diving assistant.
                </p>
                <p>Ask me about:</p>
                <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                  <li>PADI and SSI certifications</li>
                  <li>Dive destinations and sites</li>
                  <li>Training and safety</li>
                  <li>Equipment and preparation</li>
                </ul>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              style={{
                marginBottom: '1rem',
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              }}
            >
              <div
                style={{
                  maxWidth: '80%',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  backgroundColor: message.role === 'user' ? '#0070f3' : '#f5f5f5',
                  color: message.role === 'user' ? 'white' : '#333',
                }}
              >
                <div style={{ fontSize: '0.875rem', whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </div>
                <div
                  style={{
                    fontSize: '0.75rem',
                    marginTop: '0.25rem',
                    opacity: 0.7,
                  }}
                >
                  {message.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div
              style={{
                marginBottom: '1rem',
                display: 'flex',
                justifyContent: 'flex-start',
              }}
            >
              <div
                style={{
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  backgroundColor: '#f5f5f5',
                  color: '#666',
                  fontSize: '0.875rem',
                }}
              >
                Thinking...
              </div>
            </div>
          )}

          {error && (
            <div
              style={{
                marginBottom: '1rem',
                padding: '1rem',
                backgroundColor: '#fff0f0',
                border: '1px solid #ffcccc',
                borderRadius: '8px',
              }}
            >
              <p style={{ fontSize: '0.875rem', color: '#cc0000' }}>
                <strong>Error:</strong> {error}
              </p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <form
          onSubmit={handleSubmit}
          style={{
            padding: '1rem 1.5rem',
            borderTop: '1px solid #e5e5e5',
            backgroundColor: '#f9f9f9',
          }}
        >
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              style={{
                flex: 1,
                padding: '0.75rem',
                border: '1px solid #e5e5e5',
                borderRadius: '6px',
                backgroundColor: isLoading ? '#f5f5f5' : 'white',
                fontSize: '1rem',
              }}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: !input.trim() || isLoading ? '#cccccc' : '#0070f3',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '1rem',
                fontWeight: '500',
                cursor: !input.trim() || isLoading ? 'not-allowed' : 'pointer',
              }}
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
