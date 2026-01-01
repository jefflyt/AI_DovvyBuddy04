import postgres from 'postgres';
import { readdir, readFile } from 'fs/promises';
import { join } from 'path';

const sql = postgres(process.env.DATABASE_URL!, { ssl: 'require' });

interface DiveSiteJSON {
  dive_site_id: string;
  destination_id: string;
  site_name: string;
  min_cert_level_code?: string;
  difficulty_rating_1_5?: number;
  depth_min_m?: number;
  depth_max_m?: number;
  depth_range_m?: [number, number];
  last_updated?: string;
  tags?: string[];
}

/**
 * Extracts description from markdown file's Site Overview section
 */
async function extractDescription(markdownPath: string): Promise<string | null> {
  try {
    const content = await readFile(markdownPath, 'utf-8');
    
    // Find the Site Overview section
    const overviewMatch = content.match(/## 2\. Site Overview\s+([\s\S]*?)(?=\n#{2,3}\s|$)/);
    if (!overviewMatch) return null;
    
    const overviewText = overviewMatch[1].trim();
    
    // Extract first paragraph (before bullet points or tables)
    const firstParagraph = overviewText.split(/\n\n-|\n\n\*\*|^\*\*|^-/)[0].trim();
    
    return firstParagraph || null;
  } catch (error) {
    console.warn(`   ⚠️  Could not read markdown file: ${markdownPath}`);
    return null;
  }
}

async function updateDiveSites() {
  const contentDir = join(process.cwd(), 'content/destinations/Malaysia-Tioman');
  
  try {
    const files = await readdir(contentDir);
    const jsonFiles = files.filter(f => f.endsWith('.json'));
    
    console.log(`\n🚀 Updating dive sites from JSON files...\n`);
    console.log(`📁 Found ${jsonFiles.length} JSON files\n`);
    
    // First, get the destination UUID for Tioman
    const destinations = await sql`
      SELECT id FROM destinations WHERE name ILIKE '%Tioman%' LIMIT 1
    `;
    
    if (destinations.length === 0) {
      console.error('❌ Tioman destination not found in database');
      console.log('\nCreating Tioman destination...');
      
      const newDest = await sql`
        INSERT INTO destinations (name, country, is_active)
        VALUES ('Tioman Island', 'Malaysia', true)
        RETURNING id
      `;
      
      console.log('✅ Created Tioman destination');
    }
    
    const destination = destinations[0] || (await sql`
      SELECT id FROM destinations WHERE name ILIKE '%Tioman%' LIMIT 1
    `)[0];
    
    const destinationId = destination.id;
    console.log(`📍 Using destination ID: ${destinationId}\n`);
    
    for (const file of jsonFiles) {
      const filePath = join(contentDir, file);
      const content = await readFile(filePath, 'utf-8');
      const data: DiveSiteJSON = JSON.parse(content);
      
      console.log(`📄 Processing: ${file}`);
      console.log(`   Site: ${data.site_name}`);
      
      // Try to find corresponding markdown file
      const baseName = file.replace('.json', '');
      const markdownPath = join(contentDir, `${baseName}.md`);
      const description = await extractDescription(markdownPath);
      
      if (description) {
        console.log(`   📝 Found description (${description.length} chars)`);
      }
      
      // Check if site exists
      const existing = await sql`
        SELECT id FROM dive_sites WHERE dive_site_id = ${data.dive_site_id}
      `;
      
      if (existing.length > 0) {
        // Update existing site
        await sql`
          UPDATE dive_sites
          SET 
            name = ${data.site_name},
            destination_id = ${destinationId},
            description = ${description || null},
            min_certification_level = ${data.min_cert_level_code || null},
            difficulty_rating = ${data.difficulty_rating_1_5 || null},
            depth_min_m = ${data.depth_min_m || null},
            depth_max_m = ${data.depth_max_m || null},
            tags = ${data.tags ? JSON.stringify(data.tags) : null}::json,
            last_updated = ${data.last_updated ? new Date(data.last_updated) : null},
            updated_at = NOW()
          WHERE dive_site_id = ${data.dive_site_id}
        `;
        console.log(`   ✅ Updated existing dive site\n`);
      } else {
        // Insert new site
        await sql`
          INSERT INTO dive_sites (
            dive_site_id,
            destination_id,
            name,
            description,
            min_certification_level,
            difficulty_rating,
            depth_min_m,
            depth_max_m,
            tags,
            last_updated,
            is_active
          ) VALUES (
            ${data.dive_site_id},
            ${destinationId},
            ${data.site_name},
            ${description || null},
            ${data.min_cert_level_code || null},
            ${data.difficulty_rating_1_5 || null},
            ${data.depth_min_m || null},
            ${data.depth_max_m || null},
            ${data.tags ? JSON.stringify(data.tags) : null}::json,
            ${data.last_updated ? new Date(data.last_updated) : null},
            true
          )
        `;
        console.log(`   ✅ Inserted new dive site\n`);
      }
    }
    
    // Show summary
    const allSites = await sql`
      SELECT 
        dive_site_id,
        name,
        min_certification_level,
        difficulty_rating,
        depth_min_m,
        depth_max_m,
        CASE 
          WHEN tags IS NOT NULL THEN jsonb_array_length(tags::jsonb)
          ELSE 0
        END as tag_count,
        CASE
          WHEN description IS NOT NULL THEN length(description)
          ELSE 0
        END as description_length
      FROM dive_sites
      ORDER BY name
    `;
    
    console.log('============================================================');
    console.log('📊 Dive Sites Summary');
    console.log('============================================================');
    console.log(`Total dive sites: ${allSites.length}\n`);
    
    allSites.forEach(site => {
      console.log(`📍 ${site.name}`);
      console.log(`   ID: ${site.dive_site_id}`);
      console.log(`   Cert: ${site.min_certification_level || 'N/A'}`);
      console.log(`   Difficulty: ${site.difficulty_rating || 'N/A'}/5`);
      console.log(`   Depth: ${site.depth_min_m || 'N/A'}m - ${site.depth_max_m || 'N/A'}m`);
      console.log(`   Tags: ${site.tag_count || 0}`);
      console.log(`   Description: ${site.description_length || 0} chars\n`);
    });
    
    console.log('✨ Database update complete!');
    
  } catch (error) {
    console.error('❌ Error updating dive sites:', error);
    throw error;
  }
}

updateDiveSites().catch(console.error);
