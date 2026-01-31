/**
 * useSessionState Hook
 * 
 * Manages session state in localStorage for conversation continuity.
 * Provides graceful degradation if localStorage is unavailable.
 * 
 * PR6.1: Conversation Continuity
 */

import { useCallback, useEffect, useState } from 'react';

const STORAGE_KEY = 'dovvybuddy-session-state';

export interface SessionState {
  cert_level?: string | null; // "OW", "AOW", "DM", "Instructor", "unknown"
  context_mode?: string | null; // "learning", "planning", "briefing", "curiosity"
  location_known?: boolean;
  conditions_known?: boolean;
  last_intent?: string | null;
}

export interface UseSessionStateReturn {
  sessionState: SessionState;
  updateSessionState: (updates: Partial<SessionState>) => void;
  clearSessionState: () => void;
  isAvailable: boolean; // Whether localStorage is available
}

/**
 * Check if localStorage is available
 * (may be disabled in private browsing, or due to SecurityError)
 */
function isLocalStorageAvailable(): boolean {
  try {
    const test = '__localStorage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Read session state from localStorage
 */
function readSessionState(): SessionState {
  if (!isLocalStorageAvailable()) {
    return {};
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return {};
    }

    const parsed = JSON.parse(stored);
    return parsed as SessionState;
  } catch (error) {
    console.warn('Failed to read session state from localStorage:', error);
    return {};
  }
}

/**
 * Write session state to localStorage
 */
function writeSessionState(state: SessionState): void {
  if (!isLocalStorageAvailable()) {
    console.warn('localStorage unavailable, session state will not persist');
    return;
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (error) {
    console.warn('Failed to write session state to localStorage:', error);
  }
}

/**
 * Clear session state from localStorage
 */
function clearSessionStateStorage(): void {
  if (!isLocalStorageAvailable()) {
    return;
  }

  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.warn('Failed to clear session state from localStorage:', error);
  }
}

/**
 * Hook for managing session state
 * 
 * Usage:
 * ```tsx
 * const { sessionState, updateSessionState, clearSessionState } = useSessionState();
 * 
 * // Update state
 * updateSessionState({ cert_level: 'OW', context_mode: 'planning' });
 * 
 * // Clear state
 * clearSessionState();
 * ```
 */
export function useSessionState(): UseSessionStateReturn {
  const [isAvailable] = useState(isLocalStorageAvailable);
  const [sessionState, setSessionState] = useState<SessionState>(() => readSessionState());

  // Sync with localStorage on mount
  useEffect(() => {
    if (!isAvailable) {
      console.warn('localStorage unavailable, session state will not persist');
    }
  }, [isAvailable]);

  /**
   * Update session state (merges with existing state)
   */
  const updateSessionState = useCallback((updates: Partial<SessionState>) => {
    setSessionState((prev) => {
      const newState = { ...prev, ...updates };
      writeSessionState(newState);
      return newState;
    });
  }, []);

  /**
   * Clear session state
   */
  const clearSessionState = useCallback(() => {
    setSessionState({});
    clearSessionStateStorage();
  }, []);

  return {
    sessionState,
    updateSessionState,
    clearSessionState,
    isAvailable,
  };
}
