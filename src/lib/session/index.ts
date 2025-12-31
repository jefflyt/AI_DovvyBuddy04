/**
 * Session Service public API
 * Exports session management functions and types
 */

export {
  createSession,
  getSession,
  updateSessionHistory,
  expireSession,
  isSessionExpired,
  updateDiverProfile,
} from './session-service';

export type {
  SessionData,
  SessionMessage,
  DiverProfile,
  CreateSessionInput,
  UpdateSessionInput,
} from './types';
