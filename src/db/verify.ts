/**
 * Database Verification Script
 * 
 * Tests basic database operations to verify PR1 implementation.
 */

import { config } from 'dotenv'
import { resolve } from 'path'
config({ path: resolve(process.cwd(), '.env.local') })

import { db } from './client'
import { destinations, diveSites } from './schema'
import { eq, count } from 'drizzle-orm'

async function verify() {
  console.log('🔍 Verifying database setup...\n')

  try {
    // Test 1: Count destinations
    const destinationCount = await db
      .select({ count: count() })
      .from(destinations)
    console.log(`✓ Destinations table: ${destinationCount[0].count} records`)

    // Test 2: Count dive sites
    const diveSiteCount = await db
      .select({ count: count() })
      .from(diveSites)
    console.log(`✓ Dive sites table: ${diveSiteCount[0].count} records`)

    // Test 3: Query Tioman destination
    const tioman = await db
      .select()
      .from(destinations)
      .where(eq(destinations.name, 'Tioman Island'))
      .limit(1)

    if (tioman.length > 0) {
      console.log(`✓ Found destination: ${tioman[0].name}, ${tioman[0].country}`)
      
      // Test 4: Query dive sites for Tioman
      const tiomanSites = await db
        .select()
        .from(diveSites)
        .where(eq(diveSites.destinationId, tioman[0].id))

      console.log(`✓ Found ${tiomanSites.length} dive sites for Tioman:`)
      tiomanSites.forEach((site) => {
        console.log(`  - ${site.name} (${site.difficultyBand})`)
      })
    } else {
      console.log('✗ Tioman Island destination not found')
    }

    console.log('\n✅ Database verification completed successfully!')
  } catch (error) {
    console.error('❌ Verification failed:', error)
    throw error
  }
}

verify()
  .catch((error) => {
    console.error('Fatal error during verification:', error)
    process.exit(1)
  })
  .finally(() => {
    process.exit(0)
  })
