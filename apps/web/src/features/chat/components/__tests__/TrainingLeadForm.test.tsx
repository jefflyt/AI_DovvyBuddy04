import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { TrainingLeadForm } from '../TrainingLeadForm'

describe('TrainingLeadForm', () => {
  const mockOnSubmit = vi.fn()
  const mockOnCancel = vi.fn()

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should render all form fields', () => {
    render(
      <TrainingLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/phone/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/agency preference/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/certification level/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/location/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/additional information/i)).toBeInTheDocument()
  })

  it('should show validation error when name is empty', async () => {
    render(
      <TrainingLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    const submitButton = screen.getByRole('button', { name: /submit/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument()
    })

    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('should show validation error when email is empty', async () => {
    render(
      <TrainingLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    const nameInput = screen.getByLabelText(/name/i)
    fireEvent.change(nameInput, { target: { value: 'John Doe' } })

    const submitButton = screen.getByRole('button', { name: /submit/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    })

    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('should show validation error for invalid email format', async () => {
    render(
      <TrainingLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    const nameInput = screen.getByLabelText(/name/i)
    fireEvent.change(nameInput, { target: { value: 'John Doe' } })

    const emailInput = screen.getByLabelText(/email/i)
    fireEvent.change(emailInput, { target: { value: 'not-an-email' } })

    const submitButton = screen.getByRole('button', { name: /submit/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(
        screen.getByText(/please enter a valid email address/i)
      ).toBeInTheDocument()
    })

    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('should call onSubmit with correct data when form is valid', async () => {
    mockOnSubmit.mockResolvedValueOnce(undefined)

    render(
      <TrainingLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    const nameInput = screen.getByLabelText(/name/i)
    fireEvent.change(nameInput, { target: { value: 'John Doe' } })

    const emailInput = screen.getByLabelText(/email/i)
    fireEvent.change(emailInput, { target: { value: 'john@example.com' } })

    const phoneInput = screen.getByLabelText(/phone/i)
    fireEvent.change(phoneInput, { target: { value: '+1234567890' } })

    const agencySelect = screen.getByLabelText(/agency preference/i)
    fireEvent.change(agencySelect, { target: { value: 'PADI' } })

    const certificationSelect = screen.getByLabelText(/certification level/i)
    fireEvent.change(certificationSelect, { target: { value: 'Open Water' } })

    const locationInput = screen.getByLabelText(/location/i)
    fireEvent.change(locationInput, { target: { value: 'Singapore' } })

    const messageInput = screen.getByLabelText(/additional information/i)
    fireEvent.change(messageInput, {
      target: { value: 'Looking to get certified soon' },
    })

    const submitButton = screen.getByRole('button', { name: /submit/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com',
        phone: '+1234567890',
        agency: 'PADI',
        certificationLevel: 'Open Water',
        location: 'Singapore',
        message: 'Looking to get certified soon',
      })
    })
  })

  it('should call onCancel when cancel button is clicked', () => {
    render(
      <TrainingLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    fireEvent.click(cancelButton)

    expect(mockOnCancel).toHaveBeenCalledTimes(1)
  })

  it('should disable submit button when isSubmitting is true', () => {
    render(
      <TrainingLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={true}
        error={null}
      />
    )

    const submitButton = screen.getByRole('button', { name: /submitting/i })
    expect(submitButton).toBeDisabled()
  })

  it('should display error message when error prop is provided', () => {
    render(
      <TrainingLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error="Failed to submit. Please try again."
      />
    )

    expect(
      screen.getByText('Failed to submit. Please try again.')
    ).toBeInTheDocument()
  })

  it('should clear validation error when user starts typing', async () => {
    render(
      <TrainingLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    // Trigger validation error
    const submitButton = screen.getByRole('button', { name: /submit/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument()
    })

    // Start typing in name field
    const nameInput = screen.getByLabelText(/name/i)
    fireEvent.change(nameInput, { target: { value: 'John' } })

    // Error should be cleared
    await waitFor(() => {
      expect(screen.queryByText(/name is required/i)).not.toBeInTheDocument()
    })
  })
})
