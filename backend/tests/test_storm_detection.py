"""
Tests for Storm Cell Identification, Tracking, Verification, Calibration, and QC
"""
import pytest
import numpy as np
from datetime import datetime, timezone

from backend.app.science.storm_detection.detector import StormCellDetector
from backend.app.science.storm_tracking.tracker import StormTracker
from backend.app.science.storm_tracking.lifecycle import StormLifecycleEngine, LifecycleState
from backend.app.science.verification.metrics import VerificationEngine
from backend.app.science.ml.calibration import ConformalCalibrator
from backend.app.data.qc import QualityControlEngine


def test_storm_cell_detection_synthetic_core():
    # 50x50 radar grid with a 50 dBZ convective core
    grid = np.zeros((50, 50))
    grid[20:30, 20:30] = 52.0  # Convective core
    bbox = [76.0, 28.0, 78.0, 30.0]
    now = datetime.now(timezone.utc)
    
    detector = StormCellDetector(convective_threshold_dbz=35.0, min_area_km2=10.0)
    cells = detector.detect_cells(grid, bbox, now, region_prefix="IN-DEL")
    
    assert len(cells) == 1
    cell = cells[0]
    assert cell.max_reflectivity_dbz >= 50.0
    assert cell.area_km2 > 10.0
    assert 28.0 <= cell.centroid_lat <= 30.0
    assert 76.0 <= cell.centroid_lon <= 78.0


def test_hungarian_storm_tracking():
    tracker = StormTracker(max_distance_km=60.0)
    now1 = datetime(2023, 5, 23, 17, 30, tzinfo=timezone.utc)
    now2 = datetime(2023, 5, 23, 17, 45, tzinfo=timezone.utc)
    
    # Step 1: Initial detection
    grid1 = np.zeros((50, 50))
    grid1[20:30, 20:30] = 48.0
    bbox = [76.0, 28.0, 78.0, 30.0]
    detector = StormCellDetector()
    cells1 = detector.detect_cells(grid1, bbox, now1, region_prefix="IN-DEL")
    
    tracked1 = tracker.update_tracks(cells1, now1, dt_minutes=15.0)
    assert len(tracked1) == 1
    first_id = tracked1[0].storm_id
    
    # Step 2: Shifted detection (eastward advection)
    grid2 = np.zeros((50, 50))
    grid2[20:30, 24:34] = 52.0  # Moved right (east)
    cells2 = detector.detect_cells(grid2, bbox, now2, region_prefix="IN-DEL")
    
    tracked2 = tracker.update_tracks(cells2, now2, dt_minutes=15.0)
    assert len(tracked2) == 1
    # Hungarian tracking should maintain identical storm ID
    assert tracked2[0].storm_id == first_id
    assert tracked2[0].speed_kmh > 0.0


def test_verification_metrics_perfect_forecast():
    probs = [0.9, 0.85, 0.8, 0.1, 0.05]
    obs = [1, 1, 1, 0, 0]
    metrics = VerificationEngine.evaluate_skills(probs, obs, threshold=0.5)
    
    assert metrics.pod == 1.0  # Perfect detection
    assert metrics.far == 0.0  # Zero false alarms
    assert metrics.csi == 1.0  # Perfect threat score
    assert metrics.brier_score < 0.05


def test_conformal_uncertainty_quantification():
    raw_prob = 0.85
    cal_pred = ConformalCalibrator.calibrate_hazard("LIGHTNING", raw_prob, horizon_minutes=30)
    
    assert 0.0 <= cal_pred.calibrated_probability <= 1.0
    assert cal_pred.p10 <= cal_pred.p50 <= cal_pred.p90
    assert cal_pred.conformal_lower <= cal_pred.calibrated_probability <= cal_pred.conformal_upper
    assert cal_pred.uncertainty_width > 0.0


def test_quality_control_bounds():
    now = datetime.now(timezone.utc)
    
    # Valid observation
    res_good = QualityControlEngine.check_observation("temperature_c", 35.5, now, 28.6, 77.2)
    assert res_good.is_valid is True
    assert res_good.quality_flag == "GOOD"
    
    # Physical out of bounds
    res_bad = QualityControlEngine.check_observation("temperature_c", 85.0, now, 28.6, 77.2)
    assert res_bad.is_valid is False
    assert res_bad.quality_flag == "INVALID"
    
    # Spatial out of bounds (Equator / Africa)
    res_geo = QualityControlEngine.check_observation("temperature_c", 28.0, now, -5.0, 10.0)
    assert res_geo.is_valid is False
    assert res_geo.quality_flag == "INVALID"
