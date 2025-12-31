/**
 * Clear Database Script
 * 
 * Removes all data from destinations and dive_sites tables.
 * Run before reseeding with new data.
 */

import { config } from 'dotenv'
import { resolve } from 'path'
config({ path: resolve(process.cwd(), '.env.local') })

import { db } from './client'
import { destinations, diveSites } from './schema'

async function clear() {
  console.log('🗑️  Clearing database...\n')

  try {
    // Delete dive sites first (foreign key constraint)
    const deletedSites = await db.delete(diveSites).returning()
    console.log(`✓ Deleted ${deletedSites.length} dive sites`)

    // Delete destinations
    const deletedDestinations = await db.delete(destinations).returning()
    console.log(`✓ Deleted ${deletedDestinations.length} destinations`)

    console.log('\n✅ Database cleared successfully!')
  } catch (error) {
    console.error('❌ Clear failed:', error)
    throw error
  }
}

clear()
  .catch((error) => {
    console.error('Fatal error during clear:', error)
    process.exit(1)
  })
  .finally(() => {
    process.exit(0)
  })
