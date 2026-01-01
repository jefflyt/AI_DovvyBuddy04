/**
 * Agent Registry
 * Central registry for all specialized agents
 */

import { RetrievalAgent } from './retrieval-agent';
import { CertificationAgent } from './certification-agent';
import { TripAgent } from './trip-agent';
import { SafetyAgent } from './safety-agent';

const agents = {
  retrieval: new RetrievalAgent(),
  certification: new CertificationAgent(),
  trip: new TripAgent(),
  safety: new SafetyAgent(),
};

export function getAgent(name: string) {
  return agents[name as keyof typeof agents];
}

export { agents };
