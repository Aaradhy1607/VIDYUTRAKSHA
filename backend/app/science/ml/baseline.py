"""
VIDYUTRAKSHA - Model A: Lagged Persistence & Climatological Baseline
Provides an honest meteorological reference baseline for model comparison.
"""
from typing import Dict, Any, List
from pydantic import BaseModel


class BaselineModel:
    """Persistence and Climatology benchmark model."""
    MODEL_VERSION = "baseline_pers_v1.0"

    @classmethod
    def predict(
        cls,
        current_dbz: float,
        current_flash_rate: float,
        horizon_minutes: int,
        climatological_prior: float = 0.12
    ) -> Dict[str, float]:
        """
        Lagged persistence with exponential autocorrelation decay towards climatology:
        P(t + h) = P(t) * exp(-h / tau) + (1 - exp(-h / tau)) * P_clim
        """
        # Convective decorrelation time scale tau ~45 minutes
        tau = 45.0
        decay = float(2.71828 ** (-horizon_minutes / tau))
        
        # Current state indicator
        curr_lightning_state = 1.0 if current_flash_rate > 1.0 else 0.0
        curr_storm_state = 1.0 if current_dbz >= 35.0 else 0.0
        curr_rain_state = 1.0 if current_dbz >= 40.0 else 0.0
        curr_wind_state = 1.0 if current_dbz >= 48.0 else 0.0
        
        p_light = curr_lightning_state * decay + (1.0 - decay) * climatological_prior
        p_storm = curr_storm_state * decay + (1.0 - decay) * (climatological_prior * 1.2)
        p_rain = curr_rain_state * decay + (1.0 - decay) * (climatological_prior * 0.8)
        p_wind = curr_wind_state * decay + (1.0 - decay) * (climatological_prior * 0.4)
        
        return {
            "p_lightning": round(float(p_light), 3),
            "p_thunderstorm": round(float(p_storm), 3),
            "p_heavy_rain": round(float(p_rain), 3),
            "p_severe_wind": round(float(p_wind), 3),
            "model_version": cls.MODEL_VERSION
        }
