"""
FastAPI wrapper for the Digital Twin AI Agent.
Exposes the agent as a REST API for integration with frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from agent import run_agent
from metadata import get_agent_metadata

app = FastAPI(
    title="Digital Twin AI Agent API",
    description="Natural language interface for digital twin platform",
    version="1.0.0"
)

# CORS configuration - adjust for your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EntityContext(BaseModel):
    """Context about the currently viewed entity."""
    entity_id: int = Field(..., description="ID of the current entity")
    entity_name: Optional[str] = Field(None, description="Name of the entity")
    entity_type: Optional[str] = Field(None, description="Type of entity (e.g., HeatExchanger)")


class QueryRequest(BaseModel):
    """Request body for agent queries."""
    query: str = Field(..., description="User's natural language query")
    entity_context: Optional[EntityContext] = Field(
        None,
        description="Context about the entity the user is currently viewing"
    )
    metadata: Optional[str] = Field(
        None,
        description="Additional context/metadata (optional)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What's the current temperature?",
                "entity_context": {
                    "entity_id": 40976504,
                    "entity_name": "Heat Exchanger HX00-A3",
                    "entity_type": "HeatExchanger"
                }
            }
        }


class QueryResponse(BaseModel):
    """Response from the agent."""
    response: str = Field(..., description="Agent's response")
    entity_context: Optional[EntityContext] = Field(
        None,
        description="Echo of the entity context that was used"
    )
    tools_used: Optional[list] = Field(
        None,
        description="List of tools called and their arguments (for debugging)"
    )


@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Query the digital twin agent with natural language.
    
    If entity_context is provided, the agent will use it as the default entity
    for queries that don't specify an entity ID.
    
    Example with entity context (user viewing specific entity):
    ```
    POST /query
    {
        "query": "What's the temperature?",
        "entity_context": {
            "entity_id": 40976504,
            "entity_name": "Heat Exchanger HX00-A3"
        }
    }
    ```
    
    Example without entity context (user must specify ID):
    ```
    POST /query
    {
        "query": "What's the temperature of entity 40976504?"
    }
    ```
    """
    try:
        # Convert entity_context to dict if provided
        entity_ctx_dict = None
        if request.entity_context:
            entity_ctx_dict = request.entity_context.model_dump(exclude_none=True)
        
        # Get base metadata
        base_metadata = request.metadata or get_agent_metadata()
        
        # Inject current time (UTC) for accurate date calculations
        current_time_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        metadata = f"""{base_metadata}

**CURRENT TIME (UTC):** {current_time_utc}

Use this exact time for all date calculations. 
Example: If user asks "last week", calculate start_date as 7 days before {current_time_utc}"""
        
        # Run the agent and get tool usage
        result = run_agent(
            query=request.query,
            metadata=metadata,
            entity_context=entity_ctx_dict
        )
        
        # Unpack result (response_text, tools_used)
        response_text, tools_used = result
        
        return QueryResponse(
            response=response_text,
            entity_context=request.entity_context,
            tools_used=tools_used
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Digital Twin AI Agent"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Digital Twin AI Agent API",
        "version": "1.0.0",
        "endpoints": {
            "POST /query": "Query the agent",
            "GET /health": "Health check",
            "GET /docs": "API documentation"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
