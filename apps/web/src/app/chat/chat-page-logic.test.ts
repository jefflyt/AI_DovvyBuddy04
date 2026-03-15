import { describe, expect, it } from 'vitest'

import {
  formatAssistantMessageContent,
  getLeadCaptureType,
  shouldAutoSubmitPrompt,
} from './chat-page-logic'

describe('chat page logic', () => {
  it('waits for session hydration before auto-submitting a prompt', () => {
    expect(
      shouldAutoSubmitPrompt({
        prompt: 'Plan a dive trip',
        handledPrompt: null,
        isLoading: false,
        hasSessionHydrated: false,
        messagesLength: 0,
      })
    ).toBe(false)

    expect(
      shouldAutoSubmitPrompt({
        prompt: 'Plan a dive trip',
        handledPrompt: null,
        isLoading: false,
        hasSessionHydrated: true,
        messagesLength: 0,
      })
    ).toBe(true)
  })

  it('does not auto-submit the same prompt twice', () => {
    expect(
      shouldAutoSubmitPrompt({
        prompt: 'Plan a dive trip',
        handledPrompt: 'Plan a dive trip',
        isLoading: false,
        hasSessionHydrated: true,
        messagesLength: 0,
      })
    ).toBe(false)
  })

  it('detects training lead prompts from assistant copy', () => {
    expect(
      getLeadCaptureType(
        'I can connect you with a shop that offers this certification course.'
      )
    ).toBe('training')
  })

  it('detects trip lead prompts from assistant copy', () => {
    expect(
      getLeadCaptureType(
        'I can recommend a shop that can help with your liveaboard trip.'
      )
    ).toBe('trip')
  })

  it('leaves normal replies without a lead trigger alone', () => {
    expect(getLeadCaptureType('Here is a neutral answer about buoyancy.')).toBe(
      null
    )
  })

  it('formats follow-up questions only when the feature is enabled', () => {
    const response = {
      message: 'Here is the answer.',
      followUpQuestion: 'What destination are you considering?',
    }

    expect(formatAssistantMessageContent(response, true)).toContain(
      response.followUpQuestion
    )
    expect(formatAssistantMessageContent(response, false)).toBe(
      response.message
    )
  })
})
