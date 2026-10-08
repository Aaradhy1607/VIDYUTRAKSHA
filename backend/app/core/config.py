"""
VIDYUTRAKSHA - Application Configuration & Settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "VIDYUTRAKSHA"
    SYSTEM_VERSION: str = "1.0.0-PROD"
    DESCRIPTION: str = "AI-Powered Multi-Modal Thunderstorm & Lightning Nowcasting and Early Warning Platform for India"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="development, staging, production, demo")
    DEBUG: bool = Field(default=False)
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "*"]
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./vidyutraksha.db"
    
    # Spatial Analysis Grid Configuration
    INDIA_GRID_BBOX: List[float] = [68.0, 6.0, 98.0, 38.0]  # [min_lon, min_lat, max_lon, max_lat]
    DEFAULT_GRID_RESOLUTION_DEG: float = 0.05  # ~5.5 km resolution
    HIGHRES_GRID_RESOLUTION_DEG: float = 0.02  # ~2.2 km resolution
    
    # Operational Thresholds (Meteorologically Calibrated for Indian Subcontinent)
    REFLECTIVITY_CONVECTIVE_THRESH_DBZ: float = 35.0   # Deep convection initiation threshold
    REFLECTIVITY_SEVERE_THRESH_DBZ: float = 45.0       # Severe thunderstorm / hail potential threshold
    REFLECTIVITY_HAIL_THRESH_DBZ: float = 55.0         # Probable hail core
    LIGHTNING_FLASH_RATE_JUMP_RATIO: float = 2.0       # 200% increase in 10 mins (severe precursor)
    CAPE_ELEVATED_J_KG: float = 1000.0                 # Elevated instability threshold
    CAPE_EXTREME_J_KG: float = 2500.0                  # Extreme convective potential
    VERTICAL_SHEAR_0_6KM_MS: float = 15.0              # Deep layer shear threshold for organized supercells
    
    # Forecast Horizons (Minutes)
    FORECAST_HORIZONS: List[int] = [0, 15, 30, 60, 120, 180]
    
    # Alert Thresholds (Risk Score 0-100)
    ALERT_GREEN_MAX: float = 25.0
    ALERT_YELLOW_MAX: float = 50.0
    ALERT_ORANGE_MAX: float = 75.0
    # Above 75 is RED
    
    # Model Drift Monitoring Thresholds
    DRIFT_PSI_WARNING: float = 0.10
    DRIFT_PSI_CRITICAL: float = 0.25
    DRIFT_KS_PVALUE_THRESH: float = 0.05

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
