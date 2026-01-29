'use client';

import { useState } from 'react';
import { LeadFormData } from './LeadCaptureModal';

interface TrainingLeadFormProps {
  onSubmit: (data: LeadFormData) => Promise<void>;
  onCancel: () => void;
  isSubmitting: boolean;
  error: string | null;
}

export function TrainingLeadForm({
  onSubmit,
  onCancel,
  isSubmitting,
  error,
}: TrainingLeadFormProps) {
  const [formData, setFormData] = useState<LeadFormData>({
    name: '',
    email: '',
    phone: '',
    agency: 'No Preference',
    certificationLevel: 'None',
    location: '',
    message: '',
  });

  const [validationErrors, setValidationErrors] = useState<{
    name?: string;
    email?: string;
  }>({});

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    
    // Clear validation error when user starts typing
    if (validationErrors[name as keyof typeof validationErrors]) {
      setValidationErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation
    const errors: { name?: string; email?: string } = {};

    if (!formData.name?.trim()) {
      errors.name = 'Name is required';
    }

    if (!formData.email?.trim()) {
      errors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    // Submit form
    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1.5rem' }}>
        Get Certified
      </h2>

      <p style={{ fontSize: '0.875rem', color: '#666', marginBottom: '1.5rem' }}>
        Tell us about your certification goals and we&apos;ll connect you with a qualified dive shop.
      </p>

      {/* Error message */}
      {error && (
        <div
          style={{
            padding: '0.75rem',
            backgroundColor: '#fff0f0',
            border: '1px solid #ffcccc',
            borderRadius: '6px',
            marginBottom: '1rem',
            fontSize: '0.875rem',
            color: '#cc0000',
          }}
        >
          {error}
        </div>
      )}

      {/* Name field */}
      <div style={{ marginBottom: '1rem' }}>
        <label
          htmlFor="name"
          style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            marginBottom: '0.25rem',
          }}
        >
          Name <span style={{ color: '#cc0000' }}>*</span>
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          disabled={isSubmitting}
          style={{
            width: '100%',
            padding: '0.5rem',
            border: `1px solid ${validationErrors.name ? '#cc0000' : '#e5e5e5'}`,
            borderRadius: '6px',
            fontSize: '1rem',
            backgroundColor: isSubmitting ? '#f5f5f5' : 'white',
          }}
        />
        {validationErrors.name && (
          <p style={{ fontSize: '0.75rem', color: '#cc0000', marginTop: '0.25rem' }}>
            {validationErrors.name}
          </p>
        )}
      </div>

      {/* Email field */}
      <div style={{ marginBottom: '1rem' }}>
        <label
          htmlFor="email"
          style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            marginBottom: '0.25rem',
          }}
        >
          Email <span style={{ color: '#cc0000' }}>*</span>
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          disabled={isSubmitting}
          style={{
            width: '100%',
            padding: '0.5rem',
            border: `1px solid ${validationErrors.email ? '#cc0000' : '#e5e5e5'}`,
            borderRadius: '6px',
            fontSize: '1rem',
            backgroundColor: isSubmitting ? '#f5f5f5' : 'white',
          }}
        />
        {validationErrors.email && (
          <p style={{ fontSize: '0.75rem', color: '#cc0000', marginTop: '0.25rem' }}>
            {validationErrors.email}
          </p>
        )}
      </div>

      {/* Phone field (optional) */}
      <div style={{ marginBottom: '1rem' }}>
        <label
          htmlFor="phone"
          style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            marginBottom: '0.25rem',
          }}
        >
          Phone (optional)
        </label>
        <input
          type="tel"
          id="phone"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
          disabled={isSubmitting}
          placeholder="+1 234 567 8900"
          style={{
            width: '100%',
            padding: '0.5rem',
            border: '1px solid #e5e5e5',
            borderRadius: '6px',
            fontSize: '1rem',
            backgroundColor: isSubmitting ? '#f5f5f5' : 'white',
          }}
        />
      </div>

      {/* Agency preference */}
      <div style={{ marginBottom: '1rem' }}>
        <label
          htmlFor="agency"
          style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            marginBottom: '0.25rem',
          }}
        >
          Agency Preference
        </label>
        <select
          id="agency"
          name="agency"
          value={formData.agency}
          onChange={handleChange}
          disabled={isSubmitting}
          style={{
            width: '100%',
            padding: '0.5rem',
            border: '1px solid #e5e5e5',
            borderRadius: '6px',
            fontSize: '1rem',
            backgroundColor: isSubmitting ? '#f5f5f5' : 'white',
          }}
        >
          <option value="No Preference">No Preference</option>
          <option value="PADI">PADI</option>
          <option value="SSI">SSI</option>
        </select>
      </div>

      {/* Certification level */}
      <div style={{ marginBottom: '1rem' }}>
        <label
          htmlFor="certificationLevel"
          style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            marginBottom: '0.25rem',
          }}
        >
          Current Certification Level
        </label>
        <select
          id="certificationLevel"
          name="certificationLevel"
          value={formData.certificationLevel}
          onChange={handleChange}
          disabled={isSubmitting}
          style={{
            width: '100%',
            padding: '0.5rem',
            border: '1px solid #e5e5e5',
            borderRadius: '6px',
            fontSize: '1rem',
            backgroundColor: isSubmitting ? '#f5f5f5' : 'white',
          }}
        >
          <option value="None">None (New Diver)</option>
          <option value="Open Water">Open Water</option>
          <option value="Advanced Open Water">Advanced Open Water</option>
          <option value="Rescue Diver">Rescue Diver</option>
          <option value="Divemaster">Divemaster</option>
        </select>
      </div>

      {/* Location preference */}
      <div style={{ marginBottom: '1rem' }}>
        <label
          htmlFor="location"
          style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            marginBottom: '0.25rem',
          }}
        >
          Preferred Location (optional)
        </label>
        <input
          type="text"
          id="location"
          name="location"
          value={formData.location}
          onChange={handleChange}
          disabled={isSubmitting}
          placeholder="e.g., Singapore, Phuket, Bali"
          style={{
            width: '100%',
            padding: '0.5rem',
            border: '1px solid #e5e5e5',
            borderRadius: '6px',
            fontSize: '1rem',
            backgroundColor: isSubmitting ? '#f5f5f5' : 'white',
          }}
        />
      </div>

      {/* Additional message */}
      <div style={{ marginBottom: '1.5rem' }}>
        <label
          htmlFor="message"
          style={{
            display: 'block',
            fontSize: '0.875rem',
            fontWeight: '500',
            marginBottom: '0.25rem',
          }}
        >
          Additional Information (optional)
        </label>
        <textarea
          id="message"
          name="message"
          value={formData.message}
          onChange={handleChange}
          disabled={isSubmitting}
          rows={3}
          placeholder="Any specific questions or requirements?"
          style={{
            width: '100%',
            padding: '0.5rem',
            border: '1px solid #e5e5e5',
            borderRadius: '6px',
            fontSize: '1rem',
            resize: 'vertical',
            backgroundColor: isSubmitting ? '#f5f5f5' : 'white',
            fontFamily: 'inherit',
          }}
        />
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: 'transparent',
            color: '#666',
            border: '1px solid #e5e5e5',
            borderRadius: '6px',
            fontSize: '1rem',
            fontWeight: '500',
            cursor: isSubmitting ? 'not-allowed' : 'pointer',
            opacity: isSubmitting ? 0.5 : 1,
          }}
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: isSubmitting ? '#cccccc' : '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '1rem',
            fontWeight: '500',
            cursor: isSubmitting ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          {isSubmitting ? (
            <>
              <span
                style={{
                  display: 'inline-block',
                  width: '1rem',
                  height: '1rem',
                  border: '2px solid white',
                  borderTopColor: 'transparent',
                  borderRadius: '50%',
                  animation: 'spin 0.8s linear infinite',
                }}
              />
              Submitting...
            </>
          ) : (
            'Submit'
          )}
        </button>
      </div>

      <style jsx>{`
        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </form>
  );
}
