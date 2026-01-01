/**
 * Agent and Tool type definitions for ADK integration
 */

export interface Agent {
  name: string;
  description: string;
  tools?: Tool[];
  generate(input: AgentInput): Promise<AgentOutput>;
}

export interface Tool {
  name: string;
  description: string;
  parameters: Record<string, any>;
  execute(params: any): Promise<any>;
}

export interface AgentInput {
  messages: Array<{ role: string; content: string }>;
  context?: string;
  sessionId?: string;
}

export interface AgentOutput {
  content: string;
  toolCalls?: Array<{ tool: string; params: any; result: any }>;
  metadata?: { tokensUsed?: number; model?: string };
}
