/**
 * Trip Agent
 * Specialist in dive trip planning and destination recommendations
 */

import { BaseAgent } from './base-agent';
import { vectorSearchTool, sessionLookupTool } from './tools';
import { getGenkit } from './config';
import type { AgentInput, AgentOutput } from './types';

export class TripAgent extends BaseAgent {
  constructor() {
    super(
      'trip',
      'Specialist in dive trip planning and destinations',
      [vectorSearchTool, sessionLookupTool]
    );
  }

  async generate(input: AgentInput): Promise<AgentOutput> {
    const genkit = getGenkit();
    if (!genkit) {
      throw new Error('ADK not initialized');
    }

    const systemPrompt = `You are a dive trip planning expert for DovvyBuddy.

Focus on:
- Destination recommendations based on certification level and experience
- Dive site characteristics (depth, currents, visibility, marine life)
- Safety considerations (conditions, difficulty, hazards)
- Best seasons and accessibility
- Equipment requirements

Always consider:
- User's certification level (Open Water max 18m, Advanced max 30m)
- Logged dive experience
- Environmental conditions and seasonal factors
- Safety margins and dive planning

Use tools to retrieve context from the knowledge base and conversation history.`;

    const conversationText = input.messages
      .map((m) => `${m.role}: ${m.content}`)
      .join('\n');

    const fullPrompt = `${systemPrompt}\n\n${conversationText}`;

    try {
        const result = await genkit.generate({
          model: process.env.ADK_SPECIALIST_MODEL || 'gemini-2.0-flash',',
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
      console.error('Trip agent error:', error);
      throw error;
    }
  }
}
