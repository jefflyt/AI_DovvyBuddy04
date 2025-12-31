/**
 * Database Seed Script
 * 
 * Seeds the database with initial data:
 * - 1 destination (Tioman Island, Malaysia)
 * - 5 dive sites in Tioman
 * 
 * Run with: pnpm db:seed
 * 
 * This script is idempotent - safe to run multiple times.
 */

import { db } from './client'
import { destinations, diveSites } from './schema'
import { eq } from 'drizzle-orm'

async function seed() {
  console.log('🌱 Starting database seed...\n')

  try {
    // Check if Tioman already exists
    const existingDestination = await db
      .select()
      .from(destinations)
      .where(eq(destinations.name, 'Tioman Island'))
      .limit(1)

    let destinationId: string

    if (existingDestination.length > 0) {
      console.log('✓ Destination "Tioman Island" already exists, skipping...')
      destinationId = existingDestination[0].id
    } else {
      // Insert Tioman destination
      const [destination] = await db
        .insert(destinations)
        .values({
          name: 'Tioman Island',
          country: 'Malaysia',
          isActive: true,
        })
        .returning()

      destinationId = destination.id
      console.log('✓ Created destination: Tioman Island, Malaysia')
    }

    // Define dive sites for Tioman (based on content files)
    const tiomanDiveSites = [
      {
        name: 'Tiger Reef',
        description: 'A submerged pinnacle between Labas and Sepoi Islands, resembling a crouching tiger from above. Known for dramatic boulder formations, prolific soft coral coverage, and large schools of jacks and barracudas. Strong currents attract pelagic life.',
        minCertificationLevel: 'AOW',
        minLoggedDives: 20,
        difficultyBand: 'intermediate',
        accessType: 'boat',
        dataQuality: 'verified',
      },
      {
        name: 'Batu Malang',
        description: 'Meaning "Unlucky Rock," this site features dramatic granite boulder topography with extensive swim-throughs and caverns. Shallow dive perfect for beginners, with rich macro life and hard coral gardens.',
        minCertificationLevel: 'OW',
        minLoggedDives: 0,
        difficultyBand: 'beginner',
        accessType: 'boat',
        dataQuality: 'verified',
      },
      {
        name: 'Pulau Chebeh',
        description: 'A small island off Tioman\'s northwest coast offering pristine coral reefs and diverse marine life. Suitable for all certification levels with varying depth zones.',
        minCertificationLevel: 'AOW',
        minLoggedDives: 10,
        difficultyBand: 'intermediate',
        accessType: 'boat',
        dataQuality: 'compiled',
      },
      {
        name: 'Pulau Labas',
        description: 'Remote island location with excellent visibility and healthy coral formations. Known for encounters with turtles and schooling fish.',
        minCertificationLevel: 'OW',
        minLoggedDives: 10,
        difficultyBand: 'intermediate',
        accessType: 'boat',
        dataQuality: 'compiled',
      },
      {
        name: 'Renggis Island',
        description: 'Popular shallow dive site near the main Tioman coastline. Features coral gardens, sandy patches, and abundant tropical fish. Excellent for training and checkout dives.',
        minCertificationLevel: 'OW',
        minLoggedDives: 0,
        difficultyBand: 'beginner',
        accessType: 'boat',
        dataQuality: 'verified',
      },
    ]

    // Check which dive sites already exist
    const existingSites = await db
      .select()
      .from(diveSites)
      .where(eq(diveSites.destinationId, destinationId))

    const existingSiteNames = new Set(existingSites.map((site) => site.name))

    // Filter out sites that already exist
    const sitesToInsert = tiomanDiveSites.filter(
      (site) => !existingSiteNames.has(site.name)
    )

    if (sitesToInsert.length > 0) {
      // Insert dive sites
      const insertedSites = await db
        .insert(diveSites)
        .values(
          sitesToInsert.map((site) => ({
            destinationId,
            name: site.name,
            description: site.description,
            minCertificationLevel: site.minCertificationLevel,
            minLoggedDives: site.minLoggedDives,
            difficultyBand: site.difficultyBand,
            accessType: site.accessType,
            dataQuality: site.dataQuality,
            isActive: true,
          }))
        )
        .returning()

      console.log(`✓ Created ${insertedSites.length} dive sites`)
      insertedSites.forEach((site) => {
        console.log(`  - ${site.name}`)
      })
    } else {
      console.log('✓ All dive sites already exist, skipping...')
    }

    console.log('\n✅ Database seed completed successfully!')
  } catch (error) {
    console.error('❌ Seed failed:', error)
    throw error
  }
}

// Run seed function
seed()
  .catch((error) => {
    console.error('Fatal error during seed:', error)
    process.exit(1)
  })
  .finally(() => {
    process.exit(0)
  })
