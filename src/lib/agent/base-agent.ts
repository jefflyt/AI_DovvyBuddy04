/**
 * Base Agent abstract class
 * Provides common structure for all specialized agents
 */

import type { Agent, AgentInput, AgentOutput, Tool } from './types';

export abstract class BaseAgent implements Agent {
  constructor(
    public name: string,
    public description: string,
    public tools: Tool[] = []
  ) {}

  abstract generate(input: AgentInput): Promise<AgentOutput>;
}
