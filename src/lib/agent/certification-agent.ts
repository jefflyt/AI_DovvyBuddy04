/**
 * Certification Agent
 * Specialist in diving certification queries (PADI/SSI equivalency, prerequisites, etc.)
 */

import { BaseAgent } from './base-agent';
import { vectorSearchTool, sessionLookupTool } from './tools';
import { getGenkit } from './config';
import type { AgentInput, AgentOutput } from './types';

export class CertificationAgent extends BaseAgent {
  constructor() {
    super(
      'certification',
      'Specialist in diving certification queries',
      [vectorSearchTool, sessionLookupTool]
    );
  }

  async generate(input: AgentInput): Promise<AgentOutput> {
    const genkit = getGenkit();
    if (!genkit) {
      throw new Error('ADK not initialized');
    }

    const systemPrompt = `You are a diving certification expert for DovvyBuddy.

Focus on:
- PADI/SSI equivalency and differences
- Course prerequisites and requirements
- Training duration and structure
- Certification levels (Open Water, Advanced, Rescue, Divemaster)
- Safety requirements and medical considerations

Include appropriate disclaimers:
- Medical topics: "Consult a dive medical professional (DAN) for health-related concerns"
- Depth limits: Always state certification-appropriate max depths
- Legal topics: "This is not legal advice"

Use tools to retrieve context from the knowledge base and conversation history.`;

    const conversationText = input.messages
      .map((m) => `${m.role}: ${m.content}`)
      .join('\n');

    const fullPrompt = `${systemPrompt}\n\n${conversationText}`;

    try {
      const result = await genkit.generate({
        model: process.env.ADK_SPECIALIST_MODEL || 'gemini-2.0-flash',
        prompt: fullPrompt,
        tools: this.tools,
      });

      return {
        content: result.text || '',
        toolCalls: result.toolCalls || [],
        metadata: { 
          tokensUsed: result.usage?.totalTokens,
          model: process.env.ADK_SPECIALIST_MODEL || 'gemini-1.5-pro',
        },
      };
    } catch (error) {
      console.error('Certification agent error:', error);
      throw error;
    }
  }
}
