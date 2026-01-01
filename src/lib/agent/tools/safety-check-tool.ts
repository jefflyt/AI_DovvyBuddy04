/**
 * Safety Check Tool
 * Validates responses for required safety disclaimers
 */

import type { Tool } from '../types';

export const safetyCheckTool: Tool = {
  name: 'validate_safety',
  description: 'Check response for required safety disclaimers',
  parameters: {
    response: { type: 'string' },
    query: { type: 'string' },
  },
  async execute(params: { response: string; query: string }) {
    const warnings: string[] = [];
    const response = params.response.toLowerCase();
    const query = params.query.toLowerCase();

    // Medical terms check
    const medicalTerms = [
      'medical',
      'doctor',
      'prescription',
      'diagnosis',
      'health condition',
      'medication',
      'surgery',
      'heart',
      'lung',
      'asthma',
    ];
    if (medicalTerms.some((term) => response.includes(term) || query.includes(term))) {
      if (!response.includes('consult') && !response.includes('medical professional')) {
        warnings.push('Add medical disclaimer');
      }
    }

    // Depth limits check
    const depthMention = /(\d+)\s*(m|meter|metre|ft|feet)/i.exec(params.response);
    if (depthMention) {
      const depth = parseInt(depthMention[1], 10);
      if (
        depth > 18 &&
        !response.includes('certification') &&
        !response.includes('advanced')
      ) {
        warnings.push('Mention certification requirements for depth');
      }
    }

    // Legal terms check
    const legalTerms = ['lawsuit', 'liability', 'insurance', 'legal', 'contract'];
    if (legalTerms.some((term) => response.includes(term) || query.includes(term))) {
      if (!response.includes('not legal advice')) {
        warnings.push('Add legal disclaimer');
      }
    }

    return {
      safe: warnings.length === 0,
      warnings,
      suggestions: warnings.map((w) => {
        if (w.includes('medical'))
          return 'Consult a dive medical professional (DAN) for health-related concerns.';
        if (w.includes('legal'))
          return 'This is not legal advice. Consult appropriate professionals.';
        if (w.includes('certification'))
          return 'Ensure dive plan matches certification level and experience.';
        return '';
      }),
    };
  },
};

