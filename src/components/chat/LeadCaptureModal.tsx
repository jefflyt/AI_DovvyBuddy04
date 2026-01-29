'use client';

import { useEffect } from 'react';
import { TrainingLeadForm } from './TrainingLeadForm.js';
import { TripLeadForm } from './TripLeadForm.js';

export interface LeadFormData {
  name: string;
  email: string;
  phone?: string;
  // Training specific
  agency?: string;
  certificationLevel?: string;
  location?: string;
  // Trip specific
  destination?: string;
  dates?: string;
  diveCount?: number;
  interests?: string[];
  // Common
  message?: string;
}

interface LeadCaptureModalProps {
  isOpen: boolean;
  onClose: () => void;
  leadType: 'training' | 'trip' | null;
  onSubmit: (data: LeadFormData) => Promise<void>;
  isSubmitting: boolean;
  error: string | null;
}

export function LeadCaptureModal({
  isOpen,
  onClose,
  leadType,
  onSubmit,
  isSubmitting,
  error,
}: LeadCaptureModalProps) {
  // Handle ESC key to close modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isSubmitting) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, isSubmitting, onClose]);

  if (!isOpen || !leadType) return null;

  // Handle backdrop click
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget && !isSubmitting) {
      onClose();
    }
  };

  return (
    <div
      onClick={handleBackdropClick}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '1rem',
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          maxWidth: '600px',
          width: '100%',
          maxHeight: 'calc(100vh - 2rem)',
          overflowY: 'auto',
          position: 'relative',
        }}
        // Mobile full-screen on small devices
        className="lead-modal-container"
      >
        {/* Close button */}
        <button
          onClick={onClose}
          disabled={isSubmitting}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            background: 'none',
            border: 'none',
            fontSize: '1.5rem',
            cursor: isSubmitting ? 'not-allowed' : 'pointer',
            color: '#666',
            padding: '0.25rem',
            lineHeight: 1,
            opacity: isSubmitting ? 0.5 : 1,
          }}
          aria-label="Close modal"
        >
          ×
        </button>

        {/* Modal content */}
        <div style={{ padding: '2rem' }}>
          {leadType === 'training' ? (
            <TrainingLeadForm
              onSubmit={onSubmit}
              onCancel={onClose}
              isSubmitting={isSubmitting}
              error={error}
            />
          ) : (
            <TripLeadForm
              onSubmit={onSubmit}
              onCancel={onClose}
              isSubmitting={isSubmitting}
              error={error}
            />
          )}
        </div>
      </div>

      <style jsx>{`
        @media (max-width: 768px) {
          .lead-modal-container {
            max-width: 100%;
            max-height: 100vh;
            border-radius: 0;
            margin: 0;
          }
        }
      `}</style>
    </div>
  );
}
