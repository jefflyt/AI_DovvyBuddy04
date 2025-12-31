/**
 * Integration Test: Content Ingestion
 *
 * Tests the full ingestion pipeline with actual content files
 * Note: Requires database connection and may incur API costs
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { readFile } from 'fs/promises'
import { join } from 'path'
import matter from 'gray-matter'
import { db } from '../../src/db/client'
import { contentEmbeddings } from '../../src/db/schema'
import { chunkText } from '../../src/lib/rag/chunking'
import { eq } from 'drizzle-orm'

const CONTENT_DIR = join(process.cwd(), 'content')
const TEST_FILE = 'certifications/padi/open-water.md'

describe.skip('Content Ingestion Integration', () => {
  // Skip by default to avoid API costs during normal test runs
  // Run with: vitest run tests/integration/ingest-content.test.ts

  beforeAll(async () => {
    // Clean up any existing test data
    await db.delete(contentEmbeddings).where(eq(contentEmbeddings.contentPath, TEST_FILE))
  })

  afterAll(async () => {
    // Clean up test data
    await db.delete(contentEmbeddings).where(eq(contentEmbeddings.contentPath, TEST_FILE))
  })

  it('should read and parse markdown file', async () => {
    const filePath = join(CONTENT_DIR, TEST_FILE)
    const fileContent = await readFile(filePath, 'utf-8')
    const { data: frontmatter, content } = matter(fileContent)

    expect(frontmatter).toBeDefined()
    expect(frontmatter.doc_type).toBe('certification')
    expect(frontmatter.agency).toBe('PADI')
    expect(content).toBeTruthy()
  })

  it('should chunk markdown content', async () => {
    const filePath = join(CONTENT_DIR, TEST_FILE)
    const fileContent = await readFile(filePath, 'utf-8')
    const { data: frontmatter, content } = matter(fileContent)

    const chunks = chunkText(content, TEST_FILE, frontmatter)

    expect(chunks.length).toBeGreaterThan(0)
    expect(chunks[0].metadata.contentPath).toBe(TEST_FILE)
    expect(chunks[0].metadata.doc_type).toBe('certification')
  })

  // Add more integration tests here for actual ingestion
  // These would require GEMINI_API_KEY and would incur API costs
})
