# VIDYUTRAKSHA — Machine Learning Model Cards

## 1. Model A — Lagged Autoregressive Baseline
- **Model Version:** `baseline_pers_v1.0`
- **Architecture:** Autoregressive Lagrangian Extrapolation with exponential convective decorrelation ($\tau = 45\text{ min}$) towards climatology.
- **Inputs:** Current radar reflectivity, current flash rate, lead time horizon.
- **Intended Use:** Honest scientific benchmark for evaluating incremental skill gains of machine learning architectures.

---

## 2. Model B — Tabular Atmospheric LightGBM
- **Model Version:** `tabular_lgbm_v1.2`
- **Architecture:** Gradient-Boosted Decision Trees (LightGBM) trained on thermodynamic sounding indices and storm cell morphometrics.
- **Features (16):** `cape_j_kg`, `cin_j_kg`, `lifted_index_c`, `k_index_c`, `total_totals_c`, `precipitable_water_mm`, `bulk_shear_0_6km_ms`, `lapse_rate_700_500_c_km`, `dewpoint_depression_sfc_c`, `max_reflectivity_dbz`, `vil_kg_m2`, `echo_top_km`, `flash_rate_min`, `flash_rate_10min_trend_pct`, `growth_rate_area_pct`, `speed_kmh`.
- **Explainability:** SHAP-style direct feature contribution attributions.

---

## 3. Model C — Spatiotemporal Optical Flow DL Tensor Net
- **Model Version:** `spatiotemporal_dl_v1.1`
- **Architecture:** Farneback optical flow motion estimation + 2D Convolutional feature pyramid on radar reflectivity and INSAT-3D infrared channel brightness temperature differences ($\text{BTD} = T_{10.8\mu m} - T_{6.7\mu m}$).
- **Key Capability:** Captures rapid cloud-top cooling and tropopause-overshooting convective cores.

---

## 4. Model D — Multi-Modal Dynamic Convective Fusion Engine (Primary Operational Model)
- **Model Version:** `fusion_multimodal_v2.0`
- **Architecture:** Dynamic weighted ensemble fusing Model B (60%), Model C (30%), and Model A (10%) with sensor health-aware modality weights.
- **Output Heads (4):**
  1. $P(\text{Lightning})$
  2. $P(\text{Thunderstorm})$
  3. $P(\text{Heavy Rain})$
  4. $P(\text{Severe Wind})$
- **Uncertainty Engine:** Isotonic probability scaling + Conformal prediction intervals ($P_{10}, P_{50}, P_{90}$).
- **Inference Latency:** 18.4 ms.
