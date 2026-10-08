# VIDYUTRAKSHA — System Architecture Specification

## 1. High-Level Modular Design

VIDYUTRAKSHA is structured into discrete, decoupled, testable subsystems:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          1. DATA INGESTION                             │
│  IMD Doppler Radar | INSAT-3D | IITM Lightning | NCMRWF NWP | AWS Tele │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    2. QUALITY CONTROL & VALIDATION                     │
│    Range Sanity | Spatial Check | Timestamp Check | QC Flagging       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                 3. SPATIAL & TEMPORAL HARMONIZATION                    │
│   Common Analysis Grid (0.05°) | Temporal Windowing | Metadata Tracking│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                  4. ATMOSPHERIC & RADAR FEATURE ENGINE                 │
│   CAPE / CIN | VIL & Echo Tops | 2-Sigma Lightning Jump Algorithm     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                  5. STORM CELL IDENTIFICATION & TRACK                  │
│   Modified TITAN/SCIT | Hungarian Association | Kinematics & Lifecycle│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                   6. MULTI-MODAL ML & NOWCASTING                       │
│   Model A (Persist) | Model B (Tabular) | Model C (Spatio) | Model D   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│              7. CONFORMAL UNCERTAINTY & CALIBRATION                    │
│   P10 / P50 / P90 Quantiles | Conformal Bounds | Isotonic Scaling     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│               8. RISK ENGINE & CAP EMERGENCY ALERTING                  │
│   0-100 Risk Index | CAP v1.2 Alerts | Transit Corridor Hazard Exposure│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│               9. CONTINUOUS VERIFICATION & MODEL HEALTH                │
│   CSI / POD / FAR / Brier | PSI Feature Drift | Model Battle Arena    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                   10. FASTAPI BACKEND & COMMAND CENTRE                 │
│   REST API v1 | React Tactical MapLibre / Leaflet | Digital Storm Twin │
└────────────────────────────────────────────────────────────────────────┘
```

## 2. Technical Component Rationale

1. **Python-First Scientific Core:** Built on FastAPI, NumPy, SciPy, Pandas, OpenCV, and Shapely for sub-millisecond vector math and geometric contour extraction.
2. **Asynchronous Architecture:** Non-blocking async endpoints prevent thread starvation during concurrent radar raster computations and multi-horizon projections.
3. **Normalized Indexed Relational & Spatial Storage:** PostgreSQL/PostGIS / SQLite schemas indexed on `(latitude, longitude, timestamp)` prevent table scans during dashboard queries.
4. **Offline-First Seed & Historical Replay Engine:** Allows reliable live demonstration to SIH judges without dependency on live external radar network uptime.
