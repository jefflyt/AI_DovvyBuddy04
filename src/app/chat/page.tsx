'use client';

import { useState, useRef, useEffect } from 'react';
import { apiClient, type ChatResponse, ApiClientError } from '@/lib/api-client';
import { LeadCaptureModal, type LeadFormData } from '@/components/chat/LeadCaptureModal';
import { useSessionState } from '@/lib/hooks/useSessionState'; // PR6.1
import { FeatureFlag, isFeatureEnabled } from '@/lib/feature-flags'; // Centralized feature flags
import { WatercolorBackground } from '@/components/ui/WatercolorBackground';
import { ChatMessage } from '@/components/chat/ChatMessage';
import { Send, Plus, MapPin, GraduationCap } from 'lucide-react';
import { cn } from '@/lib/utils';

import Image from 'next/image';

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
        sessionState?: Record<string, unknown>;
      } = {
        sessionId: sessionId || undefined,
        message: userMessage.content,
      };

      if (isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP)) {
        requestPayload.sessionState = sessionState as Record<string, unknown>;
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

      // PR6.1: Include follow-up question in message if present
      let messageContent = response.message;
      if (isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP) && response.followUpQuestion) {
        console.log('Follow-up question received:', response.followUpQuestion);
        messageContent = `${response.message}\n\n─────\n💬 ${response.followUpQuestion}`;
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: messageContent,
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
      let payload: Record<string, unknown> = {};

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
    <main className="relative min-h-screen flex flex-col items-center">
      <WatercolorBackground />

      <div className="w-full max-w-4xl flex-1 flex flex-col h-[calc(100vh-2rem)] my-4 mx-4 md:mx-auto glass-panel rounded-2xl overflow-hidden relative z-10">

        {/* Header */}
        <div className="px-6 py-4 border-b border-border/50 bg-white/50 backdrop-blur-sm flex justify-between items-center z-20">
          <div>
            <h1 className="text-xl font-bold text-primary-800 tracking-tight">
              DovvyBuddy<span className="text-accent-500">.</span>
            </h1>
            <p className="text-xs text-muted-foreground mt-0.5">
              Your Minimalist Diving Companion
            </p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleNewChat}
              className="p-2 text-muted-foreground hover:text-primary transition-colors rounded-full hover:bg-primary/5"
              title="New Chat"
            >
              <Plus size={20} />
            </button>
          </div>
        </div>

        {/* Floating Action Buttons Implementation (optional/alternative to header buttons) */}
        <div className="absolute top-4 right-16 flex gap-2 z-20 hidden md:flex">
          <button
            onClick={() => handleOpenLeadForm('training')}
            disabled={!sessionId}
            className={cn(
              "px-3 py-1.5 text-xs font-medium rounded-full border transition-all flex items-center gap-1.5",
              !sessionId
                ? "border-border text-muted-foreground cursor-not-allowed opacity-50"
                : "border-accent-200 bg-accent-50 text-accent-700 hover:bg-accent-100 hover:border-accent-300"
            )}
          >
            <GraduationCap size={14} />
            Get Certified
          </button>
          <button
            onClick={() => handleOpenLeadForm('trip')}
            disabled={!sessionId}
            className={cn(
              "px-3 py-1.5 text-xs font-medium rounded-full border transition-all flex items-center gap-1.5",
              !sessionId
                ? "border-border text-muted-foreground cursor-not-allowed opacity-50"
                : "border-primary-200 bg-primary-50 text-primary-700 hover:bg-primary-100 hover:border-primary-300"
            )}
          >
            <MapPin size={14} />
            Plan Trip
          </button>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 scroll-smooth">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center p-8 opacity-60">
              <div className="w-24 h-24 mb-6 opacity-80 mix-blend-multiply relative">
                <Image
                  src="/assets/icons/dive-mask.png"
                  alt="DovvyBuddy"
                  fill
                  className="object-contain"
                  priority
                />
              </div>
              <h2 className="text-lg font-medium text-primary-900 mb-2">How can I help you dive today?</h2>
              <p className="text-sm text-muted-foreground max-w-md">
                Ask about PADI/SSI courses, dive sites, or safety tips.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
            />
          ))}

          {isLoading && (
            <div className="flex justify-start mb-6">
              <div className="bg-white/50 backdrop-blur-sm px-4 py-3 rounded-2xl rounded-tl-sm border border-border/50 text-sm text-muted-foreground animate-pulse">
                Thinking...
              </div>
            </div>
          )}

          {error && (
            <div className="mx-auto max-w-md my-4 p-3 bg-red-50 text-red-600 text-xs rounded-lg border border-red-100 text-center">
              {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white/60 backdrop-blur-md border-t border-white/50">
          <form
            onSubmit={handleSubmit}
            className="flex gap-2 max-w-3xl mx-auto relative"
          >
            <input
              type="text"
              placeholder="Ask anything about diving..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              className="flex-1 bg-white/80 border-0 ring-1 ring-border/50 focus:ring-2 focus:ring-primary/20 rounded-xl px-4 py-3 text-sm shadow-sm placeholder:text-muted-foreground/70 transition-all outline-none"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className={cn(
                "p-3 rounded-xl transition-all shadow-sm flex items-center justify-center",
                !input.trim() || isLoading
                  ? "bg-muted text-muted-foreground cursor-not-allowed"
                  : "bg-primary text-white hover:bg-primary-600 hover:shadow-md active:scale-95"
              )}
            >
              <Send size={18} />
            </button>
          </form>
          <div className="text-center mt-2">
            <p className="text-[10px] text-muted-foreground/60">
              AI can make mistakes. Always verify with a certified instructor.
            </p>
          </div>
        </div>
      </div>

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
