import { ApiClientError, type LeadRequest } from '@/lib/api-client'
import type { LeadFormData } from '@/components/chat/LeadCaptureModal'

type LeadType = 'training' | 'trip'

function toOptionalString(value?: string): string | undefined {
  const trimmed = value?.trim()
  return trimmed ? trimmed : undefined
}

export function buildLeadRequest(
  leadType: LeadType,
  data: LeadFormData,
  sessionId?: string
): LeadRequest {
  if (leadType === 'training') {
    return {
      type: 'training',
      data: {
        name: data.name,
        email: data.email,
        phone: toOptionalString(data.phone),
        certification_level: toOptionalString(data.certificationLevel),
        preferred_location: toOptionalString(data.location),
        message: toOptionalString(data.message),
      },
      ...(sessionId ? { session_id: sessionId } : {}),
    }
  }

  return {
    type: 'trip',
    data: {
      name: data.name,
      email: data.email,
      phone: toOptionalString(data.phone),
      destination: toOptionalString(data.destination),
      travel_dates: toOptionalString(data.dates),
      message: toOptionalString(data.message),
    },
    ...(sessionId ? { session_id: sessionId } : {}),
  }
}

export function getLeadSubmissionErrorMessage(error: unknown): string {
  if (error instanceof ApiClientError) {
    return error.userMessage
  }

  if (error instanceof Error && error.message.trim()) {
    return error.message
  }

  return 'Failed to submit. Please try again.'
}
