#!/usr/bin/env tsx
/**
 * Clear Embeddings Script
 *
 * Deletes all content embeddings from the database.
 * Use with caution!
 *
 * Usage:
 *   pnpm content:clear              # Clear all embeddings (with confirmation)
 *   pnpm content:clear --yes        # Skip confirmation
 *   pnpm content:clear --file path  # Clear embeddings for specific file
 */

import { stdin as input, stdout as output } from 'process'
import { createInterface } from 'readline'
import { db } from '../src/db/client'
import { contentEmbeddings } from '../src/db/schema'
import { eq } from 'drizzle-orm'

async function askConfirmation(question: string): Promise<boolean> {
  const rl = createInterface({ input, output })

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close()
      resolve(answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes')
    })
  })
}

async function main() {
  const args = process.argv.slice(2)
  const skipConfirmation = args.includes('--yes')
  const fileArg = args.indexOf('--file')
  const targetFile = fileArg >= 0 ? args[fileArg + 1] : null

  console.log('\n🗑️  DovvyBuddy Clear Embeddings\n')

  if (targetFile) {
    // Clear embeddings for specific file
    console.log(`Target: ${targetFile}\n`)

    if (!skipConfirmation) {
      const confirmed = await askConfirmation(
        `Are you sure you want to delete embeddings for "${targetFile}"? (y/N) `
      )

      if (!confirmed) {
        console.log('Cancelled.')
        process.exit(0)
      }
    }

    const result = await db
      .delete(contentEmbeddings)
      .where(eq(contentEmbeddings.contentPath, targetFile))
      .returning({ id: contentEmbeddings.id })

    console.log(`\n✅ Deleted ${result.length} embeddings for ${targetFile}\n`)
  } else {
    // Clear all embeddings
    console.log('⚠️  This will delete ALL content embeddings from the database.\n')

    if (!skipConfirmation) {
      const confirmed = await askConfirmation('Are you sure you want to continue? (y/N) ')

      if (!confirmed) {
        console.log('Cancelled.')
        process.exit(0)
      }
    }

    // Count before deleting
    const countBefore = await db.select().from(contentEmbeddings)
    const totalCount = countBefore.length

    // Delete all
    await db.delete(contentEmbeddings)

    console.log(`\n✅ Deleted ${totalCount} embeddings\n`)
  }
}

main().catch((error) => {
  console.error('Error:', error)
  process.exit(1)
})
