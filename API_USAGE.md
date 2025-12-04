# API Usage Guide

The Digital Twin AI Agent can be deployed as a REST API for easy integration with your frontend.

## Quick Start

### 1. Install API Dependencies
```bash
pip install fastapi uvicorn
# Or reinstall from updated requirements.txt
pip install -r requirements.txt
```

### 2. Start the API Server
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

### 3. View Interactive Docs
Open in browser: `http://localhost:8000/docs`

---

## API Endpoints

### POST `/query` - Query the Agent

**With Entity Context (Recommended for UI)**

When a user is viewing a specific digital twin in your UI:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current temperature?",
    "entity_context": {
      "entity_id": 40976504,
      "entity_name": "Heat Exchanger HX00-A3",
      "entity_type": "HeatExchanger"
    }
  }'
```

Response:
```json
{
  "response": "The current fluid inlet temperature for Heat Exchanger HX00-A3 is 51.41°C...",
  "entity_context": {
    "entity_id": 40976504,
    "entity_name": "Heat Exchanger HX00-A3",
    "entity_type": "HeatExchanger"
  }
}
```

**Without Entity Context**

User must specify entity ID in the query:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the temperature of entity 40976504?"
  }'
```

### GET `/health` - Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Digital Twin AI Agent"
}
```

---

## Frontend Integration Examples

### React/JavaScript

```javascript
async function askAgent(query, entityContext) {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      entity_context: entityContext
    })
  });
  
  const data = await response.json();
  return data.response;
}

// Usage in a digital twin detail page
const currentEntity = {
  entity_id: 40976504,
  entity_name: "Heat Exchanger HX00-A3",
  entity_type: "HeatExchanger"
};

const answer = await askAgent("What's the temperature?", currentEntity);
console.log(answer);
```

### Python Client

```python
import requests

def query_agent(query: str, entity_context: dict = None):
    response = requests.post(
        "http://localhost:8000/query",
        json={
            "query": query,
            "entity_context": entity_context
        }
    )
    return response.json()["response"]

# Usage
context = {
    "entity_id": 40976504,
    "entity_name": "Heat Exchanger HX00-A3",
    "entity_type": "HeatExchanger"
}

answer = query_agent("What's the efficiency?", entity_context=context)
print(answer)
```

### cURL Examples

```bash
# Simple query with context
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Is it healthy?", "entity_context": {"entity_id": 40976504}}'

# Complex analytical query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare current efficiency with last month", "entity_context": {"entity_id": 40976504}}'

# Query without context (must specify entity)
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me the state of entity 12288"}'
```

---

## Deployment

### Development
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Production (with Gunicorn)
```bash
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
Update the Dockerfile CMD:
```dockerfile
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Then:
```bash
docker build -t digital-twin-agent-api .
docker run -p 8000:8000 --env-file .env digital-twin-agent-api
```

---

## Request/Response Schema

### QueryRequest
```json
{
  "query": "string (required)",
  "entity_context": {
    "entity_id": "integer (required)",
    "entity_name": "string (optional)",
    "entity_type": "string (optional)"
  },
  "metadata": "string (optional)"
}
```

### QueryResponse
```json
{
  "response": "string",
  "entity_context": {
    "entity_id": "integer",
    "entity_name": "string",
    "entity_type": "string"
  }
}
```

---

## CORS Configuration

By default, the API allows all origins (`*`). For production, update `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Authentication (Optional)

Add API key authentication:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.post("/query")
async def query_agent(
    request: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    # ... rest of the code
```

---

## Benefits of Entity Context

✅ **Natural Queries**: "What's the temperature?" instead of "What's the temperature of entity 40976504?"

✅ **UI Integration**: Frontend passes current entity automatically

✅ **Better UX**: Users don't need to know/remember entity IDs

✅ **Contextual AI**: Agent understands which equipment the user is viewing

✅ **Backward Compatible**: Still works without context if ID is in query

---

## Testing

Test with the interactive docs at `http://localhost:8000/docs` or use the examples above.

Example test queries with context:
- "What's the current state?"
- "Is it healthy?"
- "Show me the temperature history"
- "Compare with last week"
- "What maintenance is needed?"

All work without specifying the entity ID! 🎉
