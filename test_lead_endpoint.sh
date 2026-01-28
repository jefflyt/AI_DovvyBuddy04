#!/bin/bash
# Test script for lead capture endpoint

echo "Testing /api/leads endpoint..."
echo ""

response=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "type": "training",
    "data": {
      "name": "Test User",
      "email": "test@example.com",
      "phone": "+1234567890",
      "location": "Kuala Lumpur",
      "message": "Interested in Open Water certification"
    }
  }')

# Extract body and status code
body=$(echo "$response" | head -n-1)
status=$(echo "$response" | tail -n1)

echo "HTTP Status: $status"
echo "Response Body:"
echo "$body" | jq . 2>/dev/null || echo "$body"
