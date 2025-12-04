"""LangChain tool for fetching historical time-series data from InfluxDB."""

from langchain.tools import tool
from typing import List, Optional
from clients import InfluxDBClient


@tool
def get_historical_data_tool(
    entity_id: int,
    data_points: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    agg_type: str = "none",
    time_bucket_duration: str = "P1D"
) -> str:
    """
    Retrieves historical time-series data for a digital twin entity with optional aggregation.
    
    Use this tool when the user asks about:
    - Historical trends, past data, or time-series information
    - Aggregated metrics (max, min, average, sum)
    - "Show me the history...", "What was the trend...", "Average over time...", etc.
    
    Args:
        entity_id: The numeric ID of the entity (e.g., 40976504)
        data_points: Comma-separated data point names (e.g., "noiseCompliance,temperature")
        start_date: Start date in ISO format (e.g., "2025-11-07T00:00:00Z"). Defaults to 7 days ago.
        end_date: End date in ISO format (e.g., "2025-11-15T00:00:00Z"). Defaults to now.
        agg_type: Aggregation type - "none", "max", "min", "average", or "sum". Default: "none"
        time_bucket_duration: Time bucket in ISO 8601 format (e.g., "P1D" for 1 day, "PT1H" for 1 hour)
    
    Returns:
        A formatted string containing the historical data and statistics
    """
    # Convert comma-separated string to list
    data_point_list = [dp.strip() for dp in data_points.split(",")]
    
    client = InfluxDBClient()
    return client.get_historical_data_formatted(
        entity_id=entity_id,
        data_points=data_point_list,
        start_date=start_date,
        end_date=end_date,
        agg_type=agg_type,
        time_bucket_duration=time_bucket_duration
    )
