"""
VIDYUTRAKSHA - Lightning Kinematics & Jump Detection Feature Engine
Implements standard Lightning Jump Algorithm (Schultz et al., 2011) as a precursor for severe convection.
"""
import numpy as np
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class LightningFeatures(BaseModel):
    flash_rate_per_min: float
    flash_density_per_km2_hr: float
    flash_rate_10min_trend_pct: float
    lightning_jump_detected: bool
    jump_sigma_value: float
    ic_cg_ratio: float
    mean_peak_current_ka: float
    positive_polarity_pct: float
    lightning_severity_index: str  # NONE, LOW, ELEVATED, SEVERE, INTENSE


class LightningFeatureEngine:
    """Computes total lightning activity, flash rate growth, and 2-sigma lightning jumps."""

    @staticmethod
    def calculate_flash_rate(flash_timestamps_sec: List[float], window_seconds: float = 300.0) -> float:
        """Calculate recent flash rate (flashes/minute) over window."""
        if not flash_timestamps_sec:
            return 0.0
        count = len(flash_timestamps_sec)
        minutes = max(window_seconds / 60.0, 0.1)
        return float(count / minutes)

    @staticmethod
    def detect_lightning_jump(
        historical_rates_per_min: List[float],
        sigma_threshold: float = 2.0,
        min_rate_threshold: float = 10.0
    ) -> Tuple[bool, float]:
        """
        2-Sigma Lightning Jump Algorithm:
        A lightning jump occurs when the time rate of change of total lightning flash rate
        (DFR/dt) exceeds 2 standard deviations (2 * sigma) of the historical background rate of change
        AND the current rate is at least min_rate_threshold flashes/min.
        """
        if len(historical_rates_per_min) < 5:
            # Insufficient history
            if historical_rates_per_min and historical_rates_per_min[-1] >= 25.0:
                return True, 2.5
            return False, 0.0
            
        rates = np.array(historical_rates_per_min, dtype=float)
        # Compute first differences (DFR/dt)
        diffs = np.diff(rates)
        current_diff = diffs[-1]
        
        # Historical baseline excluding latest jump candidate
        baseline_diffs = diffs[:-1] if len(diffs) > 1 else diffs
        mean_diff = np.mean(baseline_diffs)
        std_diff = np.std(baseline_diffs)
        
        if std_diff <= 1e-4:
            sigma_val = float(current_diff / 2.0) if current_diff > 0 else 0.0
        else:
            sigma_val = float((current_diff - mean_diff) / std_diff)
            
        current_rate = rates[-1]
        jump_detected = bool(sigma_val >= sigma_threshold and current_rate >= min_rate_threshold)
        
        return jump_detected, round(sigma_val, 2)

    @classmethod
    def evaluate_lightning_cluster(
        cls,
        strike_lat_lons: List[Tuple[float, float]],
        cluster_area_km2: float,
        historical_flash_rates: List[float],
        peak_currents_ka: Optional[List[float]] = None,
        polarities: Optional[List[str]] = None,
        ic_count: int = 0,
        cg_count: int = 0
    ) -> LightningFeatures:
        """Extract multi-parameter lightning metrics for a storm cell."""
        flash_count = len(strike_lat_lons)
        current_rate = float(flash_count / 5.0)  # 5-minute aggregation -> flashes/min
        
        # Flash density (flashes/km²/hr)
        area = max(cluster_area_km2, 10.0)
        density = float((current_rate * 60.0) / area)
        
        # Historical rate progression & trend
        rates_series = list(historical_flash_rates) + [current_rate]
        if len(rates_series) >= 2 and rates_series[-2] > 0.1:
            trend_pct = float(((current_rate - rates_series[-2]) / rates_series[-2]) * 100.0)
        else:
            trend_pct = float(100.0 if current_rate > 0 else 0.0)
            
        jump_detected, sigma_val = cls.detect_lightning_jump(rates_series)
        
        # IC:CG Ratio
        total_cg = cg_count if cg_count > 0 else max(int(flash_count * 0.25), 1)
        total_ic = ic_count if ic_count > 0 else max(flash_count - total_cg, 0)
        ic_cg = float(total_ic / max(total_cg, 1))
        
        # Current and Polarity
        if peak_currents_ka and len(peak_currents_ka) > 0:
            mean_current = float(np.mean(np.abs(peak_currents_ka)))
        else:
            mean_current = 24.5  # Standard typical CG current in kA
            
        if polarities and len(polarities) > 0:
            pos_count = sum(1 for p in polarities if p == "+")
            pos_pct = float((pos_count / len(polarities)) * 100.0)
        else:
            pos_pct = 12.0  # Standard typical positive CG percentage
            
        # Severity rating
        if jump_detected or current_rate >= 40.0:
            severity = "INTENSE"
        elif current_rate >= 20.0 or density >= 0.5:
            severity = "SEVERE"
        elif current_rate >= 5.0:
            severity = "ELEVATED"
        elif current_rate > 0.0:
            severity = "LOW"
        else:
            severity = "NONE"
            
        return LightningFeatures(
            flash_rate_per_min=round(current_rate, 1),
            flash_density_per_km2_hr=round(density, 3),
            flash_rate_10min_trend_pct=round(trend_pct, 1),
            lightning_jump_detected=jump_detected,
            jump_sigma_value=sigma_val,
            ic_cg_ratio=round(ic_cg, 2),
            mean_peak_current_ka=round(mean_current, 1),
            positive_polarity_pct=round(pos_pct, 1),
            lightning_severity_index=severity
        )
