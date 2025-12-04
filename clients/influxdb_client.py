"""InfluxDB API client for fetching historical entity data."""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config import settings


class InfluxDBClient:
    """Client for interacting with InfluxDB API to get historical time-series data."""
    
    def __init__(self):
        self.base_url = settings.influxdb_base_url
        self.headers = {"Content-Type": "application/json"}
    
    def get_historical_data(
        self,
        entity_id: int,
        data_points: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        agg_type: str = "none",
        time_bucket_duration: str = "P1D"
    ) -> Dict[str, Any]:
        """
        Fetch historical time-series data for an entity.
        
        Args:
            entity_id: The ID of the entity
            data_points: List of data point names to fetch (e.g., ["noiseCompliance", "time"])
            start_date: Start date in ISO format (defaults to 7 days ago)
            end_date: End date in ISO format (defaults to now)
            agg_type: Aggregation type - "none", "max", "min", "average", "sum"
            time_bucket_duration: Time bucket duration in ISO 8601 format (e.g., "P1D" for 1 day)
            
        Returns:
            Dictionary containing the historical data
            
        Raises:
            requests.HTTPError: If the API request fails
        """
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.utcnow().isoformat() + "Z"
        if not start_date:
            start_dt = datetime.utcnow() - timedelta(days=7)
            start_date = start_dt.isoformat() + "Z"
        
        # Build request payload
        payload = {
            "dataConfig": {
                "end": end_date,
                "start": start_date,
                "aggType": agg_type,
                "entityId": entity_id,
                "dataPoint": data_points,
                "timeBucket": {
                    "duration": time_bucket_duration
                }
            }
        }
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch historical data for entity {entity_id}: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - Response: {e.response.text}"
            raise Exception(error_msg)
    
    def get_historical_data_formatted(
        self,
        entity_id: int,
        data_points: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        agg_type: str = "none",
        time_bucket_duration: str = "P1D"
    ) -> str:
        """
        Fetch historical data and return as formatted string for LLM.
        
        Args:
            Same as get_historical_data()
            
        Returns:
            Formatted string representation of historical data
        """
        try:
            data = self.get_historical_data(
                entity_id,
                data_points,
                start_date,
                end_date,
                agg_type,
                time_bucket_duration
            )
            
            # Format the response nicely
            formatted = f"Historical Data for Entity {entity_id}\n"
            formatted += f"Data Points: {', '.join(data_points)}\n"
            formatted += f"Period: {start_date or 'Last 7 days'} to {end_date or 'Now'}\n"
            formatted += f"Aggregation: {agg_type}\n"
            formatted += f"Time Bucket: {time_bucket_duration}\n\n"
            formatted += "Results:\n"
            formatted += self._format_data(data, indent=2)
            
            return formatted
        
        except Exception as e:
            return f"Error fetching historical data for entity {entity_id}: {str(e)}"
    
    def _format_data(self, data: Any, indent: int = 0) -> str:
        """Recursively format data as readable string."""
        if isinstance(data, dict):
            result = []
            for key, value in data.items():
                prefix = " " * indent
                if isinstance(value, (dict, list)):
                    result.append(f"{prefix}{key}:")
                    result.append(self._format_data(value, indent + 2))
                else:
                    result.append(f"{prefix}{key}: {value}")
            return "\n".join(result)
        elif isinstance(data, list):
            result = []
            for i, item in enumerate(data):
                prefix = " " * indent
                if isinstance(item, (dict, list)):
                    result.append(f"{prefix}[{i}]:")
                    result.append(self._format_data(item, indent + 2))
                else:
                    result.append(f"{prefix}[{i}]: {item}")
            return "\n".join(result)
        else:
            return " " * indent + str(data)
