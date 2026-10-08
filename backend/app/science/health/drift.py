"""
VIDYUTRAKSHA - Feature & Model Drift Detection Engine
Implements Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) two-sample statistical tests.
"""
import numpy as np
from typing import Dict, Any, List, Tuple
from scipy import stats
from pydantic import BaseModel


class FeatureDriftReport(BaseModel):
    feature_name: str
    psi_value: float
    psi_status: str  # NO_DRIFT (<0.1), MODERATE_DRIFT (0.1-0.25), SIGNIFICANT_DRIFT (>0.25)
    ks_statistic: float
    ks_p_value: float
    drift_detected: bool
    reference_mean: float
    current_mean: float
    recommendation: str


class DriftDetectionEngine:
    """Monitors atmospheric and storm feature distribution shifts over time."""

    @staticmethod
    def calculate_psi(reference: np.ndarray, target: np.ndarray, num_buckets: int = 10) -> float:
        """
        Compute Population Stability Index (PSI):
        PSI = sum((Actual% - Expected%) * ln(Actual% / Expected%))
        PSI < 0.10: No significant distribution change
        0.10 <= PSI < 0.25: Moderate shift / warning
        PSI >= 0.25: Significant drift / retraining required
        """
        ref_clean = reference[~np.isnan(reference)]
        tgt_clean = target[~np.isnan(target)]
        
        if len(ref_clean) < 10 or len(tgt_clean) < 10:
            return 0.0
            
        # Define bucket quantiles from reference
        quantiles = np.linspace(0, 100, num_buckets + 1)
        bins = np.percentile(ref_clean, quantiles)
        bins[0] -= 1e-5
        bins[-1] += 1e-5
        
        # Calculate counts
        ref_counts, _ = np.histogram(ref_clean, bins=bins)
        tgt_counts, _ = np.histogram(tgt_clean, bins=bins)
        
        # Proportions with Laplace smoothing to avoid division by zero
        ref_pct = (ref_counts + 1e-4) / (len(ref_clean) + 1e-4 * num_buckets)
        tgt_pct = (tgt_counts + 1e-4) / (len(tgt_clean) + 1e-4 * num_buckets)
        
        psi = np.sum((tgt_pct - ref_pct) * np.log(tgt_pct / ref_pct))
        return float(np.clip(psi, 0.0, 5.0))

    @classmethod
    def evaluate_feature_drift(
        cls,
        feature_name: str,
        reference_data: List[float],
        current_data: List[float]
    ) -> FeatureDriftReport:
        """Run two-sample KS-test and PSI for a given feature."""
        ref_arr = np.array(reference_data, dtype=float)
        cur_arr = np.array(current_data, dtype=float)
        
        psi = cls.calculate_psi(ref_arr, cur_arr)
        
        # Two-sample Kolmogorov-Smirnov Test
        ks_res = stats.ks_2samp(ref_arr, cur_arr)
        ks_stat = float(ks_res.statistic)
        ks_p = float(ks_res.pvalue)
        
        if psi >= 0.25:
            psi_status = "SIGNIFICANT_DRIFT"
            drift_detected = True
            rec = "CRITICAL: Severe feature distribution shift. Model recalibration or retraining advised."
        elif psi >= 0.10 or ks_p < 0.01:
            psi_status = "MODERATE_DRIFT"
            drift_detected = True
            rec = "WARNING: Moderate distribution shift detected. Increase verification monitoring."
        else:
            psi_status = "NO_DRIFT"
            drift_detected = False
            rec = "NORMAL: Feature distribution matches baseline training climatology."
            
        return FeatureDriftReport(
            feature_name=feature_name,
            psi_value=round(psi, 3),
            psi_status=psi_status,
            ks_statistic=round(ks_stat, 3),
            ks_p_value=round(ks_p, 4),
            drift_detected=drift_detected,
            reference_mean=round(float(np.mean(ref_arr)), 2),
            current_mean=round(float(np.mean(cur_arr)), 2),
            recommendation=rec
        )
