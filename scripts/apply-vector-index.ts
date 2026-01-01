/**
 * Apply vector index migration
 * Adds HNSW index for optimized similarity search
 */

import { sql } from '@/db/client';
import fs from 'fs';
import path from 'path';

async function applyMigration() {
  console.log('🚀 Applying vector index migration...');
  
  const migrationPath = path.join(process.cwd(), 'src/db/migrations/0002_add_vector_index.sql');
  const migrationSQL = fs.readFileSync(migrationPath, 'utf-8');
  
  try {
    await sql.unsafe(migrationSQL);
    console.log('✅ Vector index migration applied successfully');
    console.log('📊 Index: content_embeddings_vector_idx (HNSW, cosine distance)');
  } catch (error) {
    console.error('❌ Migration failed:', error);
    process.exit(1);
  } finally {
    await sql.end();
  }
}

applyMigration();
