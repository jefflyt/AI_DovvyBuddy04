import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LeadCaptureModal } from '../LeadCaptureModal';

describe('LeadCaptureModal', () => {
  const mockOnClose = vi.fn();
  const mockOnSubmit = vi.fn();

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should not render when isOpen is false', () => {
    const { container } = render(
      <LeadCaptureModal
        isOpen={false}
        onClose={mockOnClose}
        leadType="training"
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        error={null}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  it('should render when isOpen is true', () => {
    render(
      <LeadCaptureModal
        isOpen={true}
        onClose={mockOnClose}
        leadType="training"
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        error={null}
      />
    );

    expect(screen.getByText('Get Certified')).toBeInTheDocument();
  });

  it('should render TrainingLeadForm when leadType is training', () => {
    render(
      <LeadCaptureModal
        isOpen={true}
        onClose={mockOnClose}
        leadType="training"
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        error={null}
      />
    );

    expect(screen.getByText('Get Certified')).toBeInTheDocument();
    expect(screen.getByText(/certification goals/i)).toBeInTheDocument();
  });

  it('should render TripLeadForm when leadType is trip', () => {
    render(
      <LeadCaptureModal
        isOpen={true}
        onClose={mockOnClose}
        leadType="trip"
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        error={null}
      />
    );

    expect(screen.getByText('Plan a Trip')).toBeInTheDocument();
    expect(screen.getByText(/trip details/i)).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', () => {
    render(
      <LeadCaptureModal
        isOpen={true}
        onClose={mockOnClose}
        leadType="training"
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        error={null}
      />
    );

    const closeButton = screen.getByLabelText('Close modal');
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should call onClose when backdrop is clicked', () => {
    const { container } = render(
      <LeadCaptureModal
        isOpen={true}
        onClose={mockOnClose}
        leadType="training"
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        error={null}
      />
    );

    // Click the backdrop (first child of container)
    const backdrop = container.firstChild as HTMLElement;
    fireEvent.click(backdrop);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should call onClose when ESC key is pressed', () => {
    render(
      <LeadCaptureModal
        isOpen={true}
        onClose={mockOnClose}
        leadType="training"
        onSubmit={mockOnSubmit}
        isSubmitting={false}
        error={null}
      />
    );

    fireEvent.keyDown(document, { key: 'Escape' });

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should not call onClose when submitting', () => {
    render(
      <LeadCaptureModal
        isOpen={true}
        onClose={mockOnClose}
        leadType="training"
        onSubmit={mockOnSubmit}
        isSubmitting={true}
        error={null}
      />
    );

    fireEvent.keyDown(document, { key: 'Escape' });

    expect(mockOnClose).not.toHaveBeenCalled();
  });

  it('should disable close button when submitting', () => {
    render(
      <LeadCaptureModal
        isOpen={true}
        onClose={mockOnClose}
        leadType="training"
        onSubmit={mockOnSubmit}
        isSubmitting={true}
        error={null}
      />
    );

    const closeButton = screen.getByLabelText('Close modal');
    expect(closeButton).toBeDisabled();
  });
});
