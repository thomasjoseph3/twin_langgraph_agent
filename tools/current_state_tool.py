"""LangChain tool for fetching current entity state from JanusGraph."""

from langchain.tools import tool
from clients import JanusGraphClient


@tool
def get_current_state_tool(entity_id: int) -> str:
    """
    Retrieves the current state of a digital twin entity (heat exchanger, pump, building, etc.).
    
    Use this tool when the user asks about:
    - Current status, state, or properties of an entity
    - Real-time data or present conditions
    - "What is the current...", "Show me the status of...", etc.
    
    Args:
        entity_id: The numeric ID of the entity to query (e.g., 40976504, 12288, 24808)
    
    Returns:
        A formatted string containing the entity's current state and properties
    """
    client = JanusGraphClient()
    return client.get_entity_state_formatted(entity_id)
