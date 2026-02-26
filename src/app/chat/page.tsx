'use client'

import { Suspense, useState, useRef, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { apiClient, type ChatResponse, ApiClientError } from '@/lib/api-client'
import {
  LeadCaptureModal,
  type LeadFormData,
} from '@/components/chat/LeadCaptureModal'
import { useSessionState } from '@/lib/hooks/useSessionState' // PR6.1
import { FeatureFlag, isFeatureEnabled } from '@/lib/feature-flags' // Centralized feature flags
import { WatercolorBackground } from '@/components/ui/WatercolorBackground'
import { ChatMessage } from '@/components/chat/ChatMessage'
import { Send, Plus, MapPin, GraduationCap } from 'lucide-react'
import { cn } from '@/lib/utils'
import Image from 'next/image'

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

const STORAGE_KEY = 'dovvybuddy-session-id'
const UUID_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

function ChatContent() {
  const searchParams = useSearchParams()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // PR6.1: Session state hook (only if feature enabled)
  const { sessionState, updateSessionState, clearSessionState } =
    useSessionState()

  // Lead form state
  const [showLeadForm, setShowLeadForm] = useState(false)
  const [leadType, setLeadType] = useState<'training' | 'trip' | null>(null)
  const [leadSubmitting, setLeadSubmitting] = useState(false)
  const [leadError, setLeadError] = useState<string | null>(null)

  // Restore sessionId from localStorage on mount
  useEffect(() => {
    try {
      const storedSessionId = localStorage.getItem(STORAGE_KEY)
      if (storedSessionId && UUID_REGEX.test(storedSessionId)) {
        setSessionId(storedSessionId)
        if (process.env.NODE_ENV === 'development') {
          console.log('Session restored from localStorage:', storedSessionId)
        }
      } else if (storedSessionId) {
        localStorage.removeItem(STORAGE_KEY)
      }
    } catch (error) {
      console.warn('localStorage unavailable:', error)
    }
  }, [])

  // Save sessionId to localStorage when it changes
  useEffect(() => {
    if (sessionId) {
      try {
        localStorage.setItem(STORAGE_KEY, sessionId)
      } catch (error) {
        console.warn('Failed to save sessionId:', error)
      }
    }
  }, [sessionId])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle URL query parameter (e.g., from "Try this" suggestions)
  useEffect(() => {
    const query = searchParams.get('prompt')
    if (query && messages.length === 0 && !isLoading) {
      setInput(query)
      setTimeout(() => {
        const userMessage: Message = {
          id: crypto.randomUUID(),
          role: 'user',
          content: query,
          timestamp: new Date(),
        }

        setMessages([userMessage])
        setInput('')
        setIsLoading(true)
        setError(null)
        ;(async () => {
          try {
            const requestPayload: {
              sessionId?: string
              message: string
              sessionState?: Record<string, unknown>
            } = {
              sessionId: sessionId || undefined,
              message: query,
            }

            if (isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP)) {
              requestPayload.sessionState = sessionState as Record<
                string,
                unknown
              >
            }

            const response: ChatResponse = await apiClient.chat(requestPayload)

            if (!sessionId && response.sessionId) {
              setSessionId(response.sessionId)
            }

            if (
              isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP) &&
              response.metadata?.stateUpdates
            ) {
              updateSessionState(response.metadata.stateUpdates)
            }

            let messageContent = response.message
            if (
              isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP) &&
              response.followUpQuestion
            ) {
              messageContent = `${response.message}\n\n─────\n💬 ${response.followUpQuestion}`
            }

            const assistantMessage: Message = {
              id: crypto.randomUUID(),
              role: 'assistant',
              content: messageContent,
              timestamp: new Date(),
            }

            setMessages((prev) => [...prev, assistantMessage])
          } catch (err) {
            let errorMessage = 'An unexpected error occurred. Please try again.'
            if (err instanceof ApiClientError) {
              errorMessage = err.userMessage
              if (
                err.code === 'SESSION_EXPIRED' ||
                err.code === 'SESSION_NOT_FOUND'
              ) {
                clearSession()
                errorMessage =
                  'Your session has expired. Starting a new chat...'
              }
            }
            setError(errorMessage)
            setMessages((prev) =>
              prev.filter((msg) => msg.id !== userMessage.id)
            )
          } finally {
            setIsLoading(false)
          }
        })()
      }, 100)
    }
  }, [searchParams])

  const clearSession = () => {
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch (error) {
      console.warn('Failed to clear localStorage:', error)
    }
    setSessionId(null)
    setMessages([])
    setError(null)
    if (isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP)) {
      clearSessionState()
    }
  }

  const handleNewChat = () => {
    if (messages.length >= 2) {
      const confirmed = window.confirm(
        'Start a new chat? Your current conversation will be cleared.'
      )
      if (!confirmed) return
    }
    clearSession()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      const requestPayload: {
        sessionId?: string
        message: string
        sessionState?: Record<string, unknown>
      } = {
        sessionId: sessionId || undefined,
        message: userMessage.content,
      }

      if (isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP)) {
        requestPayload.sessionState = sessionState as Record<string, unknown>
      }

      const response: ChatResponse = await apiClient.chat(requestPayload)

      if (!sessionId && response.sessionId) {
        setSessionId(response.sessionId)
      }

      if (
        isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP) &&
        response.metadata?.stateUpdates
      ) {
        updateSessionState(response.metadata.stateUpdates)
      }

      // Check for lead capture triggers
      if (
        response.message.toLowerCase().includes('connect you') ||
        response.message.toLowerCase().includes('recommend a shop')
      ) {
        if (
          response.message.toLowerCase().includes('course') ||
          response.message.toLowerCase().includes('certification')
        ) {
          setLeadType('training')
        } else if (
          response.message.toLowerCase().includes('trip') ||
          response.message.toLowerCase().includes('liveaboard')
        ) {
          setLeadType('trip')
        }
      }

      let messageContent = response.message
      if (
        isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP) &&
        response.followUpQuestion
      ) {
        messageContent = `${response.message}\n\n─────\n💬 ${response.followUpQuestion}`
      }

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: messageContent,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      let errorMessage = 'An unexpected error occurred. Please try again.'

      if (err instanceof ApiClientError) {
        errorMessage = err.userMessage
        if (
          err.code === 'SESSION_EXPIRED' ||
          err.code === 'SESSION_NOT_FOUND'
        ) {
          clearSession()
          errorMessage = 'Your session has expired. Starting a new chat...'
        }
      }

      setError(errorMessage)
      setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id))
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleOpenLeadForm = (type: 'training' | 'trip') => {
    setLeadType(type)
    setShowLeadForm(true)
    setLeadError(null)
  }

  const handleCloseLeadForm = () => {
    if (!leadSubmitting) {
      setShowLeadForm(false)
      setLeadType(null)
      setLeadError(null)
    }
  }

  const handleLeadSubmit = async (data: LeadFormData) => {
    if (!sessionId) {
      setLeadError('Please start a conversation before submitting a lead.')
      return
    }

    setLeadSubmitting(true)
    setLeadError(null)

    try {
      let payload: Record<string, unknown> = {}

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
        }
        if (sessionId && UUID_REGEX.test(sessionId))
          payload.session_id = sessionId
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
        }
        if (sessionId && UUID_REGEX.test(sessionId))
          payload.session_id = sessionId
      }

      const response = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || 'Failed to submit lead')
      }

      setShowLeadForm(false)
      setLeadType(null)
      setLeadError(null)

      const confirmationMessage: Message = {
        id: crypto.randomUUID(),
        role: 'system',
        content: `✅ Thanks, ${data.name}! We'll contact you at ${data.email} soon. Feel free to keep asking questions.`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, confirmationMessage])
    } catch (err) {
      let errorMessage = 'Failed to submit. Please try again.'
      if (err instanceof Error) errorMessage = err.message
      setLeadError(errorMessage)
    } finally {
      setLeadSubmitting(false)
    }
  }

  return (
    <div className="flex flex-col h-full overflow-hidden bg-transparent">
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

      {/* Floating Action Buttons */}
      <div className="absolute top-4 right-16 flex gap-2 z-20 hidden md:flex">
        <button
          onClick={() => handleOpenLeadForm('training')}
          disabled={!sessionId}
          className={cn(
            'px-3 py-1.5 text-xs font-medium rounded-full border transition-all flex items-center gap-1.5',
            !sessionId
              ? 'border-border text-muted-foreground cursor-not-allowed opacity-50'
              : 'border-accent-200 bg-accent-50 text-accent-700 hover:bg-accent-100 hover:border-accent-300'
          )}
        >
          <GraduationCap size={14} />
          Get Certified
        </button>
        <button
          onClick={() => handleOpenLeadForm('trip')}
          disabled={!sessionId}
          className={cn(
            'px-3 py-1.5 text-xs font-medium rounded-full border transition-all flex items-center gap-1.5',
            !sessionId
              ? 'border-border text-muted-foreground cursor-not-allowed opacity-50'
              : 'border-primary-200 bg-primary-50 text-primary-700 hover:bg-primary-100 hover:border-primary-300'
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
            <h2 className="text-lg font-medium text-primary-900 mb-2">
              How can I help you dive today?
            </h2>
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
              'p-3 rounded-xl transition-all shadow-sm flex items-center justify-center',
              !input.trim() || isLoading
                ? 'bg-muted text-muted-foreground cursor-not-allowed'
                : 'bg-primary text-white hover:bg-primary-600 hover:shadow-md active:scale-95'
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

      <LeadCaptureModal
        isOpen={showLeadForm}
        onClose={handleCloseLeadForm}
        leadType={leadType}
        onSubmit={handleLeadSubmit}
        isSubmitting={leadSubmitting}
        error={leadError}
      />
    </div>
  )
}

export default function ChatPage() {
  return (
    <main className="relative min-h-screen">
      <WatercolorBackground />
      <div className="w-full max-w-4xl h-[calc(100vh-2rem)] my-4 mx-4 md:mx-auto glass-panel rounded-2xl overflow-hidden relative z-10">
        <Suspense
          fallback={
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
            </div>
          }
        >
          <ChatContent />
        </Suspense>
      </div>
    </main>
  )
}
