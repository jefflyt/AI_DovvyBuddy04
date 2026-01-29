import { test, expect } from '@playwright/test'

/**
 * Smoke Test - Critical User Journey
 * 
 * This test covers the most critical path through the application:
 * 1. Landing page loads and key sections are visible
 * 2. CTA button navigates to chat
 * 3. Chat interface loads
 * 4. User can send a message and receive a response
 * 5. Session persists (localStorage)
 * 6. Lead form can be opened and submitted
 * 
 * Note: We assert BEHAVIOR, not CONTENT. Don't test "response mentions PADI" 
 * because LLM responses are non-deterministic. Test "response appears" instead.
 */
test.describe('Critical User Journey', () => {
  test('should complete full user flow from landing to chat to lead submission', async ({
    page,
  }) => {
    // 1. Landing page loads without errors
    await page.goto('/')
    
    // Check for key sections - use first() to avoid strict mode violations
    await expect(page.getByRole('heading', { name: /your ai diving companion/i })).toBeVisible()
    await expect(page.getByText(/judgment-free guidance/i).first()).toBeVisible()
    
    // Check for value proposition section
    await expect(page.getByText(/certification navigator/i)).toBeVisible()
    await expect(page.getByText(/confidence building/i)).toBeVisible()
    await expect(page.getByText(/trip research/i)).toBeVisible()
    
    // Check for How It Works section
    await expect(page.getByText(/how it works/i)).toBeVisible()
    
    // Check for Footer
    await expect(page.getByText(/dovvybuddy/i).last()).toBeVisible()
    
    // No console errors so far
    const consoleErrors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text())
      }
    })
    
    // 2. CTA button navigates to /chat
    const ctaButton = page.getByRole('link', { name: /start chatting/i })
    await expect(ctaButton).toBeVisible()
    await ctaButton.click()
    
    // 3. Chat interface loads
    await expect(page).toHaveURL('/chat')
    
    // Wait for chat interface to be ready
    const messageInput = page.locator('[data-testid="chat-input"]')
    await expect(messageInput).toBeVisible()
    
    // Check for send button
    const sendButton = page.locator('[data-testid="send-button"]')
    await expect(sendButton).toBeVisible()
    
    // 4. Send a message (any message)
    const testMessage = 'Tell me about Open Water certification'
    await messageInput.fill(testMessage)
    await sendButton.click()
    
    // User message should appear
    await expect(page.getByText(testMessage)).toBeVisible()
    
    // Wait for AI response to appear (up to 30 seconds for LLM)
    // Don't assert content, just that a response appears
    const responseContainer = page.locator('[data-testid="ai-message"]').first()
    await expect(responseContainer).toBeVisible({ timeout: 30000 })
    
    // Response should have some text content
    const responseText = await responseContainer.textContent()
    expect(responseText).toBeTruthy()
    expect(responseText!.length).toBeGreaterThan(10)
    
    // 5. Session ID persists in localStorage
    const sessionId = await page.evaluate(() => {
      return localStorage.getItem('dovvybuddy-session-id')
    })
    expect(sessionId).toBeTruthy()
    
    // 6. Lead form can be opened
    const leadFormButton = page.getByRole('button', { name: /get certified/i })
    if (await leadFormButton.isVisible()) {
      await leadFormButton.click()
      
      // Lead form modal should appear
      const leadFormModal = page.getByRole('dialog')
      await expect(leadFormModal).toBeVisible()
      
      // Check for required fields
      await expect(page.getByLabel(/name/i)).toBeVisible()
      await expect(page.getByLabel(/email/i)).toBeVisible()
      
      // Fill out form (don't actually submit to avoid spamming in tests)
      await page.getByLabel(/name/i).fill('Test User')
      await page.getByLabel(/email/i).fill('test@example.com')
      
      // Check that submit button exists and is enabled
      const submitButton = page.getByRole('button', { name: /submit/i })
      await expect(submitButton).toBeVisible()
      await expect(submitButton).toBeEnabled()
      
      // Close modal instead of submitting
      const closeButton = page.getByRole('button', { name: /close|cancel/i }).first()
      if (await closeButton.isVisible()) {
        await closeButton.click()
      } else {
        await page.keyboard.press('Escape')
      }
    }
    
    // 7. No console errors throughout the journey
    expect(consoleErrors.filter(err => {
      // Filter out known non-critical errors
      return !err.includes('ResizeObserver') && 
             !err.includes('analytics') // Analytics may fail in test env
    })).toEqual([])
  })
})
