#!/bin/zsh
# Verification script for EMBEDDING_MODEL configuration
# Run this to verify the environment is correctly configured

# Source .zshrc to get environment variables
source ~/.zshrc 2>/dev/null

echo "=== DovvyBuddy Embedding Configuration Verification ==="
echo ""

echo "1. Checking shell environment variable:"
if [ -n "$EMBEDDING_MODEL" ]; then
    echo "   ✓ EMBEDDING_MODEL=$EMBEDDING_MODEL"
else
    echo "   ✗ EMBEDDING_MODEL not set"
    echo "   Run: source ~/.zshrc"
fi
echo ""

echo "2. Checking .zshrc configuration:"
if grep -q "EMBEDDING_MODEL=models/gemini-embedding-001" ~/.zshrc 2>/dev/null; then
    echo "   ✓ Found in ~/.zshrc"
else
    echo "   ✗ Not found in ~/.zshrc"
fi
echo ""

echo "3. Checking backend .env file:"
if grep -q "EMBEDDING_MODEL=models/gemini-embedding-001" src/backend/.env 2>/dev/null; then
    echo "   ✓ Found in src/backend/.env"
else
    echo "   ✗ Check src/backend/.env"
fi
echo ""

echo "4. Testing Python config loading:"
cd src/backend 2>/dev/null && python3 -c "from app.core.config import settings; print(f'   ✓ Loaded: {settings.embedding_model}')" 2>/dev/null || echo "   ✗ Failed to load config"
echo ""

echo "5. Testing embedding functionality:"
echo "   Run manually: cd src/backend && python3 -m pytest tests/integration/services/test_embeddings_integration.py -q"
echo "   Expected: 3 passed, 2 warnings"
echo ""

echo "=== Verification Complete ==="
