-- Enable required PostgreSQL extensions
-- Run this before applying migrations

-- Enable vector extension for pgvector support
CREATE EXTENSION IF NOT EXISTS vector;

-- Note: gen_random_uuid() is available in PostgreSQL 13+ by default
-- No need to enable uuid-ossp extension
