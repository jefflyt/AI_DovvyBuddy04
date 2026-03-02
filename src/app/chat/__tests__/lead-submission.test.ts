import { describe, expect, it } from 'vitest'
import { ApiClientError } from '@/lib/api-client'

import {
  buildLeadRequest,
  getLeadSubmissionErrorMessage,
} from '../lead-submission'

describe('lead submission helpers', () => {
  it('maps training form data to backend lead payload', () => {
    const payload = buildLeadRequest(
      'training',
      {
        name: 'John Doe',
        email: 'john@example.com',
        phone: '  +123456789  ',
        certificationLevel: ' Open Water ',
        location: ' Singapore ',
        message: '  Looking for classes  ',
      },
      '123e4567-e89b-12d3-a456-426614174000'
    )

    expect(payload).toEqual({
      type: 'training',
      data: {
        name: 'John Doe',
        email: 'john@example.com',
        phone: '+123456789',
        certification_level: 'Open Water',
        preferred_location: 'Singapore',
        message: 'Looking for classes',
      },
      session_id: '123e4567-e89b-12d3-a456-426614174000',
    })
  })

  it('maps trip form data to backend lead payload', () => {
    const payload = buildLeadRequest('trip', {
      name: 'Jane Doe',
      email: 'jane@example.com',
      destination: ' Tioman ',
      dates: ' June 2026 ',
      message: ' 2 divers ',
    })

    expect(payload).toEqual({
      type: 'trip',
      data: {
        name: 'Jane Doe',
        email: 'jane@example.com',
        phone: undefined,
        destination: 'Tioman',
        travel_dates: 'June 2026',
        message: '2 divers',
      },
    })
  })

  it('returns user-friendly message for ApiClientError', () => {
    const error = new ApiClientError(
      'NETWORK_ERROR',
      0,
      'Network error: Failed to fetch'
    )
    expect(getLeadSubmissionErrorMessage(error)).toBe(
      'Unable to connect to the server. Please check your internet connection.'
    )
  })

  it('returns plain Error message for generic errors', () => {
    expect(getLeadSubmissionErrorMessage(new Error('Service unavailable'))).toBe(
      'Service unavailable'
    )
  })

  it('falls back to default message for unknown errors', () => {
    expect(getLeadSubmissionErrorMessage({})).toBe(
      'Failed to submit. Please try again.'
    )
  })
})
