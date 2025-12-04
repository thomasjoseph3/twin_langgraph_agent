"""LangGraph-based AI agent for Digital Twin platform."""

from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from config import settings
from tools import get_current_state_tool, get_historical_data_tool


class AgentState(TypedDict):
    """State of the agent graph."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    metadata: Optional[str]


def create_digital_twin_agent(
    metadata: Optional[str] = None,
    entity_context: Optional[dict] = None
):
    """
    Create a LangGraph agent for the Digital Twin platform.
    
    The agent can:
    - Fetch current state of digital twin entities (heat exchangers, pumps, buildings, etc.)
    - Retrieve historical time-series data with aggregation
    - Answer questions using natural language
    
    Args:
        metadata: Optional context/metadata to provide the agent with domain knowledge
        entity_context: Optional dict with current entity info from frontend:
            {
                "entity_id": 40976504,
                "entity_name": "Heat Exchanger HX00-A3",
                "entity_type": "HeatExchanger"
            }
        
    Returns:
        Compiled LangGraph agent ready for invocation
    """
    # Initialize Google Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.gemini_api_key,
        temperature=0,
        convert_system_message_to_human=True
    )
    
    # Define tools
    tools = [get_current_state_tool, get_historical_data_tool]
    
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Build system prompt with metadata
    system_prompt = """You are an AI assistant for a Digital Twin platform that monitors industrial equipment and buildings.

You have access to two data sources:
1. **Current State (JanusGraph)**: Real-time state and properties of digital twin entities
2. **Historical Data (InfluxDB)**: Time-series data with aggregation capabilities

**Available Entities:**
- Heat Exchangers
- Centrifugal Pumps  
- Buildings
- Other industrial equipment

**Your capabilities:**
- Retrieve current status and properties of entities
- Analyze historical trends and patterns
- Perform aggregations (max, min, average, sum) on time-series data
- Answer questions about entity performance and behavior

**Analytical Guidelines:**
1. **Be Proactive**: If a user asks about "performance" or "health" without specifying metrics, automatically check Key KPIs like:
   - Health Score
   - Efficiency (Energy Efficiency, Fans Efficiency)
   - Noise Compliance
   - Active Alerts
2. **Deep Comparison**: When comparing entities, don't just list their values. Explicitly state:
   - Which is performing better/worse
   - The magnitude of the difference (e.g., "Entity A is 15% more efficient")
   - Potential reasons based on available alerts or health scores
3. **Trend Analysis**: When analyzing history, look for:
   - Direction (increasing/decreasing)
   - Stability (volatile vs stable)
   - Anomalies (sudden spikes/drops)
4. **No Data Handling**: If a search returns no data:
   - Clearly state "No data found for the specified period"
   - Suggest alternative actions (e.g., "Try a wider date range" or "Check if the entity ID is correct")

**Formatting Rules:**
- Use **bold** for key metric names and values
- Use lists for readability
- Create a distinct "Analysis" section for complex queries
- If there are active alerts, ALWAYS highlight them at the top

**Tool Usage:**
- For "current" or "now" queries → use get_current_state_tool
- For "historical", "trend", "past" queries → use get_historical_data_tool
- If you need an entity ID, ask the user to provide it"""

    if metadata:
        system_prompt += f"\n\n**Additional Context:**\n{metadata}"
    
    # Add entity context if provided
    if entity_context:
        entity_id = entity_context.get("entity_id")
        entity_name = entity_context.get("entity_name", f"Entity {entity_id}")
        entity_type = entity_context.get("entity_type", "Unknown")
        
        system_prompt += f"""

**Current Entity Context:**
The user is currently viewing: **{entity_name}** (ID: {entity_id}, Type: {entity_type})

IMPORTANT: When the user asks questions without specifying an entity ID, they are referring to this entity.
Examples:
- "What's the temperature?" → Use entity_id={entity_id}
- "Show me the history" → Use entity_id={entity_id}
- "Is it healthy?" → Use entity_id={entity_id}

Only query other entities if the user explicitly asks about them by ID or name."""
    
    # Define agent node
    def agent_node(state: AgentState):
        """Agent reasoning node."""
        messages = state["messages"]
        
        # Add system message if not present
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=system_prompt)] + list(messages)
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    # Define routing logic
    def should_continue(state: AgentState):
        """Determine if agent should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, continue to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        # Otherwise, end
        return END
    
    # Create tool node
    tool_node = ToolNode(tools)
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # After tools, always return to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def run_agent(
    query: str,
    metadata: Optional[str] = None,
    entity_context: Optional[dict] = None
) -> str:
    """
    Convenience function to run the agent with a query.
    
    Args:
        query: User's question or request
        metadata: Optional context to provide the agent. If None, uses default metadata from metadata.py
        entity_context: Optional dict with current entity info:
            {"entity_id": 40976504, "entity_name": "Heat Exchanger", "entity_type": "HeatExchanger"}
        
    Returns:
        Agent's response as a string
    """
    from metadata import get_agent_metadata
    
    if metadata is None:
        metadata = get_agent_metadata()
    
    agent = create_digital_twin_agent(metadata, entity_context)
    
    # Create initial state
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "metadata": metadata
    }
    
    # Run the agent
    result = agent.invoke(initial_state)
    
    # Extract final response
    final_message = result["messages"][-1]
    response_content = final_message.content
    
    # Handle different response formats from Gemini
    if isinstance(response_content, list):
        # Response is a list of content parts, extract text
        text_parts = []
        for part in response_content:
            if isinstance(part, dict) and 'text' in part:
                text_parts.append(part['text'])
            elif isinstance(part, str):
                text_parts.append(part)
        return '\n'.join(text_parts)
    else:
        # Response is already a string
        return str(response_content)
