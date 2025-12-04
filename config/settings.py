"""Configuration management for the Digital Twin AI Agent."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google Gemini Configuration
    gemini_api_key: str
    llm_model: str = "gemini-2.5-flash"
    
    # Platform API Configuration
    platform_base_url: str = "https://acme.thingspine.com/api"
    tenant_id: str
    
    # Optional Authentication
    api_key: Optional[str] = None
    auth_token: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def janusgraph_base_url(self) -> str:
        """JanusGraph API endpoint base URL."""
        return f"{self.platform_base_url}/data/graph/entities/v2"
    
    @property
    def influxdb_base_url(self) -> str:
        """InfluxDB API endpoint base URL."""
        return f"{self.platform_base_url}/data/entity-history"
    
    def get_auth_headers(self) -> dict:
        """Get authentication headers if configured."""
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        return headers


# Global settings instance
settings = Settings()
