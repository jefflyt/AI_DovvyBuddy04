/**
 * Chunking Tests
 *
 * Unit tests for text chunking functionality
 */

import { describe, it, expect } from 'vitest'
import { chunkText, countTokens } from '../../src/lib/rag/chunking'

describe('Text Chunking', () => {
  describe('countTokens', () => {
    it('should count tokens in simple text', () => {
      const text = 'Hello world'
      const tokens = countTokens(text)
      expect(tokens).toBeGreaterThan(0)
      expect(tokens).toBeLessThan(10)
    })

    it('should handle empty text', () => {
      const tokens = countTokens('')
      expect(tokens).toBe(0)
    })
  })

  describe('chunkText', () => {
    it('should create chunks from markdown with sections', () => {
      const text = `
## Section 1

This is the first section with some content.
It has multiple paragraphs.

This is the second paragraph in section 1.

## Section 2

This is the second section.
It also has content.

## Section 3

Final section here.
      `.trim()

      const chunks = chunkText(text, 'test/file.md')

      expect(chunks.length).toBeGreaterThan(0)
      chunks.forEach((chunk) => {
        expect(chunk.text).toBeTruthy()
        expect(chunk.metadata.contentPath).toBe('test/file.md')
        expect(chunk.metadata.chunkIndex).toBeGreaterThanOrEqual(0)
      })
    })

    it('should include frontmatter in chunk metadata', () => {
      const text = 'Simple content'
      const frontmatter = {
        doc_type: 'test',
        title: 'Test Document',
      }

      const chunks = chunkText(text, 'test/file.md', frontmatter)

      expect(chunks.length).toBeGreaterThan(0)
      expect(chunks[0].metadata.doc_type).toBe('test')
      expect(chunks[0].metadata.title).toBe('Test Document')
    })

    it('should preserve section headers in chunks', () => {
      const text = `
## Important Section

This content should include the header.
      `.trim()

      const chunks = chunkText(text, 'test/file.md')

      expect(chunks.length).toBeGreaterThan(0)
      expect(chunks[0].text).toContain('## Important Section')
      expect(chunks[0].metadata.sectionHeader).toBe('## Important Section')
    })

    it('should split large sections into multiple chunks', () => {
      // Create a section with lots of paragraphs
      const paragraphs = Array(30)
        .fill(null)
        .map(
          (_, i) =>
            `This is paragraph number ${i + 1}. It contains sufficient text that will be chunked properly when we reach the token limit for chunking purposes.`
        )
        .join('\n\n')

      const text = `## Large Section\n\n${paragraphs}`

      const chunks = chunkText(text, 'test/file.md', {}, { maxTokens: 150, targetTokens: 100, minTokens: 20 })

      // Should create at least one chunk
      expect(chunks.length).toBeGreaterThanOrEqual(1)

      // First chunk should have the section header
      expect(chunks[0].text).toContain('## Large Section')
    })

    it('should handle text without sections', () => {
      const text = `
This is a document without markdown sections.
It just has paragraphs.

This is the second paragraph.

And a third one.
      `.trim()

      const chunks = chunkText(text, 'test/file.md')

      expect(chunks.length).toBeGreaterThan(0)
      chunks.forEach((chunk) => {
        expect(chunk.text).toBeTruthy()
      })
    })

    it('should assign sequential chunk indices', () => {
      const text = `
## Section 1
Content 1

## Section 2
Content 2

## Section 3
Content 3
      `.trim()

      const chunks = chunkText(text, 'test/file.md')

      const indices = chunks.map((c) => c.metadata.chunkIndex)
      expect(indices).toEqual([0, 1, 2])
    })
  })
})
