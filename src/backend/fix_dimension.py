"""Fix embedding column dimension from 768 to 3072."""
from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Find and drop existing embedding indexes (not pkey)
    result = db.execute(text("SELECT indexname FROM pg_indexes WHERE tablename = 'content_embeddings' AND indexname LIKE '%embedding%' AND indexname NOT LIKE '%pkey%'"))
    indexes = [row[0] for row in result]
    for idx in indexes:
        print(f'Dropping index: {idx}')
        db.execute(text(f'DROP INDEX IF EXISTS {idx}'))
    
    # Alter column dimension
    print('Changing column to vector(3072)...')
    db.execute(text('ALTER TABLE content_embeddings ALTER COLUMN embedding TYPE vector(3072)'))
    
    # Create IVFFlat index (supports unlimited dimensions)
    print('Creating IVFFlat index...')
    db.execute(text('''
        CREATE INDEX content_embeddings_embedding_idx 
        ON content_embeddings 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    '''))
    
    db.commit()
    print('✓ Successfully changed embedding to vector(3072) with IVFFlat index')
finally:
    db.close()
