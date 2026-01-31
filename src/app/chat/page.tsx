'use client';

import { useState, useRef, useEffect } from 'react';
import { apiClient, type ChatResponse, ApiClientError } from '@/lib/api-client';
import { LeadCaptureModal, type LeadFormData } from '@/components/chat/LeadCaptureModal';
import { useSessionState } from '@/lib/hooks/useSessionState'; // PR6.1
import { FeatureFlag, isFeatureEnabled } from '@/lib/feature-flags'; // Centralized feature flags

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

const STORAGE_KEY = 'dovvybuddy-session-id';
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // PR6.1: Session state hook (only if feature enabled)
  const { sessionState, updateSessionState, clearSessionState } = useSessionState();

  // Lead form state
  const [showLeadForm, setShowLeadForm] = useState(false);
  const [leadType, setLeadType] = useState<'training' | 'trip' | null>(null);
  const [leadSubmitting, setLeadSubmitting] = useState(false);
  const [leadError, setLeadError] = useState<string | null>(null);

  // Restore sessionId from localStorage on mount
  useEffect(() => {
    try {
      const storedSessionId = localStorage.getItem(STORAGE_KEY);
      if (storedSessionId && UUID_REGEX.test(storedSessionId)) {
        setSessionId(storedSessionId);
        if (process.env.NODE_ENV === 'development') {
          console.log('Session restored from localStorage:', storedSessionId);
        }
      } else if (storedSessionId) {
        // Invalid sessionId format, clear it
        localStorage.removeItem(STORAGE_KEY);
        if (process.env.NODE_ENV === 'development') {
          console.warn('Invalid sessionId in localStorage, cleared:', storedSessionId);
        }
      }
    } catch (error) {
      // localStorage unavailable (private browsing, SecurityError, etc.)
      if (process.env.NODE_ENV === 'development') {
        console.warn('localStorage unavailable, session will not persist:', error);
      }
    }
  }, []);

  // Save sessionId to localStorage when it changes
  useEffect(() => {
    if (sessionId) {
      try {
        localStorage.setItem(STORAGE_KEY, sessionId);
        if (process.env.NODE_ENV === 'development') {
          console.log('Session saved to localStorage:', sessionId);
        }
      } catch (error) {
        // Handle quota exceeded or other storage errors
        if (process.env.NODE_ENV === 'development') {
          console.warn('Failed to save sessionId to localStorage:', error);
        }
      }
    }
  }, [sessionId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Clear session data (localStorage + state)
   * Will be used by "New Chat" button in PR5.3
   */
  const clearSession = () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      // Ignore errors when clearing
      if (process.env.NODE_ENV === 'development') {
        console.warn('Failed to clear localStorage:', error);
      }
    }
    setSessionId(null);
    setMessages([]);
    setError(null);
    // PR6.1: Clear session state
    if (isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP)) {
      clearSessionState();
    }
  };

  /**
   * Handle "New Chat" button click
   * Shows confirmation if conversation has 2+ messages
   */
  const handleNewChat = () => {
    // Show confirmation if conversation has started (2+ messages)
    if (messages.length >= 2) {
      const confirmed = window.confirm(
        'Start a new chat? Your current conversation will be cleared.'
      );
      if (!confirmed) {
        return; // User cancelled
      }
    }

    // Clear session and state
    clearSession();

    if (process.env.NODE_ENV === 'development') {
      console.log('New chat started, session cleared');
    }
  };

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
      
      // PR6.1: Include session state if feature enabled
      const requestPayload: {
        sessionId?: string;
        message: string;
        sessionState?: Record<string, any>;
      } = {
        sessionId: sessionId || undefined,
        message: userMessage.content,
      };
      
      if (isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP)) {
        requestPayload.sessionState = sessionState;
        console.log('Session state sent:', sessionState);
      }
      
      const response: ChatResponse = await apiClient.chat(requestPayload);
      console.log('API Response:', response);

      // Store session ID if this is first message
      if (!sessionId && response.sessionId) {
        setSessionId(response.sessionId);
      }
      
      // PR6.1: Apply state updates from backend if feature enabled
      if (isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP) && response.metadata?.stateUpdates) {
        console.log('State updates received:', response.metadata.stateUpdates);
        updateSessionState(response.metadata.stateUpdates);
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

        // Handle session expiration/not found
        if (err.code === 'SESSION_EXPIRED' || err.code === 'SESSION_NOT_FOUND') {
          clearSession();
          errorMessage = 'Your session has expired. Starting a new chat...';
          if (process.env.NODE_ENV === 'development') {
            console.log('Session expired, cleared from localStorage');
          }
        }

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

  // Lead form handlers
  const handleOpenLeadForm = (type: 'training' | 'trip') => {
    if (process.env.NODE_ENV === 'development') {
      console.log('Opening lead form:', type);
    }
    setLeadType(type);
    setShowLeadForm(true);
    setLeadError(null);
  };

  const handleCloseLeadForm = () => {
    if (!leadSubmitting) {
      setShowLeadForm(false);
      setLeadType(null);
      setLeadError(null);
    }
  };

  const handleLeadSubmit = async (data: LeadFormData) => {
    if (!sessionId) {
      setLeadError('Please start a conversation before submitting a lead.');
      return;
    }

    setLeadSubmitting(true);
    setLeadError(null);

    try {
      // Format payload based on lead type
      let payload: any;
      
      if (leadType === 'training') {
        payload = {
          type: 'training',
          data: {
            name: data.name,
            email: data.email,
            phone: data.phone || undefined,
            certification_level: data.certificationLevel,
            preferred_location: data.location || undefined,
            message: data.message || undefined,
          },
        };
        
        // Only include session_id if it's a valid UUID
        if (sessionId && UUID_REGEX.test(sessionId)) {
          payload.session_id = sessionId;
        }
      } else if (leadType === 'trip') {
        payload = {
          type: 'trip',
          data: {
            name: data.name,
            email: data.email,
            phone: data.phone || undefined,
            destination: data.destination || undefined,
            travel_dates: data.dates || undefined,
            message: data.message || undefined,
          },
        };
        
        // Only include session_id if it's a valid UUID
        if (sessionId && UUID_REGEX.test(sessionId)) {
          payload.session_id = sessionId;
        }
      }

      // Submit lead to API
      const response = await fetch('/api/leads', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to submit lead');
      }

      const result = await response.json();

      if (process.env.NODE_ENV === 'development') {
        console.log('Lead submitted successfully:', result.lead_id);
      }

      // Close modal
      setShowLeadForm(false);
      setLeadType(null);
      setLeadError(null);

      // Add success confirmation to chat
      const confirmationMessage: Message = {
        id: crypto.randomUUID(),
        role: 'system',
        content: `✅ Thanks, ${data.name}! We'll contact you at ${data.email} soon. Feel free to keep asking questions.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, confirmationMessage]);
    } catch (err) {
      // Handle error
      let errorMessage = 'Failed to submit. Please try again.';

      if (err instanceof Error) {
        errorMessage = err.message;
      }

      if (process.env.NODE_ENV === 'development') {
        console.error('Lead submission error:', err);
      }

      setLeadError(errorMessage);
    } finally {
      setLeadSubmitting(false);
    }
  };

  return (
    <main style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <style jsx>{`
        @media (max-width: 768px) {
          .new-chat-text {
            display: none;
          }
        }
      `}</style>
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
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div>
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
          
          {/* Action buttons */}
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {/* New Chat button */}
            <button
              onClick={handleNewChat}
              aria-label="Start a new chat"
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
              title="Start a new chat"
            >
              <span style={{ fontSize: '1rem' }}>➕</span>
              <span className="new-chat-text">New Chat</span>
            </button>
            
            {/* Lead capture buttons */}
            <button
              onClick={() => handleOpenLeadForm('training')}
              disabled={!sessionId}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: !sessionId ? '#e5e5e5' : '#10b981',
                color: !sessionId ? '#999' : 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: !sessionId ? 'not-allowed' : 'pointer',
                whiteSpace: 'nowrap',
              }}
              title={!sessionId ? 'Start a conversation first' : 'Request training information'}
            >
              🎓 Get Certified
            </button>
            <button
              onClick={() => handleOpenLeadForm('trip')}
              disabled={!sessionId}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: !sessionId ? '#e5e5e5' : '#0070f3',
                color: !sessionId ? '#999' : 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: !sessionId ? 'not-allowed' : 'pointer',
                whiteSpace: 'nowrap',
              }}
              title={!sessionId ? 'Start a conversation first' : 'Plan a diving trip'}
            >
              ✈️ Plan a Trip
            </button>
          </div>
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
                justifyContent: 
                  message.role === 'user' 
                    ? 'flex-end' 
                    : message.role === 'system'
                    ? 'center'
                    : 'flex-start',
              }}
            >
              <div
                data-testid={message.role === 'assistant' ? 'ai-message' : message.role === 'user' ? 'user-message' : 'system-message'}
                style={{
                  maxWidth: message.role === 'system' ? '90%' : '80%',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  backgroundColor: 
                    message.role === 'user' 
                      ? '#0070f3' 
                      : message.role === 'system'
                      ? '#f0f7ff'
                      : '#f5f5f5',
                  color: 
                    message.role === 'user' 
                      ? 'white' 
                      : message.role === 'system'
                      ? '#0066cc'
                      : '#333',
                  border: message.role === 'system' ? '1px solid #b3d9ff' : 'none',
                }}
              >
                <div style={{ fontSize: '0.875rem', whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </div>
                {message.role !== 'system' && (
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
                )}
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
              data-testid="chat-input"
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
              data-testid="send-button"
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

      {/* Lead capture modal */}
      <LeadCaptureModal
        isOpen={showLeadForm}
        onClose={handleCloseLeadForm}
        leadType={leadType}
        onSubmit={handleLeadSubmit}
        isSubmitting={leadSubmitting}
        error={leadError}
      />
    </main>
  );
}
