import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { TripLeadForm } from '../TripLeadForm'

describe('TripLeadForm', () => {
  const mockOnSubmit = vi.fn()
  const mockOnCancel = vi.fn()

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should render all form fields', () => {
    render(
      <TripLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    expect(screen.getByLabelText(/^name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/phone/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/destination/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/travel dates/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/certification level/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/dive count/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/diving interests/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/additional information/i)).toBeInTheDocument()
  })

  it('should render all interest checkboxes', () => {
    render(
      <TripLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    expect(screen.getByLabelText(/^wrecks$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^reefs$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/marine life/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/macro/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/drift/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/night dives/i)).toBeInTheDocument()
  })

  it('should show validation error when name is empty', async () => {
    render(
      <TripLeadForm
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

  it('should show validation error when destination is empty', async () => {
    render(
      <TripLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    const nameInput = screen.getByLabelText(/^name/i)
    fireEvent.change(nameInput, { target: { value: 'Jane Doe' } })

    const emailInput = screen.getByLabelText(/^email/i)
    fireEvent.change(emailInput, { target: { value: 'jane@example.com' } })

    const submitButton = screen.getByRole('button', { name: /submit/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/destination is required/i)).toBeInTheDocument()
    })

    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('should handle interest checkboxes correctly', () => {
    render(
      <TripLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    const wrecksCheckbox = screen.getByLabelText(/^wrecks$/i)
    const reefsCheckbox = screen.getByLabelText(/^reefs$/i)

    // Initially unchecked
    expect(wrecksCheckbox).not.toBeChecked()
    expect(reefsCheckbox).not.toBeChecked()

    // Check wrecks
    fireEvent.click(wrecksCheckbox)
    expect(wrecksCheckbox).toBeChecked()

    // Check reefs
    fireEvent.click(reefsCheckbox)
    expect(reefsCheckbox).toBeChecked()

    // Uncheck wrecks
    fireEvent.click(wrecksCheckbox)
    expect(wrecksCheckbox).not.toBeChecked()
    expect(reefsCheckbox).toBeChecked()
  })

  it('should handle dive count as number input', () => {
    render(
      <TripLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    const diveCountInput = screen.getByLabelText(
      /dive count/i
    ) as HTMLInputElement

    fireEvent.change(diveCountInput, { target: { value: '25' } })
    expect(diveCountInput.value).toBe('25')
  })

  it('should call onSubmit with correct data including interests', async () => {
    mockOnSubmit.mockResolvedValueOnce(undefined)

    render(
      <TripLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    const nameInput = screen.getByLabelText(/^name/i)
    fireEvent.change(nameInput, { target: { value: 'Jane Smith' } })

    const emailInput = screen.getByLabelText(/^email/i)
    fireEvent.change(emailInput, { target: { value: 'jane@example.com' } })

    const destinationInput = screen.getByLabelText(/destination/i)
    fireEvent.change(destinationInput, { target: { value: 'Tioman' } })

    const datesInput = screen.getByLabelText(/travel dates/i)
    fireEvent.change(datesInput, { target: { value: 'June 2026' } })

    const diveCountInput = screen.getByLabelText(/dive count/i)
    fireEvent.change(diveCountInput, { target: { value: '25' } })

    // Select interests
    const wrecksCheckbox = screen.getByLabelText(/^wrecks$/i)
    const reefsCheckbox = screen.getByLabelText(/^reefs$/i)
    fireEvent.click(wrecksCheckbox)
    fireEvent.click(reefsCheckbox)

    const submitButton = screen.getByRole('button', { name: /submit/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Jane Smith',
          email: 'jane@example.com',
          destination: 'Tioman',
          dates: 'June 2026',
          certificationLevel: 'Open Water',
          diveCount: 25,
          interests: expect.arrayContaining(['Wrecks', 'Reefs']),
        })
      )
    })
  })

  it('should call onCancel when cancel button is clicked', () => {
    render(
      <TripLeadForm
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

  it('should disable all inputs when isSubmitting is true', () => {
    render(
      <TripLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={true}
        error={null}
      />
    )

    expect(screen.getByLabelText(/^name/i)).toBeDisabled()
    expect(screen.getByLabelText(/^email/i)).toBeDisabled()
    expect(screen.getByLabelText(/destination/i)).toBeDisabled()
    expect(screen.getByRole('button', { name: /submitting/i })).toBeDisabled()
  })

  it('should display error message when error prop is provided', () => {
    render(
      <TripLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error="Network error occurred."
      />
    )

    expect(screen.getByText('Network error occurred.')).toBeInTheDocument()
  })

  it('should handle empty dive count correctly', async () => {
    mockOnSubmit.mockResolvedValueOnce(undefined)

    render(
      <TripLeadForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        isSubmitting={false}
        error={null}
      />
    )

    const nameInput = screen.getByLabelText(/^name/i)
    fireEvent.change(nameInput, { target: { value: 'Test User' } })

    const emailInput = screen.getByLabelText(/^email/i)
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })

    const destinationInput = screen.getByLabelText(/destination/i)
    fireEvent.change(destinationInput, { target: { value: 'Bali' } })

    // Leave dive count empty
    const submitButton = screen.getByRole('button', { name: /submit/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          diveCount: undefined,
        })
      )
    })
  })
})
