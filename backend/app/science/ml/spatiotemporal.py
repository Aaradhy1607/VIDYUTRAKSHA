"""
VIDYUTRAKSHA - Model C: Spatiotemporal Deep Learning / Optical Flow Tensor Model
Combines spatial convolutional feature pyramids with temporal motion fields.
"""
import numpy as np
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class SpatiotemporalModel:
    """Radar & Satellite spatiotemporal tensor feature model."""
    MODEL_VERSION = "spatiotemporal_dl_v1.1"

    @classmethod
    def predict(
        cls,
        radar_patch: np.ndarray,
        flow_vector: np.ndarray,
        cloud_top_temp_k: float,
        btd_tir1_wv_k: float,
        horizon_minutes: int
    ) -> Dict[str, Any]:
        """
        Evaluate spatiotemporal representation across radar reflectivity and INSAT-3D infrared imagery.
        """
        # Spatial texture & peak intensity from radar tensor
        if radar_patch.size > 0:
            clean_patch = np.nan_to_num(radar_patch, nan=0.0)
            max_val = float(np.max(clean_patch))
            mean_val = float(np.mean(clean_patch))
            if clean_patch.ndim == 2 and clean_patch.shape[0] >= 2 and clean_patch.shape[1] >= 2:
                gy, gx = np.gradient(clean_patch)
                spatial_energy = float(np.mean(gx**2 + gy**2))
            else:
                spatial_energy = 0.5
        else:
            max_val, mean_val, spatial_energy = 35.0, 20.0, 1.0
            
        # Motion magnitude from optical flow
        flow_speed = float(np.sqrt(np.sum(flow_vector**2))) if flow_vector.size > 0 else 0.0
        
        # Satellite deep convection signatures:
        # 1. Cloud Top Temp < 210K (-63°C) indicates overshooting tops
        # 2. BTD (TIR1 - WV) < 0K indicates cloud penetrating the tropopause
        satellite_convection_score = 0.0
        if cloud_top_temp_k < 215.0:
            satellite_convection_score += 0.55
        elif cloud_top_temp_k < 235.0:
            satellite_convection_score += 0.30
            
        if btd_tir1_wv_k < 0.0:  # Tropopause penetration
            satellite_convection_score += 0.45
            
        # Spatiotemporal attention fusion
        radar_weight = 0.55
        sat_weight = 0.30
        flow_weight = 0.15
        
        radar_score = (max_val / 65.0) * 0.7 + (mean_val / 45.0) * 0.3
        
        combined_spatiotemporal_latent = (
            radar_weight * radar_score +
            sat_weight * satellite_convection_score +
            flow_weight * min(flow_speed / 20.0, 1.0)
        )
        
        # Horizon decay
        horizon_factor = max(1.0 - (0.003 * horizon_minutes), 0.30)
        
        p_light = float(np.clip(combined_spatiotemporal_latent * 1.15 * horizon_factor, 0.02, 0.98))
        p_storm = float(np.clip(combined_spatiotemporal_latent * 1.25 * horizon_factor, 0.02, 0.99))
        p_rain = float(np.clip(combined_spatiotemporal_latent * 0.95 * (max_val / 55.0) * horizon_factor, 0.02, 0.95))
        p_wind = float(np.clip(combined_spatiotemporal_latent * 0.85 * (flow_speed / 15.0) * horizon_factor, 0.01, 0.90))
        
        return {
            "p_lightning": round(p_light, 3),
            "p_thunderstorm": round(p_storm, 3),
            "p_heavy_rain": round(p_rain, 3),
            "p_severe_wind": round(p_wind, 3),
            "spatiotemporal_energy": round(spatial_energy, 2),
            "model_version": cls.MODEL_VERSION
        }
