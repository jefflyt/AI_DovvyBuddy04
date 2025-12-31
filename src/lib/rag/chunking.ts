/**
 * Text Chunking for RAG
 *
 * Implements hybrid chunking strategy:
 * 1. Try semantic split (preserve markdown sections)
 * 2. Fall back to paragraph split for large sections
 * 3. Include section headers for context
 */

import { encoding_for_model, type Tiktoken } from 'tiktoken'
import type { ContentChunk, ChunkingOptions } from './types'

const DEFAULT_TARGET_TOKENS = 650
const DEFAULT_MAX_TOKENS = 800
const DEFAULT_MIN_TOKENS = 100
const DEFAULT_OVERLAP_TOKENS = 50

// Use GPT-3.5 tokenizer as approximation for Gemini
// (Gemini's tokenizer isn't available in tiktoken, but token counts are close enough)
let tokenizer: Tiktoken | null = null

function getTokenizer(): Tiktoken {
  if (!tokenizer) {
    tokenizer = encoding_for_model('gpt-3.5-turbo')
  }
  return tokenizer
}

/**
 * Count tokens in text using tiktoken
 */
export function countTokens(text: string): number {
  const encoder = getTokenizer()
  return encoder.encode(text).length
}

/**
 * Split text into sections based on markdown headers
 */
function splitIntoSections(text: string): Array<{ header: string; content: string }> {
  const sections: Array<{ header: string; content: string }> = []

  // Split on markdown headers (## or ###)
  const lines = text.split('\n')
  let currentHeader = ''
  let currentContent: string[] = []

  for (const line of lines) {
    // Check if line is a header (## or ###)
    const headerMatch = line.match(/^(#{2,3})\s+(.+)$/)

    if (headerMatch) {
      // Save previous section if it has content
      if (currentContent.length > 0) {
        sections.push({
          header: currentHeader,
          content: currentContent.join('\n').trim(),
        })
      }

      // Start new section
      currentHeader = line
      currentContent = []
    } else {
      currentContent.push(line)
    }
  }

  // Save last section
  if (currentContent.length > 0) {
    sections.push({
      header: currentHeader,
      content: currentContent.join('\n').trim(),
    })
  }

  return sections
}

/**
 * Split text into paragraphs (by double newline)
 */
function splitIntoParagraphs(text: string): string[] {
  return text
    .split(/\n\n+/)
    .map((p) => p.trim())
    .filter((p) => p.length > 0)
}

/**
 * Combine paragraphs into chunks that fit within token limits
 */
function combineParagraphsIntoChunks(
  paragraphs: string[],
  header: string,
  options: Required<ChunkingOptions>
): string[] {
  const chunks: string[] = []
  let currentChunk: string[] = []
  let currentTokens = 0

  // Add header token count if present
  const headerTokens = header ? countTokens(header + '\n\n') : 0

  for (const paragraph of paragraphs) {
    const paragraphTokens = countTokens(paragraph)

    // If single paragraph exceeds max tokens, include it as its own chunk
    if (paragraphTokens > options.maxTokens) {
      // Save current chunk if it has content
      if (currentChunk.length > 0) {
        const chunkText = header ? `${header}\n\n${currentChunk.join('\n\n')}` : currentChunk.join('\n\n')
        chunks.push(chunkText)
        currentChunk = []
        currentTokens = 0
      }

      // Add oversized paragraph as its own chunk
      const chunkText = header ? `${header}\n\n${paragraph}` : paragraph
      chunks.push(chunkText)
      continue
    }

    // Check if adding this paragraph would exceed target
    const potentialTokens = currentTokens + paragraphTokens + (currentChunk.length > 0 ? 2 : 0) // +2 for \n\n

    if (potentialTokens > options.targetTokens && currentChunk.length > 0) {
      // Save current chunk
      const chunkText = header ? `${header}\n\n${currentChunk.join('\n\n')}` : currentChunk.join('\n\n')
      chunks.push(chunkText)

      // Start new chunk with this paragraph
      currentChunk = [paragraph]
      currentTokens = headerTokens + paragraphTokens
    } else {
      // Add paragraph to current chunk
      currentChunk.push(paragraph)
      currentTokens += paragraphTokens + (currentChunk.length > 1 ? 2 : 0)
    }
  }

  // Save last chunk
  if (currentChunk.length > 0) {
    const chunkText = header ? `${header}\n\n${currentChunk.join('\n\n')}` : currentChunk.join('\n\n')
    chunks.push(chunkText)
  }

  return chunks
}

/**
 * Chunk text using hybrid strategy
 *
 * 1. Split into sections by markdown headers
 * 2. For each section, check if it fits within maxTokens
 * 3. If yes, keep section intact
 * 4. If no, split section into paragraphs and combine into chunks
 */
export function chunkText(
  text: string,
  contentPath: string,
  frontmatter: Record<string, any> = {},
  options: ChunkingOptions = {}
): ContentChunk[] {
  const opts: Required<ChunkingOptions> = {
    targetTokens: options.targetTokens ?? DEFAULT_TARGET_TOKENS,
    maxTokens: options.maxTokens ?? DEFAULT_MAX_TOKENS,
    minTokens: options.minTokens ?? DEFAULT_MIN_TOKENS,
    overlapTokens: options.overlapTokens ?? DEFAULT_OVERLAP_TOKENS,
  }

  const chunks: ContentChunk[] = []
  let chunkIndex = 0

  // Split into sections
  const sections = splitIntoSections(text)

  for (const section of sections) {
    const sectionText = section.header ? `${section.header}\n\n${section.content}` : section.content

    // Skip empty sections
    if (!sectionText.trim()) {
      continue
    }

    const sectionTokens = countTokens(sectionText)

    // If section fits within max tokens, keep it intact
    if (sectionTokens <= opts.maxTokens) {
      chunks.push({
        text: sectionText,
        metadata: {
          contentPath,
          chunkIndex: chunkIndex++,
          sectionHeader: section.header || undefined,
          ...frontmatter,
        },
      })
    } else {
      // Split section into paragraphs and combine into chunks
      const paragraphs = splitIntoParagraphs(section.content)
      const sectionChunks = combineParagraphsIntoChunks(paragraphs, section.header, opts)

      for (const chunkText of sectionChunks) {
        // Skip chunks that are too small (unless it's the only chunk in section)
        const chunkTokens = countTokens(chunkText)
        if (chunkTokens < opts.minTokens && sectionChunks.length > 1) {
          continue
        }

        chunks.push({
          text: chunkText,
          metadata: {
            contentPath,
            chunkIndex: chunkIndex++,
            sectionHeader: section.header || undefined,
            ...frontmatter,
          },
        })
      }
    }
  }

  return chunks
}

/**
 * Free tokenizer resources (call when done chunking)
 */
export function freeTokenizer(): void {
  if (tokenizer) {
    tokenizer.free()
    tokenizer = null
  }
}
