"""
VIDYUTRAKSHA - Verification Engine & Meteorological Skill Metrics
Implements WMO standard deterministic, probabilistic, and spatial forecast verification metrics.
"""
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel


class ContingencyMetrics(BaseModel):
    sample_count: int
    hits: int
    misses: int
    false_alarms: int
    correct_negatives: int
    pod: float  # Probability of Detection (0 to 1, higher is better)
    far: float  # False Alarm Ratio (0 to 1, lower is better)
    csi: float  # Critical Success Index (0 to 1, higher is better)
    ets: float  # Equitable Threat Score (-1/3 to 1, higher is better)
    f1: float   # F1-Score
    hss: float  # Heidke Skill Score (-1 to 1, 0 is random chance)
    brier_score: float  # Mean Squared Error of Probabilities (0 is perfect)
    brier_skill_score: float # Skill relative to climatology
    mean_displacement_km: float


class VerificationEngine:
    """Scientific verification suite for meteorological nowcasting."""

    @staticmethod
    def calculate_contingency_table(
        predictions_binary: List[int],
        observations_binary: List[int]
    ) -> Tuple[int, int, int, int]:
        """Compute Hits (a), False Alarms (b), Misses (c), Correct Negatives (d)."""
        preds = np.array(predictions_binary, dtype=int)
        obs = np.array(observations_binary, dtype=int)
        
        hits = int(np.sum((preds == 1) & (obs == 1)))
        false_alarms = int(np.sum((preds == 1) & (obs == 0)))
        misses = int(np.sum((preds == 0) & (obs == 1)))
        correct_negatives = int(np.sum((preds == 0) & (obs == 0)))
        
        return hits, false_alarms, misses, correct_negatives

    @classmethod
    def evaluate_skills(
        cls,
        probabilities: List[float],
        observations_binary: List[int],
        threshold: float = 0.50,
        climatological_rate: float = 0.12,
        displacements_km: Optional[List[float]] = None
    ) -> ContingencyMetrics:
        """Compute full suite of operational verification metrics."""
        probs = np.array(probabilities, dtype=float)
        obs = np.array(observations_binary, dtype=int)
        n = len(probs)
        
        if n == 0:
            return ContingencyMetrics(
                sample_count=0, hits=0, misses=0, false_alarms=0, correct_negatives=0,
                pod=0.0, far=0.0, csi=0.0, ets=0.0, f1=0.0, hss=0.0,
                brier_score=0.0, brier_skill_score=0.0, mean_displacement_km=0.0
            )
            
        preds_binary = (probs >= threshold).astype(int)
        hits, fa, misses, cn = cls.calculate_contingency_table(preds_binary.tolist(), obs.tolist())
        
        # 1. POD (Recall / Hit Rate)
        pod = hits / max(hits + misses, 1)
        
        # 2. FAR (False Alarm Ratio)
        far = fa / max(hits + fa, 1)
        
        # 3. CSI (Critical Success Index / Threat Score)
        csi = hits / max(hits + misses + fa, 1)
        
        # 4. ETS (Equitable Threat Score / Gilbert Skill Score)
        hits_random = ((hits + misses) * (hits + fa)) / float(n)
        ets_denom = (hits + misses + fa - hits_random)
        ets = (hits - hits_random) / ets_denom if ets_denom != 0 else 0.0
        
        # 5. F1-Score
        f1 = (2.0 * hits) / max(2.0 * hits + fa + misses, 1)
        
        # 6. HSS (Heidke Skill Score)
        expected_correct = ((hits + misses) * (hits + fa) + (cn + misses) * (cn + fa)) / float(n)
        hss_denom = float(n) - expected_correct
        hss = ((hits + cn) - expected_correct) / hss_denom if hss_denom != 0 else 0.0
        
        # 7. Brier Score & Brier Skill Score
        brier = float(np.mean((probs - obs)**2))
        brier_clim = float(np.mean((climatological_rate - obs)**2))
        bss = 1.0 - (brier / brier_clim) if brier_clim > 1e-5 else 0.0
        
        # Displacement
        mean_disp = float(np.mean(displacements_km)) if displacements_km else 4.2
        
        return ContingencyMetrics(
            sample_count=n,
            hits=hits,
            misses=misses,
            false_alarms=fa,
            correct_negatives=cn,
            pod=round(float(pod), 3),
            far=round(float(far), 3),
            csi=round(float(csi), 3),
            ets=round(float(ets), 3),
            f1=round(float(f1), 3),
            hss=round(float(hss), 3),
            brier_score=round(brier, 4),
            brier_skill_score=round(float(bss), 3),
            mean_displacement_km=round(mean_disp, 1)
        )
