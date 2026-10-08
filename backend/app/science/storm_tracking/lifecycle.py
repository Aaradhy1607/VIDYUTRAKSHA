"""
VIDYUTRAKSHA - Storm Lifecycle State Machine
Classifies storm lifecycle states: INITIATING, GROWING, MATURE, DECAYING, DISSIPATING, SPLIT, MERGED.
"""
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class LifecycleState(str, Enum):
    INITIATING = "INITIATING"
    GROWING = "GROWING"
    MATURE = "MATURE"
    DECAYING = "DECAYING"
    DISSIPATING = "DISSIPATING"
    SPLIT = "SPLIT"
    MERGED = "MERGED"


class LifecycleTransition(BaseModel):
    previous_state: LifecycleState
    current_state: LifecycleState
    area_growth_rate_pct: float
    intensity_growth_rate_dbz: float
    flash_rate_trend_pct: float
    lifetime_minutes: int
    is_split: bool = False
    is_merged: bool = False


class StormLifecycleEngine:
    """Classify storm cell developmental stage based on physical growth and kinematics."""

    @staticmethod
    def evaluate_lifecycle(
        lifetime_min: int,
        area_prev_km2: float,
        area_curr_km2: float,
        dbz_prev: float,
        dbz_curr: float,
        flash_rate_prev: float,
        flash_rate_curr: float,
        dt_minutes: float = 10.0
    ) -> LifecycleTransition:
        """Determine thermodynamic and kinematic lifecycle stage."""
        if dt_minutes <= 0:
            dt_minutes = 10.0
            
        # Growth rates
        if area_prev_km2 > 0:
            area_growth = ((area_curr_km2 - area_prev_km2) / area_prev_km2) * (10.0 / dt_minutes) * 100.0
        else:
            area_growth = 100.0
            
        dbz_growth = (dbz_curr - dbz_prev) * (10.0 / dt_minutes)
        
        if flash_rate_prev > 0.1:
            fr_trend = ((flash_rate_curr - flash_rate_prev) / flash_rate_prev) * (10.0 / dt_minutes) * 100.0
        else:
            fr_trend = 100.0 if flash_rate_curr > 0 else 0.0
            
        # State logic
        if lifetime_min <= 15 and area_growth > 25.0 and dbz_curr < 45.0:
            current_state = LifecycleState.INITIATING
        elif area_growth > 15.0 or dbz_growth > 3.0 or fr_trend > 30.0:
            current_state = LifecycleState.GROWING
        elif dbz_curr >= 45.0 and abs(area_growth) <= 20.0:
            current_state = LifecycleState.MATURE
        elif area_growth < -15.0 or dbz_growth < -3.0 or fr_trend < -30.0:
            if area_curr_km2 < 25.0 or dbz_curr < 35.0:
                current_state = LifecycleState.DISSIPATING
            else:
                current_state = LifecycleState.DECAYING
        else:
            current_state = LifecycleState.MATURE if dbz_curr >= 40.0 else LifecycleState.GROWING
            
        return LifecycleTransition(
            previous_state=LifecycleState.INITIATING,
            current_state=current_state,
            area_growth_rate_pct=round(area_growth, 1),
            intensity_growth_rate_dbz=round(dbz_growth, 1),
            flash_rate_trend_pct=round(fr_trend, 1),
            lifetime_minutes=lifetime_min
        )
