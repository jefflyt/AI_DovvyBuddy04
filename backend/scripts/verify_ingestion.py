"""Verify content ingestion."""
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
env_path = Path(__file__).resolve().parent.parent.parent / ".env.local"
load_dotenv(env_path)

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

try:
    # Count total
    cur.execute('SELECT COUNT(*) FROM content_embeddings')
    total = cur.fetchone()[0]
    print(f'Total embeddings: {total}')
    
    # Count Malaysia chunks
    cur.execute("SELECT COUNT(*) FROM content_embeddings WHERE metadata->>'content_path' LIKE '%malaysia%'")
    malaysia = cur.fetchone()[0]
    print(f'Malaysia emergency contact chunks: {malaysia}')
    
    # Show first chunk
    cur.execute("SELECT chunk_text, metadata FROM content_embeddings WHERE metadata->>'content_path' LIKE '%malaysia%' LIMIT 1")
    row = cur.fetchone()
    if row:
        print(f'\nFirst chunk preview (300 chars):')
        print(row[0][:300])
        print(f'\nMetadata: {row[1]}')
finally:
    conn.close()
