"""
VIDYUTRAKSHA - Radar Volumetric & Reflectivity Feature Engine
Computes Vertically Integrated Liquid (VIL), Echo Tops, Core Roughness, and Severe Convection Proxies.
"""
import numpy as np
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class RadarFeatures(BaseModel):
    max_reflectivity_dbz: float
    mean_reflectivity_dbz: float
    vil_kg_m2: float
    vil_density_g_m3: float
    echo_top_18dbz_km: float
    echo_top_45dbz_km: float
    core_area_fraction_gt40dbz: float
    texture_gradient_rms: float
    severe_hail_risk: str  # LOW, MODERATE, HIGH, EXTREME


class RadarFeatureEngine:
    """Extract meteorological features from 2D/3D Doppler Weather Radar fields."""

    @staticmethod
    def calculate_vil(reflectivity_profile_dbz: List[float], layer_heights_km: List[float]) -> float:
        """
        Calculate Vertically Integrated Liquid (VIL, kg/m²).
        VIL = 3.44e-6 * sum( (10^(0.1 * Z_mean))^(4/7) * delta_h_m )
        VIL > 40 kg/m² is a classic severe storm / hail threshold.
        """
        if len(reflectivity_profile_dbz) < 2 or len(layer_heights_km) < 2:
            # Single level fallback using equivalent convective column depth ~8km
            z_linear = 10.0 ** (0.1 * max(reflectivity_profile_dbz[0] if reflectivity_profile_dbz else 0, 0))
            return float(3.44e-6 * (z_linear ** (4.0 / 7.0)) * 8000.0)
            
        vil = 0.0
        for i in range(len(reflectivity_profile_dbz) - 1):
            dbz1 = reflectivity_profile_dbz[i]
            dbz2 = reflectivity_profile_dbz[i+1]
            h1_m = layer_heights_km[i] * 1000.0
            h2_m = layer_heights_km[i+1] * 1000.0
            dh = abs(h2_m - h1_m)
            
            # Linear reflectivity Z = 10^(0.1 * dBZ)
            z1 = 10.0 ** (0.1 * max(dbz1, 0.0))
            z2 = 10.0 ** (0.1 * max(dbz2, 0.0))
            z_avg = (z1 + z2) / 2.0
            
            vil += 3.44e-6 * (z_avg ** (4.0 / 7.0)) * dh
            
        return float(np.clip(vil, 0.0, 120.0))

    @staticmethod
    def calculate_vil_density(vil_kg_m2: float, echo_top_km: float) -> float:
        """
        VIL Density = (VIL / Echo Top) in g/m³.
        VIL Density > 3.5 g/m³ strongly correlates with severe hail.
        """
        if echo_top_km <= 0.5:
            return 0.0
        return float((vil_kg_m2 / (echo_top_km * 1000.0)) * 1000.0)  # g/m³

    @classmethod
    def extract_patch_features(
        cls,
        radar_grid: np.ndarray,
        echo_top_km: float = 12.0,
        elevations_dbz: Optional[List[float]] = None
    ) -> RadarFeatures:
        """Extract spatial texture, VIL, and severe indicators from a radar bounding patch."""
        if radar_grid.size == 0 or np.all(np.isnan(radar_grid)):
            return RadarFeatures(
                max_reflectivity_dbz=0.0,
                mean_reflectivity_dbz=0.0,
                vil_kg_m2=0.0,
                vil_density_g_m3=0.0,
                echo_top_18dbz_km=0.0,
                echo_top_45dbz_km=0.0,
                core_area_fraction_gt40dbz=0.0,
                texture_gradient_rms=0.0,
                severe_hail_risk="LOW"
            )
            
        valid_data = radar_grid[~np.isnan(radar_grid)]
        if valid_data.size == 0:
            valid_data = np.array([0.0])
            
        max_dbz = float(np.max(valid_data))
        mean_dbz = float(np.mean(valid_data))
        
        # Convective core area fraction
        core_pixels = np.sum(valid_data >= 40.0)
        core_fraction = float(core_pixels / valid_data.size)
        
        # Spatial texture gradient (Sobel-like RMS gradient)
        if radar_grid.ndim == 2 and radar_grid.shape[0] > 2 and radar_grid.shape[1] > 2:
            gy, gx = np.gradient(np.nan_to_num(radar_grid, nan=0.0))
            grad_rms = float(np.sqrt(np.mean(gx**2 + gy**2)))
        else:
            grad_rms = 0.0
            
        # VIL estimation
        if elevations_dbz is None:
            elevations_dbz = [max_dbz, max_dbz * 0.85, max_dbz * 0.6, max_dbz * 0.3]
        layer_heights = [1.5, 4.0, 8.0, 14.0]
        vil = cls.calculate_vil(elevations_dbz, layer_heights)
        vil_density = cls.calculate_vil_density(vil, echo_top_km)
        
        # Echo tops approximation
        echo_18 = echo_top_km
        echo_45 = echo_top_km * 0.7 if max_dbz >= 45.0 else 0.0
        
        # Hail risk determination
        if max_dbz >= 55.0 and vil_density >= 3.5:
            hail_risk = "EXTREME"
        elif max_dbz >= 48.0 and vil_density >= 2.5:
            hail_risk = "HIGH"
        elif max_dbz >= 40.0:
            hail_risk = "MODERATE"
        else:
            hail_risk = "LOW"
            
        return RadarFeatures(
            max_reflectivity_dbz=round(max_dbz, 1),
            mean_reflectivity_dbz=round(mean_dbz, 1),
            vil_kg_m2=round(vil, 1),
            vil_density_g_m3=round(vil_density, 2),
            echo_top_18dbz_km=round(echo_18, 1),
            echo_top_45dbz_km=round(echo_45, 1),
            core_area_fraction_gt40dbz=round(core_fraction, 3),
            texture_gradient_rms=round(grad_rms, 2),
            severe_hail_risk=hail_risk
        )
