# content/

Curated markdown content for RAG (Retrieval-Augmented Generation) in DovvyBuddy.

## Purpose

This folder contains **version-controlled markdown files** that serve as the knowledge base for the AI assistant. All content is:

- Written or curated by the DovvyBuddy team
- Reviewed for accuracy and diver safety
- Grounded in authoritative sources (PADI, SSI, dive operators, safety organizations)

## Structure (to be added in PR2)

```
content/
├── certifications/
│   ├── padi/
│   │   ├── open-water.md
│   │   ├── advanced-open-water.md
│   │   └── specialties.md
│   ├── ssi/
│   │   ├── open-water-diver.md
│   │   ├── advanced-adventurer.md
│   │   └── specialties.md
│   └── comparison.md
├── destinations/
│   └── [destination-name]/
│       ├── overview.md
│       ├── logistics.md
│       ├── safety.md
│       └── sites/
│           └── [site-name].md
├── safety/
│   ├── general-safety.md
│   ├── prerequisites.md
│   └── no-fly-times.md
└── faq/
    ├── new-divers.md
    └── advanced-planning.md
```

## RAG Pipeline (implemented in PR2)

1. **Ingestion:** Parse markdown files
2. **Chunking:** Split into semantic chunks (500-1000 tokens)
3. **Embedding:** Generate embeddings using Gemini API
4. **Indexing:** Store vectors in Postgres (pgvector) or object storage
5. **Retrieval:** Search for relevant chunks based on user query
6. **Grounding:** Pass retrieved chunks as context to LLM

## Content Guidelines

- Use clear, diver-friendly language
- Include sources and last-updated dates in frontmatter
- Mark prerequisites and suitability clearly
- Add safety disclaimers where appropriate
- Keep content modular (one concept per file when possible)
