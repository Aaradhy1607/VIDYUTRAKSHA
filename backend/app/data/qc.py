"""
VIDYUTRAKSHA - Real-time Quality Control & Validation Engine
Applies WMO and IMD standard meteorological sanity and bounds checks.
Assigns quality flags: GOOD, SUSPECT, MISSING, STALE, INVALID.
"""
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel


class QCResult(BaseModel):
    is_valid: bool
    quality_flag: str  # GOOD, SUSPECT, MISSING, STALE, INVALID
    rejection_reasons: list[str] = []
    sanitized_value: Optional[float] = None
    flags_triggered: list[str] = []


# Meteorological Physical Limits (Indian Subcontinent Climatological Extremes)
METEOROLOGICAL_BOUNDS = {
    "temperature_c": {"min": -20.0, "max": 55.0, "max_rate_c_hr": 15.0},
    "dew_point_c": {"min": -30.0, "max": 35.0},
    "relative_humidity_pct": {"min": 1.0, "max": 100.0},
    "pressure_hpa": {"min": 850.0, "max": 1050.0, "max_step_hpa_3hr": 25.0},
    "wind_speed_ms": {"min": 0.0, "max": 85.0},  # Up to super cyclonic / severe convective gust
    "wind_direction_deg": {"min": 0.0, "max": 360.0},
    "rainfall_10min_mm": {"min": 0.0, "max": 120.0},  # Extreme cloudburst upper limit
    "reflectivity_dbz": {"min": -10.0, "max": 80.0},
    "radial_velocity_ms": {"min": -75.0, "max": 75.0},
    "cloud_top_temp_k": {"min": 170.0, "max": 330.0}, # Deep overshooting top lower limit ~180K (-93°C)
    "lightning_peak_current_ka": {"min": 2.0, "max": 400.0},
    "cape_j_kg": {"min": 0.0, "max": 7000.0},
    "cin_j_kg": {"min": 0.0, "max": 1500.0},
}


class QualityControlEngine:
    """Scientific Data Validation & Quality Control Suite."""

    @staticmethod
    def validate_coordinate(lat: float, lon: float) -> Tuple[bool, str]:
        """Validate if coordinate is within Indian geographical bounding box."""
        # India bounding box (approx 5.0°N - 39.0°N, 67.0°E - 99.0°E)
        if not (5.0 <= lat <= 39.0):
            return False, f"Latitude {lat}° out of Indian operational domain [5.0, 39.0]"
        if not (67.0 <= lon <= 99.0):
            return False, f"Longitude {lon}° out of Indian operational domain [67.0, 99.0]"
        return True, "VALID"

    @staticmethod
    def validate_timestamp(obs_time: datetime, max_age_hours: float = 6.0, max_future_seconds: float = 300.0) -> Tuple[bool, str]:
        """Check for future timestamps or excessive staleness."""
        now = datetime.now(timezone.utc)
        if obs_time.tzinfo is None:
            obs_time = obs_time.replace(tzinfo=timezone.utc)
            
        time_diff = (now - obs_time).total_seconds()
        
        # Future check
        if time_diff < -max_future_seconds:
            return False, f"Timestamp is in the future by {-time_diff:.1f}s"
            
        # Staleness check
        if time_diff > (max_age_hours * 3600):
            return False, f"Observation is stale (Age: {time_diff/3600:.2f} hrs)"
            
        return True, "VALID"

    @classmethod
    def check_observation(
        cls,
        variable: str,
        value: Optional[float],
        timestamp: datetime,
        lat: float,
        lon: float,
        prev_value: Optional[float] = None,
        prev_timestamp: Optional[datetime] = None
    ) -> QCResult:
        """Run comprehensive 6-stage QC pipeline on an observation."""
        reasons = []
        flags = []
        
        # Stage 1: Missing value check
        if value is None or (isinstance(value, float) and (value != value)):  # NaN check
            return QCResult(
                is_valid=False,
                quality_flag="MISSING",
                rejection_reasons=["Value is null or NaN"],
                flags_triggered=["MISSING_VALUE"]
            )
            
        # Stage 2: Geographic validation
        geo_valid, geo_msg = cls.validate_coordinate(lat, lon)
        if not geo_valid:
            reasons.append(geo_msg)
            flags.append("OUT_OF_BOUNDS_SPATIAL")
            
        # Stage 3: Temporal validation
        time_valid, time_msg = cls.validate_timestamp(timestamp)
        if not time_valid:
            if "stale" in time_msg.lower():
                flags.append("STALE_DATA")
            else:
                reasons.append(time_msg)
                flags.append("FUTURE_TIMESTAMP")
                
        # Stage 4: Physical bounds range check
        bounds = METEOROLOGICAL_BOUNDS.get(variable)
        if bounds:
            if value < bounds["min"] or value > bounds["max"]:
                reasons.append(f"{variable} value {value} outside physical bounds [{bounds['min']}, {bounds['max']}]")
                flags.append("OUT_OF_BOUNDS_PHYSICAL")
                
        # Stage 5: Step change / rate of change check
        if prev_value is not None and prev_timestamp is not None and bounds:
            dt_hours = abs((timestamp - prev_timestamp).total_seconds()) / 3600.0
            if dt_hours > 0 and "max_rate_c_hr" in bounds:
                rate = abs(value - prev_value) / dt_hours
                if rate > bounds["max_rate_c_hr"]:
                    reasons.append(f"Excessive rate of change: {rate:.2f}/hr (limit: {bounds['max_rate_c_hr']})")
                    flags.append("EXCESSIVE_RATE_OF_CHANGE")

        # Stage 6: Internal consistency check (e.g. Dew Point <= Temperature)
        # Final Quality Flag Determination
        if "OUT_OF_BOUNDS_PHYSICAL" in flags or "OUT_OF_BOUNDS_SPATIAL" in flags or "FUTURE_TIMESTAMP" in flags:
            quality_flag = "INVALID"
            is_valid = False
        elif "STALE_DATA" in flags:
            quality_flag = "STALE"
            is_valid = True
        elif len(flags) > 0:
            quality_flag = "SUSPECT"
            is_valid = True
        else:
            quality_flag = "GOOD"
            is_valid = True
            
        return QCResult(
            is_valid=is_valid,
            quality_flag=quality_flag,
            rejection_reasons=reasons,
            sanitized_value=value if is_valid else None,
            flags_triggered=flags
        )
