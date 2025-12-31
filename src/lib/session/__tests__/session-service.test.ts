/**
 * Unit tests for Session Service
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  createSession,
  getSession,
  isSessionExpired,
} from '../session-service';
import type { SessionData, DiverProfile } from '../types';

// Mock the database
vi.mock('@/db/client', () => ({
  db: {
    insert: vi.fn(),
    select: vi.fn(),
    update: vi.fn(),
  },
}));

// Mock the schema
vi.mock('@/db/schema/sessions', () => ({
  sessions: {
    id: 'id',
    diverProfile: 'diverProfile',
    conversationHistory: 'conversationHistory',
    expiresAt: 'expiresAt',
  },
}));

import { db } from '@/db/client';

describe('Session Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('createSession', () => {
    it('should create a new session with default values', async () => {
      const mockSession = {
        id: 'test-uuid',
        diverProfile: {},
        conversationHistory: [],
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
      };

      const mockInsert = vi.fn().mockReturnValue({
        values: vi.fn().mockReturnValue({
          returning: vi.fn().mockResolvedValue([mockSession]),
        }),
      });

      (db.insert as any) = mockInsert;

      const result = await createSession();

      expect(result).toMatchObject({
        id: mockSession.id,
        conversationHistory: [],
        diverProfile: {},
      });
      expect(mockInsert).toHaveBeenCalled();
    });

    it('should create session with diver profile', async () => {
      const diverProfile: DiverProfile = {
        certificationLevel: 'Open Water',
        diveCount: 10,
        interests: ['wrecks', 'marine life'],
      };

      const mockSession = {
        id: 'test-uuid',
        diverProfile,
        conversationHistory: [],
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
      };

      const mockInsert = vi.fn().mockReturnValue({
        values: vi.fn().mockReturnValue({
          returning: vi.fn().mockResolvedValue([mockSession]),
        }),
      });

      (db.insert as any) = mockInsert;

      const result = await createSession({ diverProfile });

      expect(result.diverProfile).toEqual(diverProfile);
    });

    it('should handle database errors', async () => {
      const mockInsert = vi.fn().mockReturnValue({
        values: vi.fn().mockReturnValue({
          returning: vi.fn().mockRejectedValue(new Error('Database error')),
        }),
      });

      (db.insert as any) = mockInsert;

      await expect(createSession()).rejects.toThrow('Failed to create session');
    });
  });

  describe('getSession', () => {
    it('should retrieve existing non-expired session', async () => {
      const mockSession = {
        id: 'test-uuid',
        diverProfile: {},
        conversationHistory: [
          { role: 'user', content: 'Hello', timestamp: new Date().toISOString() },
        ],
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
      };

      const mockSelect = vi.fn().mockReturnValue({
        from: vi.fn().mockReturnValue({
          where: vi.fn().mockReturnValue({
            limit: vi.fn().mockResolvedValue([mockSession]),
          }),
        }),
      });

      (db.select as any) = mockSelect;

      const result = await getSession('test-uuid');

      expect(result).toMatchObject({
        id: mockSession.id,
        conversationHistory: mockSession.conversationHistory,
      });
    });

    it('should return null for expired session', async () => {
      const mockSession = {
        id: 'test-uuid',
        diverProfile: {},
        conversationHistory: [],
        createdAt: new Date(),
        expiresAt: new Date(Date.now() - 1000), // Expired
      };

      const mockSelect = vi.fn().mockReturnValue({
        from: vi.fn().mockReturnValue({
          where: vi.fn().mockReturnValue({
            limit: vi.fn().mockResolvedValue([mockSession]),
          }),
        }),
      });

      (db.select as any) = mockSelect;

      const result = await getSession('test-uuid');

      expect(result).toBeNull();
    });

    it('should return null for non-existent session', async () => {
      const mockSelect = vi.fn().mockReturnValue({
        from: vi.fn().mockReturnValue({
          where: vi.fn().mockReturnValue({
            limit: vi.fn().mockResolvedValue([]),
          }),
        }),
      });

      (db.select as any) = mockSelect;

      const result = await getSession('non-existent-uuid');

      expect(result).toBeNull();
    });

    it('should return null for invalid UUID format', async () => {
      const result = await getSession('invalid-uuid');

      expect(result).toBeNull();
    });
  });

  describe('isSessionExpired', () => {
    it('should return true for expired session', () => {
      const session: SessionData = {
        id: 'test-uuid',
        conversationHistory: [],
        diverProfile: {},
        createdAt: new Date(),
        expiresAt: new Date(Date.now() - 1000),
      };

      expect(isSessionExpired(session)).toBe(true);
    });

    it('should return false for non-expired session', () => {
      const session: SessionData = {
        id: 'test-uuid',
        conversationHistory: [],
        diverProfile: {},
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
      };

      expect(isSessionExpired(session)).toBe(false);
    });
  });
});
