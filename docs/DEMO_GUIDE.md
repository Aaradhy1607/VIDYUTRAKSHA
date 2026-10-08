# VIDYUTRAKSHA — SIH Live Demonstration Flow Guide

## ⏱️ Recommended 3-Minute Live Presentation Flow

---

### Minute 1: The Problem & Live Operational Command Centre
1. **The Challenge:** Lightning and severe thunderstorms kill over 2,500 people annually in India. Existing warnings are often broad, district-wide synoptic outlooks lacking hyper-local, multi-horizon nowcasting precision.
2. **Open Command Centre:**
   - Show the **Universal Top Bar**: Active live telemetry (`6/6 STREAMS LIVE`, 18ms latency, synchronized UTC/IST clocks).
   - Show the **Left Panel**: Multi-hazard heads ($P(\text{Lightning}): 91\%, P(\text{Thunderstorm}): 94\%, P(\text{Heavy Rain}): 82\%, P(\text{Severe Wind}): 74\%$) with calibrated $P_{10}-P_{90}$ conformal prediction intervals.
   - Show the **Center Interactive Map**: Real-time IMD Doppler Radar reflectivity colormap, live IITM lightning strikes with polarity ($+$ in amber, $-$ in cyan), detected storm cell polygons, and velocity vector arrows.
   - Click on Storm `#IN-DEL-042` to reveal the **Digital Storm Twin** (Right Panel) showing lifecycle, kinematics (44 km/h, 108° ESE), 54.2 dBZ core, 48 kg/m² VIL, $+240\%$ Lightning Jump detection, and transparent SHAP physical risk drivers.

---

### Minute 2: Multi-Horizon Forecasting & Historical Replay Engine
1. **Multi-Horizon Stepper:**
   - Click through the bottom horizon bar: `NOW` → `+15m` → `+30m` → `+60m` → `+120m` → `+180m`.
   - Highlight the **expanding cone of uncertainty** on the map and the honest **expected model skill curve** (CSI: 95% at 15m → 68% at 60m → 32% at 180m).
2. **Historical Replay / Demo Mode:**
   - Switch to the **Historical Replay** tab.
   - Select the **Delhi-NCR May 23, 2023 Nor'wester Supercell** event.
   - Hit **PLAY TIMELINE** and watch frame-by-frame storm intensification, the $+240\%$ lightning jump precursor 18 minutes prior to peak 96 km/h surface wind gusts, and side-by-side ground truth verification.

---

### Minute 3: Scientific Rigor & Model Battle Arena
1. **Model Battle Arena:**
   - Show the comparative leaderboard: Persistence Baseline vs Tabular LightGBM vs Spatiotemporal DL vs Multi-Modal Fusion.
   - Show the CSI vs Lead Time degradation curves.
2. **Transit Corridor Safety & Scientific Audit:**
   - Open **Transit Corridors** to evaluate severe hazard exposure for Delhi Airport → Noida route.
   - Open **Scientific Audit** to show thermodynamic formulations (CAPE, VIL, 2-sigma jump) and operational limitations.
3. **Closing Statement:**
   > *"VIDYUTRAKSHA transforms reactive weather reports into an intelligent, scientifically verified early-warning decision-support system capable of saving lives across India."*
