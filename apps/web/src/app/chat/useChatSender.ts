/**
 * Custom hook for sending chat messages.
 * Encapsulates API call, session management, lead detection, and error handling.
 */

import { apiClient, type ChatResponse, ApiClientError } from '@/shared/lib/api-client'
import { FeatureFlag, isFeatureEnabled } from '@/shared/lib/feature-flags'
import { getLeadCaptureType, formatAssistantMessageContent } from './chat-page-logic'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

interface UseChatSenderDeps {
  sessionId: string | null
  setSessionId: (id: string | null) => void
  sessionState: Record<string, unknown> | null
  updateSessionState: (updates: Record<string, unknown>) => void
  setMessages: (fn: (prev: Message[]) => Message[]) => void
  setError: (error: string | null) => void
  setLeadType: (type: 'training' | 'trip' | null) => void
  setShowLeadForm: (show: boolean) => void
  clearSession: () => void
}

interface UseChatSenderResult {
  sendMessage: (content: string, userMessageId?: string) => Promise<void>
}

export function useChatSender(deps: UseChatSenderDeps): UseChatSenderResult {
  const {
    sessionId,
    setSessionId,
    sessionState,
    updateSessionState,
    setMessages,
    setError,
    setLeadType,
    setShowLeadForm,
    clearSession,
  } = deps

  const sendMessage = async (content: string, userMessageId?: string) => {
    const requestPayload: {
      sessionId?: string
      message: string
      sessionState?: Record<string, unknown>
    } = {
      sessionId: sessionId || undefined,
      message: content,
    }

    if (isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP)) {
      requestPayload.sessionState = sessionState as Record<string, unknown>
    }

    try {
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

      const autoLeadType = getLeadCaptureType(response.message)
      if (autoLeadType) {
        setLeadType(autoLeadType)
        setShowLeadForm(true)
      }

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: formatAssistantMessageContent(
          response,
          isFeatureEnabled(FeatureFlag.CONVERSATION_FOLLOWUP)
        ),
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
      if (userMessageId) {
        setMessages((prev) => prev.filter((msg) => msg.id !== userMessageId))
      }
    }
  }

  return { sendMessage }
}
