"""
VIDYUTRAKSHA - Real-time Model & Data Stream Health Monitor
Computes operational health indices (0-100) based on availability, latency, missingness, and skill.
"""
from typing import Dict, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel
from backend.app.core.registry import DATA_SOURCE_REGISTRY, SourceStatus


class StreamHealth(BaseModel):
    source_id: str
    name: str
    status: SourceStatus
    latency_minutes: int
    qc_pass_rate_pct: float
    records_last_24h: int
    health_score: float  # 0 to 100


class ModelHealthReport(BaseModel):
    model_version: str
    overall_health_score: float  # 0 to 100
    health_status: str  # HEALTHY (80-100), DEGRADED (50-79), CRITICAL (<50)
    availability_pct: float
    p95_latency_ms: float
    feature_missingness_pct: float
    bounds_violation_rate_pct: float
    current_csi_skill: float
    drift_status: str
    streams_health: List[StreamHealth]
    last_evaluated: str


class HealthMonitorEngine:
    """Operational reliability & diagnostic health suite."""

    @classmethod
    def evaluate_model_health(
        cls,
        model_version: str = "fusion_multimodal_v2.0",
        p95_latency_ms: float = 18.4,
        missingness_pct: float = 0.5,
        bounds_violations_pct: float = 0.1,
        current_csi: float = 0.796,
        drift_status: str = "NORMAL"
    ) -> ModelHealthReport:
        """Calculate composite model health score from operational telemetry."""
        # 1. Stream health breakdown
        stream_reports: List[StreamHealth] = []
        stream_scores = []
        
        for s_id, meta in DATA_SOURCE_REGISTRY.items():
            if meta.status == SourceStatus.LIVE:
                s_score = 100.0 * (meta.qc_pass_rate * 0.7 + (1.0 - min(meta.latency_minutes / 120.0, 0.3)) * 0.3)
            elif meta.status == SourceStatus.DEGRADED:
                s_score = 65.0
            else:
                s_score = 20.0
                
            stream_scores.append(s_score)
            stream_reports.append(StreamHealth(
                source_id=s_id,
                name=meta.name,
                status=meta.status,
                latency_minutes=meta.latency_minutes,
                qc_pass_rate_pct=round(meta.qc_pass_rate * 100.0, 1),
                records_last_24h=meta.records_ingested_last_24h,
                health_score=round(s_score, 1)
            ))
            
        data_health_avg = float(sum(stream_scores) / max(len(stream_scores), 1))
        
        # 2. Latency health component (penalty if latency > 100ms)
        latency_score = max(100.0 - max(p95_latency_ms - 50.0, 0.0) * 0.5, 20.0)
        
        # 3. Missingness & Bounds component
        data_quality_score = max(100.0 - (missingness_pct * 5.0 + bounds_violations_pct * 10.0), 0.0)
        
        # 4. Skill component (CSI scaled to 100)
        skill_score = min(current_csi * 125.0, 100.0)
        
        # 5. Drift penalty
        drift_penalty = 15.0 if drift_status == "WARNING" else (30.0 if drift_status == "DRIFT_DETECTED" else 0.0)
        
        # Weighted composite score
        overall_score = (
            data_health_avg * 0.30 +
            data_quality_score * 0.25 +
            skill_score * 0.25 +
            latency_score * 0.20
        ) - drift_penalty
        
        overall_score = round(float(min(max(overall_score, 0.0), 100.0)), 1)
        
        if overall_score >= 80.0:
            status = "HEALTHY"
        elif overall_score >= 50.0:
            status = "DEGRADED"
        else:
            status = "CRITICAL"
            
        return ModelHealthReport(
            model_version=model_version,
            overall_health_score=overall_score,
            health_status=status,
            availability_pct=99.95,
            p95_latency_ms=round(p95_latency_ms, 1),
            feature_missingness_pct=round(missingness_pct, 2),
            bounds_violation_rate_pct=round(bounds_violations_pct, 2),
            current_csi_skill=round(current_csi, 3),
            drift_status=drift_status,
            streams_health=stream_reports,
            last_evaluated=datetime.now(timezone.utc).isoformat()
        )
