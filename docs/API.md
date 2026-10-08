# VIDYUTRAKSHA — REST API Reference Guide

Base URL: `http://localhost:8000/api/v1`

---

## 1. System & Ingestion Health
- `GET /health`: Overall system operational status, version, and active station counters.
- `GET /data-health`: Authoritative Data Source Registry, stream latencies, QC pass rates, and fallback strategies.

---

## 2. Atmospheric & Convective Physics
- `GET /atmospheric-sounding?lat=28.61&lon=77.20`: Computes CAPE, CIN, Lifted Index, Total Totals, K-Index, 0-6km Bulk Shear, PWAT, and Lapse Rate.
- `GET /storms`: Returns active detected storm cells (convective polygons, centroid, area, intensity, VIL, echo tops, velocity, lifecycle state).
- `GET /storms/{storm_id}`: Full digital storm twin inspector with multi-horizon footprint projections and physical risk drivers.

---

## 3. Multi-Horizon Nowcasting & Hazards
- `GET /nowcast?horizon=15`: Multi-modal nowcast returning 4 hazard heads ($P(\text{Lightning}), P(\text{Thunderstorm}), P(\text{Heavy Rain}), P(\text{Severe Wind})$), Conformal Prediction Intervals ($P_{10}, P_{50}, P_{90}$), and 0-100 Risk Score.
- `GET /alerts`: Active CAP v1.2 emergency alert bulletins for impacted districts.
- `POST /corridor-safety`: Evaluates travel hazard exposure along transportation route coordinates.

---

## 4. Verification & Model Health
- `GET /verification`: Continuous deterministic and probabilistic verification metrics ($POD, FAR, CSI, ETS, \text{Brier Score}$).
- `GET /model-arena`: Comparative Model Battle Arena leaderboard across all 4 operational architectures.
- `GET /model-health`: Model availability, P95 inference latency, and health score.
- `GET /drift`: Population Stability Index (PSI) and Kolmogorov-Smirnov distribution test reports.
- `GET /historical-events`: Catalog of verified historical severe weather scenarios.
- `GET /replay/{event_id}`: Frame-by-frame historical replay package.
- `GET /scientific-audit`: Scientific transparency and physics equations brief.
