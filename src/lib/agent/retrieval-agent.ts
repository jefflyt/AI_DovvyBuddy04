/**
 * Retrieval Agent
 * Specialist for knowledge base search and context retrieval
 */

import { BaseAgent } from './base-agent';
import { vectorSearchTool } from './tools/vector-search-tool';
import { getGenkit } from './config';
import type { AgentInput, AgentOutput } from './types';

export class RetrievalAgent extends BaseAgent {
  constructor() {
    super(
      'retrieval',
      'Retrieval specialist for knowledge base search',
      [vectorSearchTool]
    );
  }

  async generate(input: AgentInput): Promise<AgentOutput> {
    const genkit = getGenkit();
    if (!genkit) {
      throw new Error('ADK not initialized');
    }

    // Extract the user's most recent message
    const lastMessage = input.messages[input.messages.length - 1];
    const prompt = `Find relevant information for: ${lastMessage.content}`;

    try {
      const result = await genkit.generate({
        model: process.env.ADK_RETRIEVAL_MODEL || 'gemini-1.5-flash',
        prompt,
        tools: this.tools,
      });

      return {
        content: result.text || '',
        toolCalls: result.toolCalls || [],
        metadata: { 
          tokensUsed: result.usage?.totalTokens,
          model: process.env.ADK_RETRIEVAL_MODEL || 'gemini-1.5-flash',
        },
      };
    } catch (error) {
      console.error('Retrieval agent error:', error);
      throw error;
    }
  }
}
