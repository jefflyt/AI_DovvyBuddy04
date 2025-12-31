#!/usr/bin/env tsx
/**
 * Content Validation Script
 *
 * Validates markdown content files for:
 * - Frontmatter schema compliance
 * - Required fields present
 * - Valid YAML syntax
 * - Safety disclaimers where required
 * - Word count ranges
 * - Source citations
 *
 * Usage:
 *   pnpm content:validate              # Validate all content
 *   pnpm content:validate --file path  # Validate specific file
 */

import { readFile, readdir } from 'fs/promises'
import { join, relative } from 'path'
import matter from 'gray-matter'
import { z } from 'zod'

const CONTENT_DIR = join(process.cwd(), 'content')

// Validation schemas by doc_type
const baseFrontmatterSchema = z.object({
  doc_type: z.enum(['certification', 'destination', 'dive_site', 'safety', 'faq']),
  title: z.string().min(1),
  tags: z.array(z.string()),
  keywords: z.array(z.string()),
  last_updated: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  data_quality: z.enum(['verified', 'compiled', 'anecdotal']),
  sources: z.array(z.string()).optional(),
})

const certificationFrontmatterSchema = baseFrontmatterSchema.extend({
  doc_type: z.literal('certification'),
  agency: z.string(),
  level: z.string(),
})

const diveSiteFrontmatterSchema = baseFrontmatterSchema.extend({
  doc_type: z.literal('dive_site'),
  site_id: z.string(),
  destination: z.string(),
  min_certification: z.string(),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']),
  depth_range_m: z.array(z.number()).length(2),
})

const destinationFrontmatterSchema = baseFrontmatterSchema.extend({
  doc_type: z.literal('destination'),
  destination: z.string(),
})

interface ValidationIssue {
  severity: 'error' | 'warning'
  message: string
}

interface FileValidationResult {
  file: string
  valid: boolean
  issues: ValidationIssue[]
  wordCount?: number
}

/**
 * Recursively find all markdown files
 */
async function findMarkdownFiles(dir: string): Promise<string[]> {
  const files: string[] = []
  const entries = await readdir(dir, { withFileTypes: true })

  for (const entry of entries) {
    const fullPath = join(dir, entry.name)

    if (entry.isDirectory()) {
      if (entry.name.startsWith('.') || entry.name === 'node_modules') {
        continue
      }
      const subFiles = await findMarkdownFiles(fullPath)
      files.push(...subFiles)
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      if (entry.name === 'README.md') {
        continue
      }
      files.push(fullPath)
    }
  }

  return files
}

/**
 * Count words in text (approximate)
 */
function countWords(text: string): number {
  return text
    .replace(/[#*`_\[\]()]/g, '') // Remove markdown syntax
    .split(/\s+/)
    .filter((word) => word.length > 0).length
}

/**
 * Check if content contains safety disclaimer
 */
function hasSafetyDisclaimer(text: string): boolean {
  const disclaimerKeywords = [
    'safety',
    'caution',
    'warning',
    'disclaimer',
    'risk',
    'medical',
    'physician',
    'doctor',
  ]

  const lowerText = text.toLowerCase()
  return disclaimerKeywords.some((keyword) => lowerText.includes(keyword))
}

/**
 * Validate a single markdown file
 */
async function validateFile(filePath: string): Promise<FileValidationResult> {
  const relativePath = relative(CONTENT_DIR, filePath)
  const issues: ValidationIssue[] = []

  try {
    // Read and parse file
    const fileContent = await readFile(filePath, 'utf-8')
    const { data: frontmatter, content } = matter(fileContent)

    // Validate frontmatter exists
    if (!frontmatter || Object.keys(frontmatter).length === 0) {
      issues.push({
        severity: 'error',
        message: 'No frontmatter found',
      })
      return { file: relativePath, valid: false, issues }
    }

    // Validate doc_type exists
    if (!frontmatter.doc_type) {
      issues.push({
        severity: 'error',
        message: 'Missing required field: doc_type',
      })
      return { file: relativePath, valid: false, issues }
    }

    // Validate based on doc_type
    let schema: z.ZodSchema
    let expectedWordCount: { min: number; max: number } | null = null

    switch (frontmatter.doc_type) {
      case 'certification':
        schema = certificationFrontmatterSchema
        expectedWordCount = { min: 1500, max: 2500 }
        break
      case 'dive_site':
        schema = diveSiteFrontmatterSchema
        expectedWordCount = { min: 500, max: 1000 }
        break
      case 'destination':
        schema = destinationFrontmatterSchema
        expectedWordCount = { min: 800, max: 1500 }
        break
      default:
        schema = baseFrontmatterSchema
    }

    // Validate schema
    const result = schema.safeParse(frontmatter)
    if (!result.success) {
      result.error.issues.forEach((issue) => {
        issues.push({
          severity: 'error',
          message: `Frontmatter validation: ${issue.path.join('.')}: ${issue.message}`,
        })
      })
    }

    // Check for sources
    if (!frontmatter.sources || frontmatter.sources.length === 0) {
      issues.push({
        severity: 'warning',
        message: 'No sources cited in frontmatter',
      })
    }

    // Check content
    const wordCount = countWords(content)

    if (expectedWordCount) {
      if (wordCount < expectedWordCount.min) {
        issues.push({
          severity: 'warning',
          message: `Word count (${wordCount}) below recommended minimum (${expectedWordCount.min})`,
        })
      } else if (wordCount > expectedWordCount.max) {
        issues.push({
          severity: 'warning',
          message: `Word count (${wordCount}) above recommended maximum (${expectedWordCount.max})`,
        })
      }
    }

    // Check for safety disclaimers in relevant content types
    if (['certification', 'dive_site', 'safety'].includes(frontmatter.doc_type)) {
      if (!hasSafetyDisclaimer(content)) {
        issues.push({
          severity: 'warning',
          message: 'No safety disclaimer found (recommended for this content type)',
        })
      }
    }

    // Check if content is empty
    if (!content || content.trim().length === 0) {
      issues.push({
        severity: 'error',
        message: 'Content is empty',
      })
    }

    const valid = issues.filter((i) => i.severity === 'error').length === 0

    return {
      file: relativePath,
      valid,
      issues,
      wordCount,
    }
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error)
    issues.push({
      severity: 'error',
      message: `Failed to parse file: ${errorMsg}`,
    })

    return {
      file: relativePath,
      valid: false,
      issues,
    }
  }
}

/**
 * Main validation function
 */
async function main() {
  const args = process.argv.slice(2)
  const fileArg = args.indexOf('--file')
  const targetFile = fileArg >= 0 ? args[fileArg + 1] : null

  console.log('\n🔍 DovvyBuddy Content Validation\n')
  console.log(`📁 Content directory: ${CONTENT_DIR}\n`)

  // Find files to validate
  let files: string[]
  if (targetFile) {
    const fullPath = join(CONTENT_DIR, targetFile)
    files = [fullPath]
    console.log(`📝 Validating single file: ${targetFile}\n`)
  } else {
    files = await findMarkdownFiles(CONTENT_DIR)
    console.log(`📝 Found ${files.length} markdown files\n`)
  }

  if (files.length === 0) {
    console.log('⚠️  No markdown files found to validate.')
    process.exit(0)
  }

  // Validate each file
  const results: FileValidationResult[] = []

  for (const file of files) {
    const result = await validateFile(file)
    results.push(result)

    // Print result
    if (result.valid) {
      console.log(`✅ ${result.file} ${result.wordCount ? `(${result.wordCount} words)` : ''}`)
      if (result.issues.length > 0) {
        result.issues.forEach((issue) => {
          console.log(`   ⚠️  ${issue.message}`)
        })
      }
    } else {
      console.log(`❌ ${result.file}`)
      result.issues.forEach((issue) => {
        const icon = issue.severity === 'error' ? '❌' : '⚠️'
        console.log(`   ${icon} ${issue.message}`)
      })
    }
  }

  // Print summary
  const validCount = results.filter((r) => r.valid).length
  const invalidCount = results.length - validCount
  const totalErrors = results.reduce(
    (sum, r) => sum + r.issues.filter((i) => i.severity === 'error').length,
    0
  )
  const totalWarnings = results.reduce(
    (sum, r) => sum + r.issues.filter((i) => i.severity === 'warning').length,
    0
  )

  console.log('\n' + '='.repeat(60))
  console.log('📊 Validation Summary')
  console.log('='.repeat(60))
  console.log(`Files validated: ${results.length}`)
  console.log(`Valid:           ${validCount}`)
  console.log(`Invalid:         ${invalidCount}`)
  console.log(`Errors:          ${totalErrors}`)
  console.log(`Warnings:        ${totalWarnings}`)
  console.log()

  if (invalidCount > 0) {
    console.log('❌ Validation failed. Please fix errors before ingesting content.\n')
    process.exit(1)
  } else if (totalWarnings > 0) {
    console.log('⚠️  Validation passed with warnings. Review warnings before ingesting.\n')
    process.exit(0)
  } else {
    console.log('✅ All files valid!\n')
    process.exit(0)
  }
}

main().catch((error) => {
  console.error('Unhandled error:', error)
  process.exit(1)
})
