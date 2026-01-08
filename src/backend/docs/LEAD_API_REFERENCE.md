# Lead Capture API Reference

Quick reference for the `/api/leads` endpoint.

## Endpoint

```
POST /api/leads
```

## Request Format

### Training Lead

```json
{
  "type": "training",
  "data": {
    "name": "string (required, 1-100 chars)",
    "email": "string (required, valid email)",
    "phone": "string (optional, max 20 chars)",
    "certification_level": "string (optional, max 50 chars)",
    "interested_certification": "string (optional, max 50 chars)",
    "preferred_location": "string (optional, max 100 chars)",
    "message": "string (optional, max 2000 chars)"
  },
  "session_id": "uuid (optional)"
}
```

### Trip Lead

```json
{
  "type": "trip",
  "data": {
    "name": "string (required, 1-100 chars)",
    "email": "string (required, valid email)",
    "phone": "string (optional, max 20 chars)",
    "destination": "string (optional, max 100 chars)",
    "travel_dates": "string (optional, max 100 chars)",
    "group_size": "integer (optional, 1-50)",
    "budget": "string (optional, max 50 chars)",
    "message": "string (optional, max 2000 chars)"
  },
  "session_id": "uuid (optional)"
}
```

## Response Format

### Success (201 Created)

```json
{
  "success": true,
  "lead_id": "uuid"
}
```

### Validation Error (400 Bad Request)

```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": [
    {
      "field": "email",
      "message": "value is not a valid email address"
    }
  ]
}
```

### Server Error (500 Internal Server Error)

```json
{
  "error": "Failed to capture lead",
  "code": "DB_ERROR"
}
```

## Example Usage

### cURL

```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "type": "training",
    "data": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "certification_level": "Open Water",
      "interested_certification": "Advanced Open Water",
      "preferred_location": "Bali, Indonesia",
      "message": "Looking to get certified next month"
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/api/leads', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    type: 'trip',
    data: {
      name: 'Jane Smith',
      email: 'jane@example.com',
      destination: 'Maldives',
      travel_dates: 'June 2026',
      group_size: 4,
      message: 'Interested in liveaboard diving'
    }
  })
});

const result = await response.json();
console.log(result.lead_id);
```

### Python (httpx)

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        'http://localhost:8000/api/leads',
        json={
            'type': 'training',
            'data': {
                'name': 'John Doe',
                'email': 'john@example.com',
                'certification_level': 'Open Water',
                'interested_certification': 'Advanced Open Water'
            }
        }
    )
    result = response.json()
    print(f"Lead ID: {result['lead_id']}")
```

## Validation Rules

### Common Fields (Both Lead Types)
- `name`: Required, 1-100 characters, trimmed
- `email`: Required, valid email format (RFC 5322)
- `phone`: Optional, max 20 characters (flexible format for international)
- `message`: Optional, max 2000 characters, trimmed

### Training-Specific Fields
- `certification_level`: Optional, max 50 characters
- `interested_certification`: Optional, max 50 characters
- `preferred_location`: Optional, max 100 characters

### Trip-Specific Fields
- `destination`: Optional, max 100 characters
- `travel_dates`: Optional, max 100 characters (flexible format)
- `group_size`: Optional, integer between 1 and 50
- `budget`: Optional, max 50 characters (flexible format)

## Email Behavior

When a lead is successfully captured:

1. **Lead is persisted to database** (critical path, always succeeds or returns 500)
2. **Email notification is sent** (fire-and-forget, failures logged but don't fail request)
3. **Email includes:**
   - Lead type (Training Inquiry or Trip Planning Request)
   - All submitted contact and request details
   - Diver profile from session (if `session_id` provided)
   - Professional formatting with HTML and plain text versions
   - Reply-to set to lead's email address

## Session Context Enrichment

If `session_id` is provided, the lead will be enriched with diver profile data from the session:

```json
{
  "type": "training",
  "data": { ... },
  "session_id": "existing-session-uuid"
}
```

Diver profile may include:
- Certification level
- Experience (number of dives)
- Interests (e.g., wreck diving, photography)
- Concerns/fears (e.g., deep water, strong currents)

This context appears in a separate section in the email notification.

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request validation failed (see `details` field) |
| `CONFIG_ERROR` | 500 | Email service not configured (missing env vars) |
| `DB_ERROR` | 500 | Database operation failed |
| `UNKNOWN` | 500 | Unexpected server error |

## Notes

- Endpoint is currently **rate-limited** (to be added in future PR)
- No authentication required (guest submissions)
- Lead persistence takes priority over email delivery
- Email failures are logged but don't fail the request
- All leads are tracked in database with unique UUID
