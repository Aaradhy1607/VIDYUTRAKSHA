"""
VIDYUTRAKSHA - Database Models & Entities
Normalized schemas with spatial, temporal, and quality indexes.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Boolean, JSON, Index, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from backend.app.db.database import Base


class ObservationRecord(Base):
    """Generic Observation Record with Quality Flagging."""
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    observation_id = Column(String(64), unique=True, index=True, nullable=False)
    source = Column(String(32), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    latitude = Column(Float, index=True, nullable=False)
    longitude = Column(Float, index=True, nullable=False)
    variable = Column(String(64), index=True, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(32), nullable=True)
    quality_flag = Column(String(16), default="GOOD", index=True, nullable=False)  # GOOD, SUSPECT, MISSING, STALE, INVALID
    qc_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_obs_source_var_time", "source", "variable", "timestamp"),
        Index("idx_obs_lat_lon_time", "latitude", "longitude", "timestamp"),
    )


class RadarObservation(Base):
    """IMD Doppler Weather Radar observations."""
    __tablename__ = "radar_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    radar_id = Column(String(32), index=True, nullable=False)
    station_name = Column(String(64), nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    max_reflectivity_dbz = Column(Float, nullable=False)
    mean_reflectivity_dbz = Column(Float, nullable=True)
    radial_velocity_ms = Column(Float, nullable=True)
    vil_kg_m2 = Column(Float, nullable=True)  # Vertically Integrated Liquid
    echo_top_km = Column(Float, nullable=True)
    grid_data_ref = Column(String(256), nullable=True)  # Link to array/raster storage
    quality_flag = Column(String(16), default="GOOD", nullable=False)

    __table_args__ = (
        Index("idx_radar_id_time", "radar_id", "timestamp"),
    )


class SatelliteObservation(Base):
    """INSAT-3D / 3DR Satellite Observations."""
    __tablename__ = "satellite_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    satellite = Column(String(32), index=True, nullable=False)  # INSAT-3D / INSAT-3DR
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    channel = Column(String(32), nullable=False)  # TIR1, TIR2, WV, VIS
    min_cloud_top_temp_k = Column(Float, nullable=True)
    mean_cloud_top_temp_k = Column(Float, nullable=True)
    btd_tir1_wv_k = Column(Float, nullable=True)  # Brightness Temp Difference (Deep convection indicator)
    cloud_top_height_km = Column(Float, nullable=True)
    raster_ref = Column(String(256), nullable=True)
    quality_flag = Column(String(16), default="GOOD", nullable=False)


class LightningEvent(Base):
    """Lightning Location System event records."""
    __tablename__ = "lightning_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    latitude = Column(Float, index=True, nullable=False)
    longitude = Column(Float, index=True, nullable=False)
    type = Column(String(8), default="CG")  # CG (Cloud to Ground), IC (Intracloud)
    polarity = Column(String(2), default="-")  # +, -
    peak_current_ka = Column(Float, nullable=True)
    multiplicity = Column(Integer, default=1)
    quality_flag = Column(String(16), default="GOOD", nullable=False)

    __table_args__ = (
        Index("idx_lightning_time_loc", "timestamp", "latitude", "longitude"),
    )


class WeatherObservation(Base):
    """Surface station meteorological observations."""
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(32), index=True, nullable=False)
    station_name = Column(String(64), nullable=False)
    state = Column(String(64), index=True, nullable=False)
    district = Column(String(64), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=True)
    dew_point_c = Column(Float, nullable=True)
    relative_humidity_pct = Column(Float, nullable=True)
    pressure_hpa = Column(Float, nullable=True)
    wind_speed_ms = Column(Float, nullable=True)
    wind_gust_ms = Column(Float, nullable=True)
    wind_direction_deg = Column(Float, nullable=True)
    rainfall_10min_mm = Column(Float, nullable=True)
    rainfall_accum_1h_mm = Column(Float, nullable=True)
    quality_flag = Column(String(16), default="GOOD", nullable=False)

    __table_args__ = (
        Index("idx_station_time", "station_id", "timestamp"),
    )


class StormCell(Base):
    """Detected Storm Cell Object (Digital Storm Twin)."""
    __tablename__ = "storm_cells"

    id = Column(Integer, primary_key=True, autoincrement=True)
    storm_id = Column(String(64), index=True, nullable=False)  # e.g., "IN-DEL-20260929-001"
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    centroid_lat = Column(Float, nullable=False)
    centroid_lon = Column(Float, nullable=False)
    area_km2 = Column(Float, nullable=False)
    max_reflectivity_dbz = Column(Float, nullable=False)
    mean_reflectivity_dbz = Column(Float, nullable=True)
    vil_kg_m2 = Column(Float, nullable=True)
    echo_top_km = Column(Float, nullable=True)
    speed_kmh = Column(Float, default=0.0)
    direction_deg = Column(Float, default=0.0)
    motion_vector_u = Column(Float, default=0.0)
    motion_vector_v = Column(Float, default=0.0)
    growth_rate_area_pct = Column(Float, default=0.0)  # Area growth rate per 10 min
    growth_rate_dbz = Column(Float, default=0.0)       # Intensity change per 10 min
    flash_rate_min = Column(Float, default=0.0)        # Lightning flash rate
    flash_rate_jump = Column(Boolean, default=False)   # True if sudden 200%+ jump
    lifetime_minutes = Column(Integer, default=10)
    lifecycle_state = Column(String(32), default="INITIATING", index=True)  # INITIATING, GROWING, MATURE, DECAYING, DISSIPATING, MERGED, SPLIT
    severity_tier = Column(String(16), default="ELEVATED")  # MODERATE, ELEVATED, SEVERE, EXTREME
    geometry_geojson = Column(JSON, nullable=False)    # Polygon coordinates
    nearest_district = Column(String(64), nullable=True)
    nearest_city = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_storm_id_time", "storm_id", "timestamp"),
        Index("idx_storm_lifecycle", "lifecycle_state", "timestamp"),
    )


class ForecastRun(Base):
    """Forecast Execution & Multi-Horizon Predictions."""
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    forecast_id = Column(String(64), unique=True, index=True, nullable=False)
    initialization_time = Column(DateTime(timezone=True), index=True, nullable=False)
    target_time = Column(DateTime(timezone=True), index=True, nullable=False)
    horizon_minutes = Column(Integer, index=True, nullable=False)  # 15, 30, 60, 120, 180
    model_version = Column(String(32), index=True, nullable=False)  # e.g., "fusion_v1.2", "lgbm_v1.0"
    hazard_type = Column(String(32), index=True, nullable=False)   # LIGHTNING, THUNDERSTORM, HEAVY_RAIN, SEVERE_WIND
    
    # Probabilistic outputs & uncertainty bounds
    probability = Column(Float, nullable=False)       # Calibrated Median Probability (P50)
    p10 = Column(Float, nullable=True)                # 10th percentile lower bound
    p50 = Column(Float, nullable=True)                # 50th percentile median
    p90 = Column(Float, nullable=True)                # 90th percentile upper bound
    conformal_lower = Column(Float, nullable=True)    # Conformal prediction interval lower
    conformal_upper = Column(Float, nullable=True)    # Conformal prediction interval upper
    uncertainty_width = Column(Float, nullable=True)  # p90 - p10 or conformal width
    confidence_score = Column(Float, default=0.85)    # 0 to 1 confidence
    
    # Spatial footprint
    target_region_geojson = Column(JSON, nullable=True)
    affected_districts = Column(JSON, nullable=True)  # List of impacted district names
    affected_population = Column(Integer, nullable=True)
    risk_score = Column(Float, default=0.0)           # 0 to 100
    alert_level = Column(String(16), default="GREEN") # GREEN, YELLOW, ORANGE, RED
    risk_drivers = Column(JSON, nullable=True)        # Feature attributions (SHAP values & physical reasons)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_forecast_init_horizon", "initialization_time", "horizon_minutes", "hazard_type"),
    )


class VerificationResult(Base):
    """Operational Verification & Skill Metrics."""
    __tablename__ = "verification_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    verification_id = Column(String(64), unique=True, index=True, nullable=False)
    model_version = Column(String(32), index=True, nullable=False)
    hazard_type = Column(String(32), index=True, nullable=False)
    horizon_minutes = Column(Integer, index=True, nullable=False)
    evaluation_start = Column(DateTime(timezone=True), nullable=False)
    evaluation_end = Column(DateTime(timezone=True), nullable=False)
    
    sample_count = Column(Integer, nullable=False)
    hits = Column(Integer, nullable=False)
    misses = Column(Integer, nullable=False)
    false_alarms = Column(Integer, nullable=False)
    correct_negatives = Column(Integer, nullable=False)
    
    # Deterministic / Contingency Metrics
    pod = Column(Float, nullable=False)  # Probability of Detection (Recall / Hit Rate)
    far = Column(Float, nullable=False)  # False Alarm Ratio
    csi = Column(Float, nullable=False)  # Critical Success Index (Threat Score)
    ets = Column(Float, nullable=False)  # Equitable Threat Score (Gilbert Skill Score)
    f1 = Column(Float, nullable=False)   # F1 Score
    hss = Column(Float, nullable=False)  # Heidke Skill Score
    
    # Probabilistic Metrics
    brier_score = Column(Float, nullable=False)
    brier_skill_score = Column(Float, nullable=False)
    crps = Column(Float, nullable=True)  # Continuous Ranked Probability Score
    calibration_error_ece = Column(Float, nullable=True)
    
    # Spatial & Kinematic Errors
    mean_displacement_km = Column(Float, nullable=True)
    track_direction_error_deg = Column(Float, nullable=True)
    footprint_iou = Column(Float, nullable=True)  # Intersection over Union
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ModelHealthLog(Base):
    """Real-time Model Health & Diagnostics."""
    __tablename__ = "model_health_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_version = Column(String(32), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    health_status = Column(String(16), default="HEALTHY")  # HEALTHY, DEGRADED, CRITICAL
    availability_pct = Column(Float, nullable=False)
    p95_latency_ms = Column(Float, nullable=False)
    missing_features_pct = Column(Float, default=0.0)
    bounds_violation_rate = Column(Float, default=0.0)
    current_csi = Column(Float, nullable=False)
    drift_status = Column(String(16), default="NORMAL")  # NORMAL, WARNING, DRIFT_DETECTED
    overall_health_score = Column(Float, nullable=False)  # 0 to 100
    diagnostic_details = Column(JSON, nullable=True)


class DriftEvent(Base):
    """Model & Feature Drift Events."""
    __tablename__ = "drift_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feature_name = Column(String(64), index=True, nullable=False)
    model_version = Column(String(32), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    detection_method = Column(String(32), nullable=False)  # PSI, KS_TEST, JS_DIVERGENCE
    test_statistic = Column(Float, nullable=False)
    p_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=False)
    severity = Column(String(16), nullable=False)  # LOW, MEDIUM, CRITICAL
    description = Column(Text, nullable=False)
