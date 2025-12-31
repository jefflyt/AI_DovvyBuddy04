/**
 * Prompts public API
 * Exports system prompts and prompt builders
 */

export { BASE_SYSTEM_PROMPT, REFUSAL_PATTERNS } from './system-prompt';
export { buildCertificationPrompt } from './certification-prompt';
export { buildTripPrompt } from './trip-prompt';

/**
 * Determine the appropriate prompt mode based on user message
 * @param userMessage - User's input message
 * @param conversationHistory - Previous conversation context
 * @returns 'certification' | 'trip' | 'general'
 */
export function detectPromptMode(
  userMessage: string,
  conversationHistory: Array<{ role: string; content: string }>
): 'certification' | 'trip' | 'general' {
  const lowerMessage = userMessage.toLowerCase();

  // Certification-related keywords
  const certKeywords = [
    'certification',
    'certify',
    'certified',
    'license',
    'course',
    'training',
    'padi',
    'ssi',
    'naui',
    'open water',
    'advanced',
    'rescue',
    'divemaster',
    'instructor',
    'specialty',
    'nitrox',
    'deep diver',
    'prerequisite',
    'requirement',
  ];

  // Trip/destination-related keywords
  const tripKeywords = [
    'trip',
    'destination',
    'dive site',
    'where to dive',
    'travel',
    'visit',
    'recommend',
    'best place',
    'best time',
    'season',
    'marine life',
    'wreck',
    'reef',
    'visibility',
    'current',
    'beginner friendly',
    'tioman',
    'malaysia',
    'thailand',
    'indonesia',
  ];

  // Check for certification keywords
  const certMatches = certKeywords.filter((keyword) => lowerMessage.includes(keyword));
  const tripMatches = tripKeywords.filter((keyword) => lowerMessage.includes(keyword));

  // If both match, prefer trip mode (more specific)
  if (tripMatches.length > 0) {
    return 'trip';
  }

  if (certMatches.length > 0) {
    return 'certification';
  }

  // Check conversation history for context
  const recentMessages = conversationHistory.slice(-4); // Last 2 exchanges
  const historyText = recentMessages.map((m) => m.content.toLowerCase()).join(' ');

  if (certKeywords.some((keyword) => historyText.includes(keyword))) {
    return 'certification';
  }

  if (tripKeywords.some((keyword) => historyText.includes(keyword))) {
    return 'trip';
  }

  return 'general';
}
