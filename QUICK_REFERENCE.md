# Digital Twin AI Agent - Quick Reference

## Project Commands

### Local Development
```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

# Run
python main.py
```

### Docker
```bash
# Build
docker build -t digital-twin-agent .

# Run
docker run -it --env-file .env digital-twin-agent

# Using Docker Compose (recommended)
docker-compose up -d
docker-compose exec digital-twin-agent python main.py
docker-compose logs -f
docker-compose down
```

## Project Structure
```
├── config/          # Configuration management
├── clients/         # API clients (JanusGraph, InfluxDB)
├── tools/           # LangChain tools
├── agent/           # LangGraph agent
├── metadata.py      # Metadata provider
├── main.py          # Entry point
├── .env             # Your credentials (not in git)
├── Dockerfile       # Docker build
└── docker-compose.yml
```

## Environment Variables
```bash
GEMINI_API_KEY=AIzaSy...           # Required
LLM_MODEL=gemini-2.0-flash-exp     # Required
PLATFORM_BASE_URL=https://...      # Required
TENANT_ID=d559...                  # Required
```

## Example Queries
- "What is the current state of entity 40976504?"
- "Show me the noise compliance history for entity 12288"
- "Compare the efficiency of entity 40976504 and 12288"
- "Get the maximum noise level for entity 40976504"

## Adding Features

### New Tool
1. Create `tools/my_tool.py`
2. Export in `tools/__init__.py`
3. Register in `agent/digital_twin_agent.py`

### New API Client
1. Create `clients/my_client.py`
2. Export in `clients/__init__.py`
3. Create tool if needed

## Troubleshooting
| Issue | Solution |
|-------|----------|
| `API key not valid` | Check `GEMINI_API_KEY` in `.env` |
| `ModuleNotFoundError` | Activate venv, run `pip install -r requirements.txt` |
| `ValidationError` | Ensure all required env vars in `.env` |
| Empty responses | Check entity ID, widen date range |

## Documentation
- **README.md** - User guide
- **DEVELOPER_GUIDE.md** - Architecture & development
- **DEPLOYMENT.md** - Docker & production deployment
- **This file** - Quick reference

## Resources
- LangGraph: https://langchain-ai.github.io/langgraph/
- Gemini API: https://ai.google.dev/docs
- Pydantic: https://docs.pydantic.dev/
