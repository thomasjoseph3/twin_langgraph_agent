# Digital Twin AI Agent - Developer Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Setup & Installation](#setup--installation)
4. [Configuration](#configuration)
5. [Core Components](#core-components)
6. [Adding New Features](#adding-new-features)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The Digital Twin AI Agent is built using **LangGraph** and **Google Gemini** to provide natural language querying capabilities for digital twin data.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                   (CLI / main.py)                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              LangGraph Agent                             │
│          (agent/digital_twin_agent.py)                   │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Google Gemini LLM (gemini-2.0-flash-exp)      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────┐        ┌────────────────────┐      │
│  │ Current State  │        │ Historical Data    │      │
│  │     Tool       │        │      Tool          │      │
│  └────────────────┘        └────────────────────┘      │
└───────────┬─────────────────────┬───────────────────────┘
            │                     │
            ▼                     ▼
┌──────────────────┐    ┌──────────────────────────┐
│  JanusGraph API  │    │    InfluxDB API          │
│  (Current State) │    │  (Historical Data)       │
└──────────────────┘    └──────────────────────────┘
```

### Key Technologies

- **LangGraph**: For building the agentic workflow with state management
- **LangChain**: Core components (tools, prompts, message handling)
- **Google Gemini API**: LLM for natural language understanding
- **Pydantic**: Configuration and data validation
- **Requests**: HTTP client for API calls

---

## Project Structure

```
/home/toobler/Desktop/inflex janus/
├── config/                    # Configuration management
│   ├── __init__.py
│   └── settings.py           # Pydantic settings loader
│
├── clients/                   # API clients
│   ├── __init__.py
│   ├── janusgraph_client.py  # JanusGraph API wrapper
│   └── influxdb_client.py    # InfluxDB API wrapper
│
├── tools/                     # LangChain tools
│   ├── __init__.py
│   ├── current_state_tool.py # Tool for current entity state
│   └── historical_data_tool.py # Tool for time-series data
│
├── agent/                     # LangGraph agent
│   ├── __init__.py
│   └── digital_twin_agent.py # Main agent implementation
│
├── metadata.py               # Metadata provider
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (excluded from git)
├── .env.example             # Template for .env
├── .gitignore               # Git exclusions
└── README.md                # User documentation
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+ (3.11+ recommended)
- pip
- Virtual environment (recommended)
- Google Gemini API key

### Local Development Setup

1. **Clone the repository** (if versioned):
   ```bash
   git clone <repository-url>
   cd "inflex janus"
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

### Docker Setup

See [Deployment](#deployment) section for Docker instructions.

---

## Configuration

### Environment Variables

All configuration is managed through `.env` file. Never commit this file to version control.

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSyABC123...` | Yes |
| `LLM_MODEL` | Gemini model to use | `gemini-2.0-flash-exp` | Yes |
| `PLATFORM_BASE_URL` | Digital twin platform base URL | `https://acme.thingspine.com/api` | Yes |
| `TENANT_ID` | Tenant identifier | `d55921e7-b179-4837-8288-bb9cc9c6ec1f` | Yes |
| `API_KEY` | Platform API key (optional) | `your_api_key` | No |
| `AUTH_TOKEN` | Platform auth token (optional) | `your_token` | No |

### Configuration Management

Configuration is handled by `config/settings.py` using Pydantic Settings:

```python
from config import settings

# Access configuration
print(settings.gemini_api_key)
print(settings.llm_model)
print(settings.janusgraph_base_url)
```

### Changing LLM Models

Edit `.env`:
```bash
# Fast experimental model (default)
LLM_MODEL=gemini-2.0-flash-exp

# Stable fast model
LLM_MODEL=gemini-1.5-flash

# More capable model
LLM_MODEL=gemini-1.5-pro
```

---

## Core Components

### 1. API Clients (`clients/`)

#### JanusGraphClient
Handles communication with JanusGraph API for current entity state.

**Key Methods:**
- `get_entity_state(entity_id: int) -> Dict[str, Any]`: Fetch raw entity data
- `get_entity_state_formatted(entity_id: int) -> str`: Get formatted string for LLM

**Usage:**
```python
from clients import JanusGraphClient

client = JanusGraphClient()
data = client.get_entity_state(40976504)
```

#### InfluxDBClient
Handles communication with InfluxDB API for historical time-series data.

**Key Methods:**
- `get_historical_data(...)`: Fetch time-series data with aggregation
- `get_historical_data_formatted(...)`: Get formatted string for LLM

**Aggregation Types:** `none`, `max`, `min`, `average`, `sum`

**Usage:**
```python
from clients import InfluxDBClient

client = InfluxDBClient()
data = client.get_historical_data(
    entity_id=40976504,
    data_points=["noiseCompliance", "temperature"],
    start_date="2025-11-01T00:00:00Z",
    end_date="2025-11-08T00:00:00Z",
    agg_type="average",
    time_bucket_duration="P1D"  # ISO 8601 duration
)
```

### 2. LangChain Tools (`tools/`)

Tools are the building blocks that the agent can use to answer queries.

#### Current State Tool
```python
@tool
def get_current_state_tool(entity_id: int) -> str:
    """Retrieves the current state of a digital twin entity."""
```

#### Historical Data Tool
```python
@tool
def get_historical_data_tool(
    entity_id: int,
    data_points: str,  # Comma-separated
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    agg_type: str = "none",
    time_bucket_duration: str = "P1D"
) -> str:
    """Retrieves historical time-series data with aggregation."""
```

### 3. LangGraph Agent (`agent/`)

The agent orchestrates tool selection and execution using a graph-based workflow.

**Graph Structure:**
```
START → Agent Node → Should Continue?
           ↑              ├─→ Tools → Agent Node
           └──────────────┘
                          └─→ END
```

**Key Functions:**
- `create_digital_twin_agent(metadata: Optional[str])`: Create agent instance
- `run_agent(query: str, metadata: Optional[str])`: Convenience function

**Usage:**
```python
from agent import create_digital_twin_agent
from langchain_core.messages import HumanMessage

agent = create_digital_twin_agent(metadata="Custom context")

result = agent.invoke({
    "messages": [HumanMessage(content="Your query here")]
})
```

### 4. Metadata Management (`metadata.py`)

Centralized metadata provider for agent context.

**Functions:**
- `get_agent_metadata() -> str`: Returns default metadata
- `get_custom_metadata(user_context: str) -> str`: Adds custom context
- `fetch_metadata_from_api() -> str`: Placeholder for dynamic metadata

**To customize:**
Edit `get_agent_metadata()` to fetch from your actual source (API, database, file).

---

## Adding New Features

### Adding a New Tool

1. **Create tool file** in `tools/`:
   ```python
   # tools/my_custom_tool.py
   from langchain.tools import tool
   
   @tool
   def my_custom_tool(param: str) -> str:
       """Description of what this tool does."""
       # Your implementation
       return "Result"
   ```

2. **Export in `tools/__init__.py`**:
   ```python
   from .my_custom_tool import my_custom_tool
   
   __all__ = [
       "get_current_state_tool",
       "get_historical_data_tool",
       "my_custom_tool"
   ]
   ```

3. **Register with agent** in `agent/digital_twin_agent.py`:
   ```python
   from tools import (
       get_current_state_tool,
       get_historical_data_tool,
       my_custom_tool
   )
   
   tools = [
       get_current_state_tool,
       get_historical_data_tool,
       my_custom_tool
   ]
   ```

### Adding a New API Client

1. Create client in `clients/my_api_client.py`
2. Follow the pattern of existing clients
3. Export in `clients/__init__.py`
4. Create corresponding tool if needed

### Modifying the System Prompt

Edit `agent/digital_twin_agent.py`, find the `system_prompt` variable and update the instructions.

---

## Deployment

### Docker Deployment

1. **Build image**:
   ```bash
   docker build -t digital-twin-agent .
   ```

2. **Run container**:
   ```bash
   docker run -it --env-file .env digital-twin-agent
   ```

3. **Using Docker Compose**:
   ```bash
   docker-compose up
   ```

### Production Considerations

1. **Environment Variables**: Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
2. **Logging**: Add structured logging for production monitoring
3. **Error Handling**: Implement retry logic and circuit breakers for API calls
4. **Rate Limiting**: Respect API rate limits
5. **Monitoring**: Add health checks and metrics

### API Deployment

To expose the agent as an API:

1. Add FastAPI to `requirements.txt`
2. Create `api.py`:
   ```python
   from fastapi import FastAPI
   from agent import run_agent
   
   app = FastAPI()
   
   @app.post("/query")
   async def query(query: str):
       response = run_agent(query)
       return {"response": response}
   ```

3. Run with: `uvicorn api:app --host 0.0.0.0 --port 8000`

---

## Troubleshooting

### Common Issues

#### API Key Errors
```
Error: API key not valid
```
**Solution**: Verify `GEMINI_API_KEY` in `.env` is correct and has no extra spaces/quotes.

#### Import Errors
```
ModuleNotFoundError: No module named 'langchain'
```
**Solution**: Ensure virtual environment is activated and dependencies are installed.

#### Configuration Not Loading
```
ValidationError: Field required
```
**Solution**: Check `.env` file exists and contains all required variables. Ensure no quotes around values.

#### Empty API Responses
```
No data found for the specified period
```
**Solution**: 
- Check entity ID is valid
- Try wider date range for historical queries
- Verify API endpoints are accessible

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing API Connectivity

```python
from clients import JanusGraphClient, InfluxDBClient

# Test JanusGraph
jg_client = JanusGraphClient()
print(jg_client.get_entity_state(40976504))

# Test InfluxDB
influx_client = InfluxDBClient()
print(influx_client.get_historical_data(
    entity_id=40976504,
    data_points=["noiseCompliance"]
))
```

---

## Development Workflow

1. **Feature Branch**: Create a branch for your feature
2. **Make Changes**: Implement your feature/fix
3. **Test Locally**: Run the agent and verify behavior
4. **Update Documentation**: Update this guide if needed
5. **Commit**: Use clear commit messages
6. **Pull Request**: Create PR for review

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all functions
- Keep functions focused (single responsibility)
- Use meaningful variable names

## Testing

Currently using manual testing. Future: Add pytest for unit tests.

Example test structure:
```python
# tests/test_clients.py
def test_janusgraph_client():
    client = JanusGraphClient()
    data = client.get_entity_state(40976504)
    assert data is not None
```

---

## Support & Resources

- **README**: User-facing documentation
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Google Gemini Docs**: https://ai.google.dev/docs
- **Pydantic Docs**: https://docs.pydantic.dev/

## License

[Your License Here]
