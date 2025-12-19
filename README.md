# Digital Twin AI Agent - Production Setup

## Quick Start

### 1. Install Dependencies
```bash
cd "/home/toobler/Desktop/inflex janus"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Start API Server
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

API available at: `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

---

## Project Structure

```
/home/toobler/Desktop/inflex janus/
├── api.py              # FastAPI server (entry point)
├── metadata.py         # Agent context provider
├── requirements.txt    # Python dependencies
├── .env               # Your configuration (don't commit!)
├── .env.example       # Template
├── config/            # Settings management
│   ├── settings.py    # Loads .env file
│   └── __init__.py
├── clients/           # API clients
│   ├── janusgraph_client.py
│   ├── influxdb_client.py
│   └── __init__.py
├── tools/             # LangChain tools
│   ├── current_state_tool.py
│   ├── historical_data_tool.py
│   └── __init__.py
└── agent/             # LangGraph agent
    ├── digital_twin_agent.py
    └── __init__.py
```

---

## API Usage

### Query with Entity Context (Recommended)

User is viewing entity 40976504 in your UI:

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

**User doesn't need to mention the entity ID - the agent knows from context!**

### Query without Context (Old Way)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the state of entity 40976504?"
  }'
```

### JavaScript/React Example

```javascript
async function askAgent(query) {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      query: query,
      entity_context: {
        entity_id: currentEntityId,  // From your UI state
        entity_name: currentEntityName
      }
    })
  });
  
  const data = await response.json();
  return data.response;
}

// Usage
const answer = await askAgent("What's the efficiency?");
```

---

## Configuration (.env)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key | `AIzaSy...` |
| `LLM_MODEL` | ✅ Yes | Gemini model | `gemini-2.5-flash` |
| `PLATFORM_BASE_URL` | ✅ Yes | Digital twin platform base URL | `https://acme.thingspine.com/api` |
| `TENANT_ID` | ✅ Yes | Your tenant ID | `d55921e7-...` |

---

## How It Works

1. **Server starts**: Uvicorn loads `api.py`
2. **Config loads**: `config/settings.py` reads `.env` file
3. **Request arrives**: POST to `/query`
4. **Agent processes**:
   - Receives query + entity_context
   - LLM understands user is viewing specific entity
   - Chooses appropriate tool (current state or historical data)
   - Calls JanusGraph/InfluxDB API
   - Returns natural language response

---

## Development

### Add New Tool

1. Create `tools/my_tool.py`
2. Export in `tools/__init__.py`
3. Register in `agent/digital_twin_agent.py`

### Change LLM Model

Edit `.env`:
```bash
LLM_MODEL=gemini-1.5-pro  # or gemini-2.5-flash
```

### Customize Metadata

Edit `metadata.py` → `get_agent_metadata()` function

---

## Deployment

### Docker (Quick)
```bash
# Build and run with port mapping
docker build -t digital-twin-agent .
docker run -d -p 8000:8000 --env-file .env --name digital-twin-agent digital-twin-agent
```

### Docker Compose (Recommended)
```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Note:** Port mapping (`-p 8000:8000` or `ports:` in docker-compose.yml) is required!

For detailed deployment instructions, troubleshooting, and production setup, see **[DEPLOYMENT.md](DEPLOYMENT.md)**.

---

## Verification

After starting the server (Docker or local), verify it's working:

```bash
# Health check
curl http://localhost:8000/health

# Should return: {"status":"healthy","service":"Digital Twin AI Agent"}
```

Access interactive API docs: **http://localhost:8000/docs**

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: pydantic_settings` | Run: `pip install pydantic-settings` |
| `API key not valid` | Check `.env` has real API key (not placeholder) |
| `404 Not Found` (Docker) | Missing port mapping - see [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting) |
| `address already in use` | Port 8000 occupied - see [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting) |
| Server won't start | Activate venv: `source venv/bin/activate` |

For comprehensive troubleshooting, see **[DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting)**.

---

## Support

- Interactive API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
