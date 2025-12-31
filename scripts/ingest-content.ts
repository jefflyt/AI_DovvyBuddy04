#!/usr/bin/env tsx
/**
 * Content Ingestion Script
 *
 * Reads markdown files from content/ directory, chunks text, generates embeddings,
 * and stores in content_embeddings table.
 *
 * Usage:
 *   pnpm content:ingest              # Ingest all content (skip already ingested)
 *   pnpm content:ingest --force      # Force re-ingest all content
 *   pnpm content:ingest --file path  # Ingest specific file
 */

import { readFile, readdir, stat } from 'fs/promises'
import { join, relative } from 'path'
import matter from 'gray-matter'
import { db } from '../src/db/client'
import { contentEmbeddings } from '../src/db/schema'
import { createEmbeddingProviderFromEnv } from '../src/lib/embeddings'
import { chunkText, freeTokenizer } from '../src/lib/rag/chunking'
import { eq } from 'drizzle-orm'

const CONTENT_DIR = join(process.cwd(), 'content')

interface IngestStats {
  filesProcessed: number
  filesSkipped: number
  chunksCreated: number
  errors: string[]
}

/**
 * Recursively find all markdown files in directory
 */
async function findMarkdownFiles(dir: string): Promise<string[]> {
  const files: string[] = []
  const entries = await readdir(dir, { withFileTypes: true })

  for (const entry of entries) {
    const fullPath = join(dir, entry.name)

    if (entry.isDirectory()) {
      // Skip hidden directories and node_modules
      if (entry.name.startsWith('.') || entry.name === 'node_modules') {
        continue
      }
      const subFiles = await findMarkdownFiles(fullPath)
      files.push(...subFiles)
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      // Skip README files (they are meta-documentation, not content)
      if (entry.name === 'README.md') {
        continue
      }
      files.push(fullPath)
    }
  }

  return files
}

/**
 * Check if file has already been ingested
 */
async function isFileIngested(contentPath: string): Promise<boolean> {
  const result = await db
    .select({ id: contentEmbeddings.id })
    .from(contentEmbeddings)
    .where(eq(contentEmbeddings.contentPath, contentPath))
    .limit(1)

  return result.length > 0
}

/**
 * Delete existing embeddings for a file
 */
async function deleteFileEmbeddings(contentPath: string): Promise<number> {
  const result = await db
    .delete(contentEmbeddings)
    .where(eq(contentEmbeddings.contentPath, contentPath))
    .returning({ id: contentEmbeddings.id })

  return result.length
}

/**
 * Ingest a single markdown file
 */
async function ingestFile(
  filePath: string,
  embeddingProvider: any,
  force: boolean = false
): Promise<{ chunks: number; skipped: boolean; error?: string }> {
  const contentPath = relative(CONTENT_DIR, filePath)

  try {
    // Check if already ingested (unless force)
    if (!force) {
      const alreadyIngested = await isFileIngested(contentPath)
      if (alreadyIngested) {
        console.log(`  ⏭️  Skipped (already ingested): ${contentPath}`)
        return { chunks: 0, skipped: true }
      }
    } else {
      // Delete existing embeddings for this file
      const deleted = await deleteFileEmbeddings(contentPath)
      if (deleted > 0) {
        console.log(`  🗑️  Deleted ${deleted} existing chunks: ${contentPath}`)
      }
    }

    // Read and parse markdown file
    const fileContent = await readFile(filePath, 'utf-8')
    const { data: frontmatter, content } = matter(fileContent)

    // Validate frontmatter
    if (!frontmatter.doc_type) {
      console.warn(`  ⚠️  Warning: Missing doc_type in frontmatter: ${contentPath}`)
    }

    // Chunk text
    const chunks = chunkText(content, contentPath, frontmatter)

    if (chunks.length === 0) {
      console.warn(`  ⚠️  Warning: No chunks created (empty content?): ${contentPath}`)
      return { chunks: 0, skipped: false }
    }

    console.log(`  📄 Processing: ${contentPath} (${chunks.length} chunks)`)

    // Generate embeddings and store
    for (let i = 0; i < chunks.length; i++) {
      const chunk = chunks[i]

      // Generate embedding
      const embedding = await embeddingProvider.generateEmbedding(chunk.text)

      // Verify embedding dimension
      const expectedDim = embeddingProvider.getDimension()
      if (embedding.length !== expectedDim) {
        throw new Error(
          `Embedding dimension mismatch: expected ${expectedDim}, got ${embedding.length}`
        )
      }

      // Store in database
      await db.insert(contentEmbeddings).values({
        contentPath: chunk.metadata.contentPath,
        chunkText: chunk.text,
        embedding: embedding, // Store as number array
        metadata: chunk.metadata,
      })

      // Log progress for large files
      if (chunks.length > 5 && (i + 1) % 5 === 0) {
        console.log(`    💾 Stored ${i + 1}/${chunks.length} chunks`)
      }
    }

    console.log(`  ✅ Completed: ${contentPath} (${chunks.length} chunks)`)

    return { chunks: chunks.length, skipped: false }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error)
    console.error(`  ❌ Error processing ${contentPath}: ${errorMsg}`)
    return { chunks: 0, skipped: false, error: errorMsg }
  }
}

/**
 * Main ingestion function
 */
async function main() {
  const args = process.argv.slice(2)
  const force = args.includes('--force')
  const fileArg = args.indexOf('--file')
  const targetFile = fileArg >= 0 ? args[fileArg + 1] : null

  console.log('\n🚀 DovvyBuddy Content Ingestion\n')
  console.log(`📁 Content directory: ${CONTENT_DIR}`)
  console.log(`⚙️  Mode: ${force ? 'Force re-ingest' : 'Skip existing'}\n`)

  // Create embedding provider
  let embeddingProvider
  try {
    embeddingProvider = createEmbeddingProviderFromEnv()
    console.log(`🤖 Embedding provider: ${embeddingProvider.getProviderName()}`)
    console.log(`📊 Embedding dimension: ${embeddingProvider.getDimension()}\n`)
  } catch (error) {
    console.error('❌ Failed to create embedding provider:')
    console.error(error instanceof Error ? error.message : String(error))
    console.error('\nMake sure EMBEDDING_PROVIDER and GEMINI_API_KEY are set in .env')
    process.exit(1)
  }

  const stats: IngestStats = {
    filesProcessed: 0,
    filesSkipped: 0,
    chunksCreated: 0,
    errors: [],
  }

  try {
    // Find markdown files
    let files: string[]
    if (targetFile) {
      const fullPath = join(CONTENT_DIR, targetFile)
      const exists = await stat(fullPath).catch(() => null)
      if (!exists || !exists.isFile()) {
        console.error(`❌ File not found: ${targetFile}`)
        process.exit(1)
      }
      files = [fullPath]
      console.log(`📝 Ingesting single file: ${targetFile}\n`)
    } else {
      files = await findMarkdownFiles(CONTENT_DIR)
      console.log(`📝 Found ${files.length} markdown files\n`)
    }

    if (files.length === 0) {
      console.log('⚠️  No markdown files found to ingest.')
      process.exit(0)
    }

    // Process each file
    for (const file of files) {
      const result = await ingestFile(file, embeddingProvider, force)

      if (result.skipped) {
        stats.filesSkipped++
      } else {
        stats.filesProcessed++
        stats.chunksCreated += result.chunks

        if (result.error) {
          stats.errors.push(`${relative(CONTENT_DIR, file)}: ${result.error}`)
        }
      }

      // Small delay to avoid rate limiting
      await new Promise((resolve) => setTimeout(resolve, 100))
    }

    // Print summary
    console.log('\n' + '='.repeat(60))
    console.log('📊 Ingestion Summary')
    console.log('='.repeat(60))
    console.log(`Files processed: ${stats.filesProcessed}`)
    console.log(`Files skipped:   ${stats.filesSkipped}`)
    console.log(`Chunks created:  ${stats.chunksCreated}`)
    console.log(`Errors:          ${stats.errors.length}`)

    if (stats.errors.length > 0) {
      console.log('\n❌ Errors encountered:')
      stats.errors.forEach((err) => console.log(`  - ${err}`))
    }

    console.log('\n✨ Ingestion complete!\n')
  } catch (error) {
    console.error('\n❌ Fatal error during ingestion:')
    console.error(error)
    process.exit(1)
  } finally {
    // Free tokenizer resources
    freeTokenizer()
  }
}

// Run main function
main().catch((error) => {
  console.error('Unhandled error:', error)
  process.exit(1)
})
