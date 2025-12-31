/**
 * Unit tests for Prompt Detection
 */

import { describe, it, expect } from 'vitest';
import { detectPromptMode } from '../index';

describe('Prompt Detection', () => {
  describe('detectPromptMode', () => {
    it('should detect certification mode from keywords', () => {
      const certMessages = [
        'What is Open Water certification?',
        'How do I get PADI certified?',
        'Tell me about SSI Advanced course',
        'What are the prerequisites for Rescue Diver?',
        'How long does Divemaster training take?',
        'Do I need a license to dive?',
      ];

      certMessages.forEach((message) => {
        const mode = detectPromptMode(message, []);
        expect(mode).toBe('certification');
      });
    });

    it('should detect trip mode from keywords', () => {
      const tripMessages = [
        'Where should I dive in Tioman?',
        'Best dive sites for beginners?',
        'Recommend a destination for wreck diving',
        'When is the best time to visit Thailand?',
        'What marine life can I see in Indonesia?',
        'Is this dive site suitable for Open Water divers?',
      ];

      tripMessages.forEach((message) => {
        const mode = detectPromptMode(message, []);
        expect(mode).toBe('trip');
      });
    });

    it('should prefer trip mode when both keywords present', () => {
      const message =
        'I have Open Water certification, where should I go for my first trip?';
      const mode = detectPromptMode(message, []);

      expect(mode).toBe('trip');
    });

    it('should detect mode from conversation history', () => {
      const message = 'Tell me more about that';
      const history = [
        { role: 'user', content: 'What certifications do I need?' },
        { role: 'assistant', content: 'You should start with Open Water...' },
      ];

      const mode = detectPromptMode(message, history);

      expect(mode).toBe('certification');
    });

    it('should return general mode for ambiguous messages', () => {
      const generalMessages = [
        'Hello',
        'Thanks!',
        'Can you help me?',
        'What can you do?',
        'I have a question',
      ];

      generalMessages.forEach((message) => {
        const mode = detectPromptMode(message, []);
        expect(mode).toBe('general');
      });
    });

    it('should handle empty conversation history', () => {
      const message = 'What is Open Water certification?';
      const mode = detectPromptMode(message, []);

      expect(mode).toBe('certification');
    });

    it('should be case-insensitive', () => {
      const messages = [
        'WHAT IS OPEN WATER CERTIFICATION?',
        'where should i dive in TIOMAN?',
        'Tell Me About PADI',
      ];

      expect(detectPromptMode(messages[0], [])).toBe('certification');
      expect(detectPromptMode(messages[1], [])).toBe('trip');
      expect(detectPromptMode(messages[2], [])).toBe('certification');
    });
  });
});
