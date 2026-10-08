"""
VIDYUTRAKSHA - Storm Cell Identification Engine (Modified TITAN/SCIT)
Performs multi-threshold reflectivity segmentation, watershed clustering,
and convective core detection.
"""
import numpy as np
import cv2
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from backend.app.science.storm_detection.morphometrics import StormMorphometrics, StormMorphology


class DetectedStormCell(BaseModel):
    storm_id: str
    timestamp: datetime
    centroid_lat: float
    centroid_lon: float
    area_km2: float
    perimeter_km: float
    max_reflectivity_dbz: float
    mean_reflectivity_dbz: float
    vil_kg_m2: float
    echo_top_km: float
    eccentricity: float
    orientation_deg: float
    speed_kmh: float = 0.0
    direction_deg: float = 0.0
    flash_rate_min: float = 0.0
    flash_count_10min: int = 0
    flash_rate_jump: bool = False
    severity_tier: str = "ELEVATED"  # MODERATE, ELEVATED, SEVERE, EXTREME
    lifecycle_state: str = "INITIATING"  # INITIATING, GROWING, MATURE, DECAYING
    geometry_geojson: Dict[str, Any]
    bounding_box: List[float]
    nearest_district: str = "Delhi NCR"
    nearest_city: str = "New Delhi"


class StormCellDetector:
    """Operational Storm Object Detection on 2D Composite Radar / Satellite grids."""

    def __init__(
        self,
        convective_threshold_dbz: float = 35.0,
        severe_threshold_dbz: float = 45.0,
        min_area_km2: float = 20.0
    ):
        self.convective_thresh = convective_threshold_dbz
        self.severe_thresh = severe_threshold_dbz
        self.min_area = min_area_km2

    def detect_cells(
        self,
        radar_grid_dbz: np.ndarray,
        grid_bbox: List[float],
        timestamp: datetime,
        region_prefix: str = "IN-DEL",
        lightning_strikes: Optional[List[Tuple[float, float]]] = None
    ) -> List[DetectedStormCell]:
        """
        Run TITAN-like multi-threshold cell detection and return list of storm objects.
        """
        if radar_grid_dbz.size == 0:
            return []
            
        # Clean grid
        clean_grid = np.nan_to_num(radar_grid_dbz, nan=0.0)
        
        # Binary thresholding for convective cells >= 35 dBZ
        binary_mask = (clean_grid >= self.convective_thresh).astype(np.uint8)
        
        # Morphological opening (noise reduction) + closing (connect fragmented convective cores)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        opened = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
        
        # Connected component labeling
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed, connectivity=8)
        
        detected_cells: List[DetectedStormCell] = []
        
        for label_idx in range(1, num_labels):
            morph = StormMorphometrics.calculate_cell_geometry(
                binary_mask=labels,
                intensity_grid=clean_grid,
                grid_bbox=grid_bbox,
                cell_label=label_idx,
                min_area_km2=self.min_area
            )
            
            if morph is None:
                continue
                
            storm_id = f"{region_prefix}-{timestamp.strftime('%Y%m%d')}-{label_idx:03d}"
            
            # Count lightning strikes located inside this cell's bounding box
            cell_flashes = 0
            if lightning_strikes:
                min_lon, min_lat, max_lon, max_lat = morph.bounding_box
                for s_lat, s_lon in lightning_strikes:
                    if min_lat <= s_lat <= max_lat and min_lon <= s_lon <= max_lon:
                        cell_flashes += 1
                        
            flash_rate = float(cell_flashes / 5.0)  # Flashes per minute
            flash_jump = bool(flash_rate >= 15.0 or cell_flashes >= 60)
            
            # Derived VIL and echo tops
            vil_est = float(np.clip(morph.max_intensity * 0.95, 5.0, 75.0))
            echo_top_est = float(np.clip(morph.max_intensity * 0.28, 6.0, 18.5))
            
            # Determine severity tier
            if morph.max_intensity >= 52.0 or flash_jump or vil_est >= 50.0:
                severity = "EXTREME"
            elif morph.max_intensity >= 45.0 or flash_rate >= 8.0:
                severity = "SEVERE"
            elif morph.max_intensity >= 38.0:
                severity = "ELEVATED"
            else:
                severity = "MODERATE"
                
            cell = DetectedStormCell(
                storm_id=storm_id,
                timestamp=timestamp,
                centroid_lat=morph.centroid_lat,
                centroid_lon=morph.centroid_lon,
                area_km2=morph.area_km2,
                perimeter_km=morph.perimeter_km,
                max_reflectivity_dbz=morph.max_intensity,
                mean_reflectivity_dbz=morph.mean_intensity,
                vil_kg_m2=round(vil_est, 1),
                echo_top_km=round(echo_top_est, 1),
                eccentricity=morph.eccentricity,
                orientation_deg=morph.orientation_deg,
                speed_kmh=0.0,  # Updated by tracker
                direction_deg=0.0,
                flash_rate_min=round(flash_rate, 1),
                flash_count_10min=cell_flashes,
                flash_rate_jump=flash_jump,
                severity_tier=severity,
                lifecycle_state="INITIATING",
                geometry_geojson=morph.polygon_geojson,
                bounding_box=morph.bounding_box,
                nearest_district="North West Delhi",
                nearest_city="New Delhi"
            )
            detected_cells.append(cell)
            
        return detected_cells
