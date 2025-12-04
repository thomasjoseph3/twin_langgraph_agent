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
    Retrieves historical time-series data for a digital twin entity.
    
     CRITICAL: Field names vary by entity type. You MUST extract field names from get_current_state_tool FIRST!
    
    Use this tool when the user asks about historical trends, past performance, or time-based analysis.
    
    Args:
        entity_id: ID of the entity (e.g., 40976504)
        
        data_points: Comma-separated list of EXACT field names from the entity's current state.
            WORKFLOW:
            1. First call get_current_state_tool(entity_id)
            2. Look at the response's telemetry/kpis/derived sections
            3. Extract EXACT field names that match user's query
            4. Pass those exact names here
            
            DO NOT use hardcoded examples. Field names differ per entity type:
            - Heat Exchanger example: "coilBundle.fluidInletTempC,fans.fanPowerKW"
            - Pump example: "inlet.pressureBar,motor.powerKW"
            - Building example: "hvac.tempC,lighting.powerKW"
            
        start_date: Start date in ISO 8601 format (e.g., "2025-11-01T00:00:00Z")
            ⚠️ You should ALWAYS calculate and pass this explicitly based on user query
            Calculate from current time, don't rely on defaults
            
        end_date: End date in ISO 8601 format (e.g., "2025-11-08T00:00:00Z")
            ⚠️ You should ALWAYS pass this (usually current time)
            Use current time as end_date unless user specifies otherwise
            
        agg_type: Aggregation type:
            - "none": Raw data points
            - "average": Average value (good for temps, efficiency)
            - "max": Maximum value (good for peak detection)
            - "min": Minimum value (good for minimums)
            - "sum": Sum of values
            
        time_bucket_duration: ISO 8601 duration for time bucketing:
            For trend analysis (day-by-day): Use smaller buckets
            - "P1D" = 1 day (default - good for week/month queries)
            - "PT1H" = 1 hour (good for yesterday/today queries)
            - "PT30M" = 30 minutes
            
            For single summary: Use period bucket
            - "P1W" = 1 week (for "overall last week")
            - "P1M" = 1 month (for "overall this month")
            
    Returns:
        Historical data formatted as a string
        
    Examples:
        # Get daily temperature trend for last week (7 data points)
        get_historical_data_tool(40976504, "coilBundle.fluidInletTempC", None, None, "average", "P1D")
        
        # Get THE peak for entire week (1 data point)
        get_historical_data_tool(40976504, "fans.fanPowerKW", None, None, "max", "P1W")
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
