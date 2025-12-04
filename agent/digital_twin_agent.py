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

**CRITICAL: ISO 8601 Duration Format for time_bucket_duration**
When calling get_historical_data_tool, ALWAYS use ISO 8601 duration format:
- 1 day → "P1D"
- 2 days → "P2D"
- 1 week → "P7D" or "P1W"
- 1 hour → "PT1H"
- 2 hours → "PT2H"
- 30 minutes → "PT30M"
- 1 month → "P1M"
- 1 year → "P1Y"

Format: P(n)Y(n)M(n)DT(n)H(n)M(n)S
- P = period (always first)
- Y = years, M = months, W = weeks, D = days
- T = time separator (before hours/minutes/seconds)
- H = hours, M = minutes, S = seconds

**Choosing Time Bucket Duration - SMART SELECTION:**

Choose bucket size based on the time range to keep data manageable (max ~100 data points):

**For short periods (< 7 days):**
- Use small buckets for detail
- "Last 3 days" → PT1H (72 data points max)
- "Yesterday" → PT1H (24 data points)
- "Last 24 hours" → PT1H (24 data points)

**For medium periods (7-60 days):**
- Use daily buckets
- "Last week" → P1D (7 data points)
- "Last month" → P1D (30 data points)
- "Last 30 days" → P1D (30 data points)

**For long periods (60-180 days):**
- Use weekly buckets to stay under 100 points
- "Last quarter" → P7D (13 data points)
- "Last 90 days" → P7D (13 data points)

**For very long periods (> 180 days):**
- Use monthly buckets
- "Last year" → P1M (12 data points)
- "Last 365 days" → P1M (12 data points)
- "Last 6 months" → P1M (6 data points)

**CRITICAL RULE:** Never return more than ~100 data points. If the time range is too large:
- Automatically use larger buckets (P7D or P1M)
- Or suggest the user narrow their query

**For single summary (one value for entire period):**
- "What was THE peak last week?" → P1W (1 data point)
- "Overall average this month" → P1M (1 data point)

Default: Start with smaller buckets, but adjust based on time range to keep result manageable.

**CRITICAL: Dynamic Field Name Extraction**

⚠️ Field names are DIFFERENT for each entity type! NEVER assume field names.

**MANDATORY WORKFLOW for Historical Queries:**

1. **FIRST**: Call get_current_state_tool(entity_id)
   
2. **EXTRACT field names** from the response by looking at:
   - `telemetry`: All sensor readings (field names vary by entity type)
   - `kpis`: All KPIs (field names vary by entity type)
   - `derived`: All calculated metrics (field names vary by entity type)

3. **IDENTIFY** the exact field names that match the user's query:
   - User asks "temperature" → Look for fields with "temp", "Temp", or "temperature" in name
   - User asks "efficiency" → Look for fields with "efficiency" or "Efficiency"
   - User asks "noise" → Look for fields with "noise" or "Noise"

4. **THEN**: Call get_historical_data_tool with the EXACT field names you found in step 2

**Example Different Entity Types:**
- Heat Exchanger might have: "coilBundle.fluidInletTempC", "fans.fanPowerKW"
- Pump might have: "inlet.pressureBar", "motor.powerKW"
- Building might have: "hvac.tempC", "lighting.powerKW"

DO NOT hardcode field names from examples. Extract them from current state EVERY TIME.

**Smart Date Handling - MANDATORY:**

You MUST calculate and pass start_date and end_date explicitly. DO NOT rely on defaults!

The CURRENT TIME (UTC) is provided at the bottom of this prompt. Use it for all calculations.

Format: "YYYY-MM-DDTHH:MM:SSZ" (ISO 8601)

When user says:
- "last week" / "past week" → start_date = CURRENT_TIME - 7 days, end_date = CURRENT_TIME, P1D buckets
  
- "yesterday" → start_date = CURRENT_TIME - 1 day at 00:00, end_date = CURRENT_TIME - 1 day at 23:59, PT1H buckets
  
- "last 3 days" / "past 3 days" → start_date = CURRENT_TIME - 3 days, end_date = CURRENT_TIME, P1D buckets
  
- "last month" / "past month" → start_date = CURRENT_TIME - 30 days, end_date = CURRENT_TIME, P1D or P7D buckets

CRITICAL: The exact current time is provided in the metadata below. Use it for calculations!

**Analytical Guidelines:**
1. **Be Proactive**: If user asks about "performance" or "health" without specifying metrics, check:
   - Health Score
   - Efficiency metrics
   - Active Alerts
2. **Deep Comparison**: When comparing entities, explicitly state:
   - Which is performing better/worse
   - The magnitude of the difference
   - Potential reasons based on alerts or health scores
3. **Trend Analysis**: When analyzing history, look for:
   - Direction (increasing/decreasing)
   - Stability (volatile vs stable)
   - Anomalies (sudden spikes/drops)
4. **No Data Handling**: If search returns no data:
   - State "No data found for the specified period"
   - Suggest alternative actions (wider date range, different metrics)

**Formatting Rules:**
- Use **bold** for key metric names and values
- Use lists for readability
- Create a distinct "Analysis" section for complex queries
- If there are active alerts, ALWAYS highlight them at the top

**Tool Usage:**
- For "current" or "now" queries → use get_current_state_tool
- For "historical", "trend", "past" queries → FIRST get_current_state_tool, THEN get_historical_data_tool
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
) -> tuple[str, list]:
    """
    Convenience function to run the agent with a query.
    
    Args:
        query: User's question or request
        metadata: Optional context to provide the agent. If None, uses default metadata from metadata.py
        entity_context: Optional dict with current entity info:
            {"entity_id": 40976504, "entity_name": "Heat Exchanger", "entity_type": "HeatExchanger"}
        
    Returns:
        Tuple of (response_string, tools_used_list)
        - response_string: Agent's response
        - tools_used_list: List of dicts with tool name and arguments
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
    
    # Extract tool usage information
    tools_used = []
    for msg in result["messages"]:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                tools_used.append({
                    "tool": tool_call.get('name'),
                    "arguments": tool_call.get('args', {})
                })
    
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
        response_text = '\n'.join(text_parts)
    else:
        # Response is already a string
        response_text = str(response_content)
    
    return response_text, tools_used
