import type { ChatResponse } from '@/shared/lib/api-client'

export type LeadCaptureType = 'training' | 'trip'

interface AutoSubmitPromptOptions {
  prompt: string | null
  handledPrompt: string | null
  isLoading: boolean
  hasSessionHydrated: boolean
  messagesLength: number
}

export function shouldAutoSubmitPrompt({
  prompt,
  handledPrompt,
  isLoading,
  hasSessionHydrated,
  messagesLength,
}: AutoSubmitPromptOptions): boolean {
  return Boolean(
    prompt &&
      prompt.trim() &&
      prompt !== handledPrompt &&
      hasSessionHydrated &&
      !isLoading &&
      messagesLength === 0
  )
}

export function getLeadCaptureType(message: string): LeadCaptureType | null {
  const normalizedMessage = message.toLowerCase()
  const shouldTriggerLeadCapture =
    normalizedMessage.includes('connect you') ||
    normalizedMessage.includes('recommend a shop')

  if (!shouldTriggerLeadCapture) {
    return null
  }

  if (
    normalizedMessage.includes('course') ||
    normalizedMessage.includes('certification')
  ) {
    return 'training'
  }

  if (
    normalizedMessage.includes('trip') ||
    normalizedMessage.includes('liveaboard')
  ) {
    return 'trip'
  }

  return null
}

export function formatAssistantMessageContent(
  response: Pick<ChatResponse, 'message' | 'followUpQuestion'>,
  showFollowUpQuestion: boolean
): string {
  if (showFollowUpQuestion && response.followUpQuestion) {
    return `${response.message}\n\n─────\n💬 ${response.followUpQuestion}`
  }

  return response.message
}
