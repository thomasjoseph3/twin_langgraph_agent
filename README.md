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

## ✨ Key Features

- **Natural Language Querying**: Ask questions in plain English (e.g., "How is the heat exchanger performing?").
- **Multi-Source Data**: Combines real-time state (JanusGraph) and historical data (InfluxDB).
- **Smart Historical Analysis**:
    - **Dynamic Field Extraction**: Automatically identifies correct metrics for any entity type.
    - **Smart Time Bucketing**: Auto-selects daily, hourly, or weekly buckets based on query range.
    - **ISO 8601 Support**: Full understanding of time durations (`P1D`, `PT1H`).
- **Context Awareness**: Remembers the current entity being viewed.
- **Tool Usage Tracking**: Debugging visibility into exactly which tools and arguments the agent used.
- **Production Ready**: Dockerized, configurable, and stateless.

## 📚 Documentation

- **[Developer Guide](DEVELOPER_GUIDE.md)**: Detailed architecture, tool mechanics, and setup instructions.
- **[API Usage](API_USAGE.md)**: API endpoints and integration examples.
- **[Deployment Guide](DEPLOYMENT.md)**: Docker and production deployment.
- **[Test Questions](TEST_QUESTIONS.md)**: 40+ example queries to test capabilities.

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

### Docker
```bash
docker build -t digital-twin-agent .
docker run -p 8000:8000 --env-file .env digital-twin-agent
```

### Docker Compose
```bash
docker-compose up -d
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: pydantic_settings` | Run: `pip install pydantic-settings` |
| `API key not valid` | Check `.env` has real API key (not placeholder) |
| `404 Not Found` | Ensure endpoint is `/query` not `/queries` |
| Server won't start | Activate venv: `source venv/bin/activate` |

---

## Support

- Interactive API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
