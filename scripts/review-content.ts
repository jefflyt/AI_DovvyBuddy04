#!/usr/bin/env tsx

/**
 * Content Review Script
 * 
 * Validates RAG content for:
 * - Required frontmatter fields
 * - Content length
 * - Last updated date freshness
 * - Proper markdown formatting
 * - Safety disclaimers (where required)
 */

import * as fs from 'fs'
import * as path from 'path'

interface ContentIssue {
  file: string
  severity: 'error' | 'warning'
  message: string
}

interface ContentStats {
  totalFiles: number
  passedFiles: number
  errors: number
  warnings: number
  issues: ContentIssue[]
}

const CONTENT_DIR = path.join(process.cwd(), 'content')
const REQUIRED_FRONTMATTER_FIELDS = ['last_updated']
const TYPE_FIELD_ALIASES = ['type', 'doc_type'] // Accept either 'type' or 'doc_type'
const SAFETY_DISCLAIMER_KEYWORDS = ['certified', 'professional', 'instructor', 'medical']
const MAX_CONTENT_AGE_DAYS = 180 // 6 months
const SKIP_FILES = ['TEMPLATE', 'WORKSHEET', 'README'] // Skip template and README files

function parseMarkdownFrontmatter(content: string): Record<string, any> | null {
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/)
  if (!frontmatterMatch) return null

  const frontmatter: Record<string, any> = {}
  const lines = frontmatterMatch[1].split('\n')

  for (const line of lines) {
    const match = line.match(/^(\w+):\s*(.+)$/)
    if (match) {
      const [, key, value] = match
      frontmatter[key] = value.trim()
    }
  }

  return frontmatter
}

function extractMarkdownContent(content: string): string {
  // Remove frontmatter
  const withoutFrontmatter = content.replace(/^---\n[\s\S]*?\n---\n/, '')
  return withoutFrontmatter.trim()
}

function checkFile(filePath: string, relativePath: string): ContentIssue[] {
  const issues: ContentIssue[] = []
  
  // Skip template, worksheet, and README files
  const fileName = path.basename(filePath)
  if (SKIP_FILES.some(skip => fileName.toUpperCase().includes(skip))) {
    return issues // Skip validation for these files
  }
  
  const content = fs.readFileSync(filePath, 'utf-8')

  // Check 1: Frontmatter exists
  const frontmatter = parseMarkdownFrontmatter(content)
  if (!frontmatter) {
    issues.push({
      file: relativePath,
      severity: 'error',
      message: 'Missing frontmatter (must start with ---)',
    })
    return issues // Can't continue validation without frontmatter
  }

  // Check 2: Required fields present
  for (const field of REQUIRED_FRONTMATTER_FIELDS) {
    if (!frontmatter[field]) {
      issues.push({
        file: relativePath,
        severity: 'error',
        message: `Missing required frontmatter field: ${field}`,
      })
    }
  }
  
  // Check 2a: Type field (accept either 'type' or 'doc_type')
  const hasTypeField = TYPE_FIELD_ALIASES.some(alias => frontmatter[alias])
  if (!hasTypeField) {
    issues.push({
      file: relativePath,
      severity: 'warning',
      message: `Missing type field (expected 'type' or 'doc_type')`,
    })
  }

  // Check 3: Last updated date format and freshness
  if (frontmatter.last_updated) {
    const lastUpdated = new Date(frontmatter.last_updated)
    if (isNaN(lastUpdated.getTime())) {
      issues.push({
        file: relativePath,
        severity: 'error',
        message: `Invalid last_updated date format: ${frontmatter.last_updated}`,
      })
    } else {
      const daysSinceUpdate =
        (Date.now() - lastUpdated.getTime()) / (1000 * 60 * 60 * 24)
      if (daysSinceUpdate > MAX_CONTENT_AGE_DAYS) {
        issues.push({
          file: relativePath,
          severity: 'warning',
          message: `Content may be stale (last updated ${Math.round(daysSinceUpdate)} days ago)`,
        })
      }
    }
  }

  // Check 4: Content length
  const markdownContent = extractMarkdownContent(content)
  if (markdownContent.length < 100) {
    issues.push({
      file: relativePath,
      severity: 'warning',
      message: `Content is very short (${markdownContent.length} chars)`,
    })
  }

  // Check 5: Safety disclaimers (for certification and safety content)
  const contentType = frontmatter.type || frontmatter.doc_type || ''
  if (
    contentType === 'certification' ||
    contentType === 'safety' ||
    relativePath.includes('/certifications/') ||
    relativePath.includes('/safety/')
  ) {
    const hasDisclaimer = SAFETY_DISCLAIMER_KEYWORDS.some((keyword) =>
      markdownContent.toLowerCase().includes(keyword)
    )
    if (!hasDisclaimer) {
      issues.push({
        file: relativePath,
        severity: 'warning',
        message: `Safety/certification content should mention professional consultation (keywords: ${SAFETY_DISCLAIMER_KEYWORDS.join(', ')})`,
      })
    }
  }

  // Check 6: Proper markdown formatting (headers, lists, etc.)
  const hasHeaders = /^#{1,6}\s+.+$/m.test(markdownContent)
  if (!hasHeaders && markdownContent.length > 200) {
    issues.push({
      file: relativePath,
      severity: 'warning',
      message: 'Content lacks section headers (consider adding ## headings)',
    })
  }

  return issues
}

function walkDirectory(dir: string, baseDir: string = dir): string[] {
  const files: string[] = []
  const entries = fs.readdirSync(dir, { withFileTypes: true })

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name)

    if (entry.isDirectory()) {
      files.push(...walkDirectory(fullPath, baseDir))
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      files.push(fullPath)
    }
  }

  return files
}

function reviewContent(): ContentStats {
  const stats: ContentStats = {
    totalFiles: 0,
    passedFiles: 0,
    errors: 0,
    warnings: 0,
    issues: [],
  }

  if (!fs.existsSync(CONTENT_DIR)) {
    console.error(`❌ Content directory not found: ${CONTENT_DIR}`)
    process.exit(1)
  }

  const files = walkDirectory(CONTENT_DIR)
  stats.totalFiles = files.length

  console.log(`📂 Reviewing ${stats.totalFiles} content files...\n`)

  for (const file of files) {
    const relativePath = path.relative(CONTENT_DIR, file)
    const issues = checkFile(file, relativePath)

    if (issues.length === 0) {
      stats.passedFiles++
      console.log(`✅ ${relativePath}`)
    } else {
      const errorCount = issues.filter((i) => i.severity === 'error').length
      const warningCount = issues.filter((i) => i.severity === 'warning').length

      stats.errors += errorCount
      stats.warnings += warningCount
      stats.issues.push(...issues)

      const icon = errorCount > 0 ? '❌' : '⚠️'
      console.log(`${icon} ${relativePath}`)
      for (const issue of issues) {
        const prefix = issue.severity === 'error' ? '   ERROR:' : '   WARN: '
        console.log(`${prefix} ${issue.message}`)
      }
    }
  }

  return stats
}

function printSummary(stats: ContentStats): void {
  console.log('\n' + '='.repeat(60))
  console.log('📊 Content Review Summary')
  console.log('='.repeat(60))
  console.log(`Total files:    ${stats.totalFiles}`)
  console.log(`Passed:         ${stats.passedFiles} ✅`)
  console.log(`Errors:         ${stats.errors} ❌`)
  console.log(`Warnings:       ${stats.warnings} ⚠️`)
  console.log('='.repeat(60))

  if (stats.errors > 0) {
    console.log('\n❌ Content review FAILED (errors found)')
    console.log('Please fix errors before proceeding.')
  } else if (stats.warnings > 0) {
    console.log('\n⚠️  Content review PASSED with warnings')
    console.log('Consider addressing warnings for better content quality.')
  } else {
    console.log('\n✅ Content review PASSED (all checks passed)')
  }
}

// Main execution
const stats = reviewContent()
printSummary(stats)

// Exit with error code if errors found (for CI)
if (stats.errors > 0) {
  process.exit(1)
}
