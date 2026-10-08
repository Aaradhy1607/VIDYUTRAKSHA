export type SourceStatus = 'LIVE' | 'DEGRADED' | 'HISTORICAL' | 'UNAVAILABLE';
export type AlertTier = 'GREEN' | 'YELLOW' | 'ORANGE' | 'RED';
export type LifecycleState = 'INITIATING' | 'GROWING' | 'MATURE' | 'DECAYING' | 'DISSIPATING';

export interface DataSourceMetadata {
  source_id: string;
  name: string;
  provider: string;
  variables: string[];
  spatial_coverage: string;
  spatial_resolution: string;
  temporal_resolution: string;
  latency_minutes: number;
  historical_availability: string;
  real_time_availability: boolean;
  access_method: string;
  licensing: string;
  data_format: string;
  reliability_score: number;
  status: SourceStatus;
  last_successful_ingestion?: string;
  records_ingested_last_24h: number;
  qc_pass_rate: number;
  fallback_strategy: string;
  operational_notes: string;
}

export interface DetectedStormCell {
  storm_id: string;
  timestamp: string;
  centroid_lat: number;
  centroid_lon: number;
  area_km2: number;
  perimeter_km: number;
  max_reflectivity_dbz: number;
  mean_reflectivity_dbz: number;
  vil_kg_m2: number;
  echo_top_km: number;
  eccentricity: number;
  orientation_deg: number;
  speed_kmh: number;
  direction_deg: number;
  flash_rate_min: number;
  flash_count_10min: number;
  flash_rate_jump: boolean;
  severity_tier: string;
  lifecycle_state: LifecycleState;
  geometry_geojson: {
    type: string;
    coordinates: number[][][];
  };
  bounding_box: number[];
  nearest_district: string;
  nearest_city: string;
}

export interface CalibratedPrediction {
  hazard_type: string;
  raw_probability: number;
  calibrated_probability: number;
  p10: number;
  p50: number;
  p90: number;
  conformal_lower: number;
  conformal_upper: number;
  uncertainty_width: number;
  calibration_method: string;
}

export interface HazardPredictions {
  lightning: CalibratedPrediction;
  thunderstorm: CalibratedPrediction;
  heavy_rain: CalibratedPrediction;
  severe_wind: CalibratedPrediction;
  model_version: string;
  modalities_used: string[];
  degraded_modalities: string[];
  primary_risk_drivers: string[];
  composite_confidence: number;
}

export interface RiskAssessment {
  risk_score: number;
  alert_level: AlertTier;
  lightning_factor: number;
  storm_intensity_factor: number;
  population_exposure_tier: string;
  population_exposure_weight: number;
  lead_time_urgency_factor: number;
  confidence_weight: number;
  contributing_breakdown: Record<string, any>;
}

export interface CAPAlert {
  identifier: string;
  sender: string;
  sent: string;
  status: string;
  msgType: string;
  scope: string;
  event: string;
  urgency: string;
  severity: string;
  certainty: string;
  headline: string;
  description: string;
  instruction: string;
  areaDesc: string;
  risk_score: number;
  alert_tier: AlertTier;
  polygon_geojson?: any;
  affected_population: number;
  expires: string;
}

export interface ModelBattleResult {
  model_name: string;
  model_version: string;
  model_type: string;
  csi_15min: number;
  csi_30min: number;
  csi_60min: number;
  csi_120min: number;
  overall_pod: number;
  overall_far: number;
  overall_f1: number;
  overall_brier: number;
  inference_latency_ms: number;
  memory_footprint_mb: number;
  operational_rank: number;
}

export interface HorizonSkillPoint {
  horizon_minutes: number;
  pod: number;
  far: number;
  csi: number;
  ets: number;
  brier_score: number;
  displacement_error_km: number;
}

export interface StreamHealth {
  source_id: string;
  name: string;
  status: SourceStatus;
  latency_minutes: number;
  qc_pass_rate_pct: number;
  records_last_24h: number;
  health_score: number;
}

export interface ModelHealthReport {
  model_version: string;
  overall_health_score: number;
  health_status: 'HEALTHY' | 'DEGRADED' | 'CRITICAL';
  availability_pct: number;
  p95_latency_ms: number;
  feature_missingness_pct: number;
  bounds_violation_rate_pct: number;
  current_csi_skill: number;
  drift_status: string;
  streams_health: StreamHealth[];
  last_evaluated: string;
}

export interface FeatureDriftReport {
  feature_name: string;
  psi_value: number;
  psi_status: string;
  ks_statistic: number;
  ks_p_value: number;
  drift_detected: boolean;
  reference_mean: number;
  current_mean: number;
  recommendation: string;
}

export interface ReplayFrame {
  frame_index: number;
  timestamp: string;
  time_label: string;
  storm_state: any;
  lightning_count: number;
  lightning_strikes: Array<{
    lat: number;
    lon: number;
    polarity: string;
    ka: number;
  }>;
  forecast_footprints: Array<{
    horizon: number;
    lat: number;
    lon: number;
    p_lightning: number;
    p_storm: number;
    risk: number;
  }>;
}

export interface HistoricalEvent {
  event_id: string;
  title: string;
  location: string;
  date: string;
  summary: string;
  synoptic_forcing: string;
  peak_dbz: number;
  peak_flash_rate_min: number;
  peak_wind_gust_kmh: number;
  max_risk_score: number;
  alert_tier: AlertTier;
  evaluation_metrics: {
    csi_15min: number;
    csi_30min: number;
    csi_60min: number;
    pod: number;
    far: number;
    lead_time_warning_min: number;
  };
  frames: ReplayFrame[];
}

export interface CorridorSafetyReport {
  corridor_name: string;
  origin: string;
  destination: string;
  total_distance_km: number;
  overall_hazard_exposure: 'LOW' | 'ELEVATED' | 'HIGH' | 'SEVERE';
  max_risk_score: number;
  highest_risk_section: string;
  lightning_strike_probability: number;
  estimated_transit_delay_minutes: number;
  safe_travel_advisory: string;
  waypoints_analysis: Array<{
    waypoint_index: number;
    lat: number;
    lon: number;
    name: string;
    p_lightning: number;
    p_heavy_rain: number;
    p_severe_wind: number;
    risk_score: number;
    alert_tier: string;
    impact_window_minutes: string;
  }>;
}
