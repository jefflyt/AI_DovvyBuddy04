#!/usr/bin/env tsx
/**
 * Enable required PostgreSQL extensions
 * Run this before the first migration
 */

import * as dotenv from 'dotenv';
import postgres from 'postgres';

// Load environment variables
dotenv.config({ path: '.env.local' });

if (!process.env.DATABASE_URL) {
  console.error('❌ DATABASE_URL environment variable is required');
  process.exit(1);
}

async function enableExtensions() {
  const sql = postgres(process.env.DATABASE_URL!, { max: 1 });

  try {
    console.log('🔧 Enabling PostgreSQL extensions...');

    // Enable pgvector extension
    await sql`CREATE EXTENSION IF NOT EXISTS vector`;
    console.log('✅ pgvector extension enabled');

    console.log('✅ All extensions enabled successfully');
  } catch (error) {
    console.error('❌ Failed to enable extensions:', error);
    process.exit(1);
  } finally {
    await sql.end();
  }
}

enableExtensions();
