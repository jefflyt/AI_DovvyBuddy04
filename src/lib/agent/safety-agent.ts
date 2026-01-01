/**
 * Safety Agent
 * Validates responses for safety disclaimers and appropriate warnings
 */

import { BaseAgent } from './base-agent';
import { safetyCheckTool } from './tools';
import { getGenkit } from './config';
import type { AgentInput, AgentOutput } from './types';

export class SafetyAgent extends BaseAgent {
  constructor() {
    super(
      'safety',
      'Validates responses for safety disclaimers',
      [safetyCheckTool]
    );
  }

  async generate(input: AgentInput): Promise<AgentOutput> {
    const genkit = getGenkit();
    if (!genkit) {
      throw new Error('ADK not initialized');
    }

    const systemPrompt = `You are a safety validation agent for DovvyBuddy.

Your job is to check if responses include appropriate disclaimers for:
- Medical topics: "Consult a dive medical professional (DAN) for health-related concerns"
- Depth limits: State certification-appropriate max depth (OW: 18m, AOW: 30m, etc.)
- Legal topics: "This is not legal advice. Consult appropriate professionals."

Use the safety check tool to validate the response and suggest any missing disclaimers.`;

    const conversationText = input.messages
      .map((m) => `${m.role}: ${m.content}`)
      .join('\n');

    const fullPrompt = `${systemPrompt}\n\n${conversationText}`;

    try {
      const result = await genkit.generate({
        model: process.env.ADK_SAFETY_MODEL || 'gemini-1.5-flash',
        prompt: fullPrompt,
        tools: this.tools,
      });

      return {
        content: result.text || '',
        toolCalls: result.toolCalls || [],
        metadata: { 
          tokensUsed: result.usage?.totalTokens,
          model: process.env.ADK_SAFETY_MODEL || 'gemini-1.5-flash',
        },
      };
    } catch (error) {
      console.error('Safety agent error:', error);
      throw error;
    }
  }
}
