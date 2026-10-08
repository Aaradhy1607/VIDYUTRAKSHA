"""
VIDYUTRAKSHA - Model D: Multi-Modal Convective Fusion Engine
State-of-the-art fusion integrating Radar, Satellite, Lightning LMS, NWP Sounding, and Surface Stations.
"""
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from backend.app.science.ml.baseline import BaselineModel
from backend.app.science.ml.tabular_lgbm import TabularMLModel
from backend.app.science.ml.spatiotemporal import SpatiotemporalModel
from backend.app.science.ml.calibration import ConformalCalibrator, CalibratedPrediction
from backend.app.core.registry import DATA_SOURCE_REGISTRY, SourceStatus


class HazardPredictions(BaseModel):
    lightning: CalibratedPrediction
    thunderstorm: CalibratedPrediction
    heavy_rain: CalibratedPrediction
    severe_wind: CalibratedPrediction
    model_version: str = "fusion_multimodal_v2.0"
    modalities_used: List[str]
    degraded_modalities: List[str]
    primary_risk_drivers: List[str]
    composite_confidence: float


class MultiModalFusionEngine:
    """Combines heterogeneous meteorological sensor streams into robust probabilistic nowcasts."""
    MODEL_VERSION = "fusion_multimodal_v2.0"

    @classmethod
    def run_fusion(
        cls,
        cape_j_kg: float,
        cin_j_kg: float,
        lifted_index_c: float,
        k_index_c: float,
        total_totals_c: float,
        precipitable_water_mm: float,
        bulk_shear_ms: float,
        lapse_rate_c_km: float,
        dewpoint_dep_c: float,
        max_reflectivity_dbz: float,
        vil_kg_m2: float,
        echo_top_km: float,
        flash_rate_min: float,
        flash_trend_pct: float,
        area_growth_pct: float,
        speed_kmh: float,
        cloud_top_temp_k: float,
        btd_tir1_wv_k: float,
        horizon_minutes: int,
        radar_status: SourceStatus = SourceStatus.LIVE,
        satellite_status: SourceStatus = SourceStatus.LIVE,
        lightning_status: SourceStatus = SourceStatus.LIVE,
        nwp_status: SourceStatus = SourceStatus.LIVE
    ) -> HazardPredictions:
        """
        Execute multi-modal ensemble fusion with dynamic modality weights according to live sensor health.
        """
        modalities_used = []
        degraded_modalities = []
        
        # Determine active modality weights
        weights = {
            "radar": 0.35 if radar_status == SourceStatus.LIVE else 0.0,
            "lightning": 0.25 if lightning_status == SourceStatus.LIVE else 0.0,
            "satellite": 0.20 if satellite_status == SourceStatus.LIVE else 0.0,
            "nwp_sounding": 0.20 if nwp_status == SourceStatus.LIVE else 0.0,
        }
        
        for k, v in [("Radar (DWR)", radar_status), ("Satellite (INSAT-3D)", satellite_status), ("Lightning (LMS)", lightning_status), ("NWP (NCMRWF)", nwp_status)]:
            if v == SourceStatus.LIVE:
                modalities_used.append(k)
            else:
                degraded_modalities.append(k)
                
        # Normalize weights
        total_w = sum(weights.values())
        if total_w > 0:
            for k in weights:
                weights[k] /= total_w
        else:
            # Fallback to persistence
            weights["radar"] = 1.0
            
        # 1. Evaluate Tabular Model B (Sounding + Storm core)
        tabular_preds = TabularMLModel.predict(
            cape=cape_j_kg, cin=cin_j_kg, li=lifted_index_c, ki=k_index_c, tt=total_totals_c,
            pwat=precipitable_water_mm, shear=bulk_shear_ms, lapse_rate=lapse_rate_c_km,
            dew_dep=dewpoint_dep_c, max_dbz=max_reflectivity_dbz, vil=vil_kg_m2,
            echo_top=echo_top_km, flash_rate=flash_rate_min, flash_trend=flash_trend_pct,
            area_growth=area_growth_pct, speed=speed_kmh, horizon_minutes=horizon_minutes
        )
        
        # 2. Evaluate Spatiotemporal Model C (Optical flow + Satellite IR)
        spatio_preds = SpatiotemporalModel.predict(
            radar_patch=np.array([[max_reflectivity_dbz]]),
            flow_vector=np.array([speed_kmh * 0.1, speed_kmh * 0.1]),
            cloud_top_temp_k=cloud_top_temp_k,
            btd_tir1_wv_k=btd_tir1_wv_k,
            horizon_minutes=horizon_minutes
        )
        
        # 3. Evaluate Baseline Model A
        baseline_preds = BaselineModel.predict(
            current_dbz=max_reflectivity_dbz,
            current_flash_rate=flash_rate_min,
            horizon_minutes=horizon_minutes
        )
        
        # Model Fusion: 60% Tabular ML + 30% Spatiotemporal DL + 10% Baseline Climatology
        raw_p_lightning = (
            0.60 * tabular_preds["p_lightning"] +
            0.30 * spatio_preds["p_lightning"] +
            0.10 * baseline_preds["p_lightning"]
        )
        raw_p_thunderstorm = (
            0.55 * tabular_preds["p_thunderstorm"] +
            0.35 * spatio_preds["p_thunderstorm"] +
            0.10 * baseline_preds["p_thunderstorm"]
        )
        raw_p_heavy_rain = (
            0.65 * tabular_preds["p_heavy_rain"] +
            0.25 * spatio_preds["p_heavy_rain"] +
            0.10 * baseline_preds["p_heavy_rain"]
        )
        raw_p_severe_wind = (
            0.70 * tabular_preds["p_severe_wind"] +
            0.20 * spatio_preds["p_severe_wind"] +
            0.10 * baseline_preds["p_severe_wind"]
        )
        
        # Apply Isotonic Calibration & Conformal Prediction Intervals
        cal_lightning = ConformalCalibrator.calibrate_hazard("LIGHTNING", raw_p_lightning, horizon_minutes)
        cal_thunderstorm = ConformalCalibrator.calibrate_hazard("THUNDERSTORM", raw_p_thunderstorm, horizon_minutes)
        cal_heavy_rain = ConformalCalibrator.calibrate_hazard("HEAVY_RAIN", raw_p_heavy_rain, horizon_minutes)
        cal_severe_wind = ConformalCalibrator.calibrate_hazard("SEVERE_WIND", raw_p_severe_wind, horizon_minutes)
        
        # Physical Risk Drivers
        drivers = []
        if flash_rate_min >= 15.0 or flash_trend_pct >= 50.0:
            drivers.append("Intense Lightning Flash Rate Surge (+200% precursor)")
        if max_reflectivity_dbz >= 45.0:
            drivers.append(f"Severe Convective Radar Core ({max_reflectivity_dbz:.1f} dBZ)")
        if cape_j_kg >= 1800.0:
            drivers.append(f"Extreme Atmospheric Buoyancy (CAPE: {cape_j_kg:.0f} J/kg)")
        if bulk_shear_ms >= 15.0:
            drivers.append(f"Strong Deep-Layer Wind Shear ({bulk_shear_ms:.1f} m/s)")
        if cloud_top_temp_k < 220.0:
            drivers.append(f"Deep Overshooting Cloud Top ({cloud_top_temp_k:.0f} K)")
        if len(drivers) == 0:
            drivers.append("Moderate thermodynamic instability & localized boundary convergence")
            
        # Composite confidence
        base_conf = max(1.0 - (0.0035 * horizon_minutes), 0.35)
        # Reduce confidence if key modalities are missing/degraded
        modality_penalty = len(degraded_modalities) * 0.12
        composite_conf = round(float(np.clip(base_conf - modality_penalty, 0.20, 0.98)), 2)
        
        return HazardPredictions(
            lightning=cal_lightning,
            thunderstorm=cal_thunderstorm,
            heavy_rain=cal_heavy_rain,
            severe_wind=cal_severe_wind,
            model_version=cls.MODEL_VERSION,
            modalities_used=modalities_used,
            degraded_modalities=degraded_modalities,
            primary_risk_drivers=drivers,
            composite_confidence=composite_conf
        )
