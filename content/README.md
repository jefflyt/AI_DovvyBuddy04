# DovvyBuddy Content Repository

This directory contains the curated markdown documentation that powers DovvyBuddy's knowledge base.

## Structure

```
content/
├── certifications/    # Certification guides (PADI, SSI, NAUI, etc.)
├── destinations/      # Dive destination overviews
├── faq/              # Frequently asked questions
└── safety/           # Safety reference documents
```

## Content Authoring Guidelines

### Frontmatter Schema

All markdown files must include YAML frontmatter. Required fields vary by content type.

#### General Fields (All Content Types)

```yaml
---
doc_type: "certification" | "destination" | "dive_site" | "safety" | "faq"
title: "Document Title"
tags: ["tag1", "tag2"]
keywords: ["keyword1", "keyword2"]
last_updated: "YYYY-MM-DD"
data_quality: "verified" | "compiled" | "anecdotal"
sources: ["URL1", "URL2"]
---
```

#### Certification-Specific

```yaml
agency: "PADI" | "SSI" | "NAUI" | "SDI" | etc.
level: "OW" | "AOW" | "Rescue" | "DM"
```

#### Dive Site-Specific

```yaml
site_id: "unique-site-identifier"
destination: "Destination Name, Country"
min_certification: "OW" | "AOW" | etc.
difficulty: "beginner" | "intermediate" | "advanced"
depth_range_m: [min, max]
```

### Content Quality Standards

1. **Accuracy**: All information must be factual and grounded in reputable sources.
2. **Sources**: Cite official agency documentation, diving publications (e.g., DIVER Magazine, Sport Diver), DAN resources, or reputable dive operators.
3. **Tone**: Descriptive and informative, not instructional or directive.
4. **Safety**: Always include relevant safety disclaimers for dive sites and certification content.
5. **Completeness**: Follow word count guidelines:
   - Certification guides: 1500-2000 words
   - Destination overviews: 800-1200 words
   - Dive site profiles: 500-800 words
   - Safety documents: Variable (as needed)

### Dive Site Template

Use the following as a descriptive guide (flexible interpretation allowed):

```markdown
---
doc_type: 'dive_site'
site_id: 'unique-identifier'
title: 'Site Name'
destination: 'Destination, Country'
min_certification: 'OW'
difficulty: 'beginner'
depth_range_m: [10, 30]
tags: ['reef', 'wreck', 'drift', etc.]
keywords: ['coral', 'marine life', etc.]
last_updated: 'YYYY-MM-DD'
data_quality: 'compiled'
sources: ['URL1', 'URL2']
---

# Site Name

## Overview

Brief introduction to the site (1-2 paragraphs).

## Marine Life

Notable species and ecosystems.

## Dive Profile

Typical depth, current conditions, visibility.

## Best For

Who this site is suitable for (beginners, photographers, etc.).

## Safety Notes

Important safety considerations and disclaimers.

## Access

How to reach the site (boat, shore, etc.).
```

### Adding New Content

1. Create markdown file in appropriate subdirectory.
2. Include complete frontmatter with all required fields.
3. Write descriptive, accurate content following quality standards.
4. Cite sources in frontmatter.
5. Run validation: `pnpm content:validate`
6. Ingest content: `pnpm content:ingest`

### Updating Existing Content

1. Edit markdown file.
2. Update `last_updated` field in frontmatter.
3. Run validation: `pnpm content:validate`
4. Re-ingest: `pnpm content:ingest --force` (or delete old embeddings first)

## Content Validation

Run `pnpm content:validate` before ingesting to check:

- Frontmatter schema compliance
- Required fields present
- Valid YAML syntax
- Safety disclaimers where required
- Word count ranges
- Source citations

## Ingestion Process

The ingestion pipeline:

1. **Read**: Recursively scan markdown files in `content/`.
2. **Parse**: Extract frontmatter and body text.
3. **Chunk**: Split text using hybrid strategy (semantic + paragraph split).
4. **Embed**: Generate 768-dimensional vectors via Gemini API (`text-embedding-004`).
5. **Store**: Save chunks and embeddings to `content_embeddings` table.

Run ingestion:

```bash
pnpm content:ingest
```

Clear embeddings (for complete re-ingest):

```bash
pnpm content:clear
```

## Content Review Checklist

Before committing new content:

- [ ] Frontmatter includes all required fields for doc type
- [ ] Sources cited (official sites, reputable publications)
- [ ] Safety disclaimers present where applicable
- [ ] Tone is descriptive, not instructional
- [ ] Word count within expected range
- [ ] YAML syntax is valid
- [ ] Validation script passes
- [ ] Content reviewed for accuracy

## Maintenance

- Review and update content quarterly
- Check for outdated information (especially certification requirements)
- Monitor user questions for gaps in content coverage
- Version all content in git for auditability
