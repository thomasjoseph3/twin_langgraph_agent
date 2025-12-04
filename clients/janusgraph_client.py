"""JanusGraph API client for fetching current entity state."""

import requests
from typing import Dict, Any
from config import settings


class JanusGraphClient:
    """Client for interacting with JanusGraph API to get current entity state."""
    
    def __init__(self):
        self.base_url = settings.janusgraph_base_url
        self.tenant_id = settings.tenant_id
        self.headers = {"Content-Type": "application/json"}
    
    def get_entity_state(self, entity_id: int) -> Dict[str, Any]:
        """
        Fetch the current state of a digital twin entity.
        
        Args:
            entity_id: The ID of the entity to fetch
            
        Returns:
            Dictionary containing the entity's current state
            
        Raises:
            requests.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/{entity_id}"
        params = {"tenantId": self.tenant_id}
        
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch entity {entity_id}: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - Response: {e.response.text}"
            raise Exception(error_msg)
    
    def get_entity_state_formatted(self, entity_id: int) -> str:
        """
        Fetch entity state and return as formatted string for LLM.
        
        Args:
            entity_id: The ID of the entity to fetch
            
        Returns:
            Formatted string representation of entity state
        """
        try:
            data = self.get_entity_state(entity_id)
            
            # Format the response nicely
            formatted = f"Entity ID: {entity_id}\n"
            formatted += f"Tenant ID: {self.tenant_id}\n"
            formatted += f"\nCurrent State:\n"
            formatted += self._format_dict(data, indent=2)
            
            return formatted
        
        except Exception as e:
            return f"Error fetching entity {entity_id}: {str(e)}"
    
    def _format_dict(self, d: Dict[str, Any], indent: int = 0) -> str:
        """Recursively format dictionary as readable string."""
        result = []
        for key, value in d.items():
            prefix = " " * indent
            if isinstance(value, dict):
                result.append(f"{prefix}{key}:")
                result.append(self._format_dict(value, indent + 2))
            elif isinstance(value, list):
                result.append(f"{prefix}{key}: {value}")
            else:
                result.append(f"{prefix}{key}: {value}")
        return "\n".join(result)
