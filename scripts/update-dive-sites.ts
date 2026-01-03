import postgres from 'postgres';
import { readdir, readFile } from 'fs/promises';
import { join, basename } from 'path';

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
 * Simple slugify helper for filename matching
 */
function slugify(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-');
}

/**
 * Extracts description from markdown file's Site Overview section
 */
async function extractDescription(markdownPath: string): Promise<string | null> {
  try {
    const content = await readFile(markdownPath, 'utf-8');
    
    // Match "## 2. Site Overview" or "## Site Overview"
    const overviewMatch = content.match(/##\s*(?:\d+\.\s*)?Site Overview\s*([\s\S]*?)(?=\n##\s|\n#\s|$)/i);
    if (!overviewMatch) return null;
    
    const overviewText = overviewMatch[1].trim();
    
    // Extract first paragraph or truncate to reasonable length
    const paragraphs = overviewText.split(/\n\s*\n/);
    const firstParagraph = paragraphs.find(p => p.trim().length > 0) || overviewText;
    
    return firstParagraph.trim().slice(0, 2000);
  } catch (error) {
    console.warn(`   ⚠️  Could not read markdown file: ${markdownPath}`);
    return null;
  }
}

/**
 * Find markdown file for a dive site by matching dive_site_id or site_name
 */
async function findMarkdownFile(contentDir: string, site: DiveSiteJSON): Promise<string | null> {
  try {
    const files = await readdir(contentDir);
    const mdFiles = files.filter(f => f.endsWith('.md') && !f.includes('overview'));
    
    // Try exact match by dive_site_id
    const exactMatch = mdFiles.find(f => basename(f, '.md') === site.dive_site_id);
    if (exactMatch) return join(contentDir, exactMatch);
    
    // Try match by slugified site_name
    if (site.site_name) {
      const slug = slugify(site.site_name);
      const slugMatch = mdFiles.find(f => basename(f, '.md').includes(slug));
      if (slugMatch) return join(contentDir, slugMatch);
    }
    
    // Fallback: match by site_name keywords
    if (site.site_name) {
      const words = site.site_name.toLowerCase().split(/\s+/).slice(0, 3);
      for (const f of mdFiles) {
        const name = basename(f, '.md').toLowerCase();
        if (words.every(w => name.includes(w))) {
          return join(contentDir, f);
        }
      }
    }
    
    return null;
  } catch (error) {
    console.warn(`   ⚠️  Error finding markdown file:`, error);
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
      
      // Find corresponding markdown file and extract description
      const mdPath = await findMarkdownFile(contentDir, data);
      let description: string | null = null;
      
      if (mdPath) {
        description = await extractDescription(mdPath);
        if (description) {
          console.log(`   📝 Found description (${description.length} chars)`);
        }
      } else {
        console.warn(`   ⚠️  No markdown found for ${data.dive_site_id} / ${data.site_name}`);
      }
      
      // Prepare data
      const depthMin = data.depth_min_m ?? (data.depth_range_m ? data.depth_range_m[0] : null);
      const depthMax = data.depth_max_m ?? (data.depth_range_m ? data.depth_range_m[1] : null);
      const tagsJson = data.tags ? JSON.stringify(data.tags) : null;
      
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
            description = COALESCE(${description}, description),
            min_certification_level = ${data.min_cert_level_code || null},
            difficulty_rating = ${data.difficulty_rating_1_5 || null},
            depth_min_m = ${depthMin},
            depth_max_m = ${depthMax},
            tags = ${tagsJson}::json,
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
            ${depthMin},
            ${depthMax},
            ${tagsJson}::json,
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
      console.log(`   Description: ${site.description_length || 0} chars\n`);
    });
    
    console.log('✨ Database update complete!');
    
  } catch (error) {
    console.error('❌ Error updating dive sites:', error);
    throw error;
  } finally {
    await sql.end({ timeout: 5 });
  }
}

if (require.main === module) {
  updateDiveSites().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
