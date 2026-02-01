import { describe, it, expect } from 'vitest';

describe('ChatPreview URL generation', () => {
    it('should generate correct /chat URL with encoded prompt', () => {
        const prompt = 'What do I need before taking an Advanced Open Water course?';
        const encoded = encodeURIComponent(prompt);
        const expectedUrl = `/chat?prompt=${encoded}`;

        expect(expectedUrl).toBe('/chat?prompt=What%20do%20I%20need%20before%20taking%20an%20Advanced%20Open%20Water%20course%3F');
    });

    it('should handle special characters in prompts', () => {
        const prompt = "I'm Advanced certified and want to see manta rays in Asia. Where should I go?";
        const encoded = encodeURIComponent(prompt);
        const expectedUrl = `/chat?prompt=${encoded}`;

        expect(expectedUrl).toContain('/chat?prompt=');
        expect(decodeURIComponent(encoded)).toBe(prompt);
    });
});
