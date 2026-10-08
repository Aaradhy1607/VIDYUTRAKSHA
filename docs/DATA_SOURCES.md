# VIDYUTRAKSHA — Authoritative Data Source Registry & Ingestion

## 1. Verified Meteorological Data Sources for India

| Source ID | Name | Provider | Key Variables | Spatial Res. | Temporal Res. | Latency | Status | Fallback Mode |
|---|---|---|---|---|---|---|---|---|
| `IMD_DWR_COMPOSITE` | Doppler Weather Radar Network (34 DWRs) | India Meteorological Department (IMD) | Reflectivity (dBZ), Radial Velocity, VIL, Echo Tops | 500m / 0.01° | 10 min | 12 min | **LIVE** | `NWP_SATELLITE_ONLY` |
| `INSAT_3D_3DR_RAPID` | INSAT-3D/3DR Imager & Sounder | ISRO / MOSDAC | TIR1, TIR2, WV Brightness Temp, Cloud Top Temp | 4 km (IR), 1 km (VIS) | 15 min | 25 min | **LIVE** | `PERSISTENCE_EXTRAPOLATION` |
| `IITM_LIGHTNING_LMS` | Damini Lightning Detection Array | Indian Institute of Tropical Meteorology (IITM) | Total Lightning (IC+CG), Flash Rate, Peak Current, Polarity | ~500m loc. | 1 min | 2 min | **LIVE** | `SURFACE_PROXY_CONVECTION` |
| `NCMRWF_IMD_NWP` | NCUM & Regional High-Res GFS | NCMRWF / IMD | CAPE, CIN, Lifted Index, Bulk Shear, PWAT, Lapse Rate | 0.05° (~4 km) | Hourly | 90 min | **LIVE** | `CLIMATOLOGY_PRIOR` |
| `IMD_AWS_SURFACE` | Automatic Weather Stations (AWS/ARG) | IMD | Temp, Dew Point, RH, Pressure, 10-min Rain, Gusts | Point (1,200+ stns) | 15 min | 20 min | **LIVE** | `PERSISTENCE_EXTRAPOLATION` |
| `TOPOGRAPHY_SRTM` | SRTM 30m / CartoDEM Topography | ISRO Bhuvan / NASA JPL | Elevation, Slope, Aspect, Terrain Ruggedness | 30 meters | Static | 0 min | **LIVE** | `CLIMATOLOGY_PRIOR` |

---

## 2. Quality Control & Sanity Protocols

Incoming sensor streams pass through a strict 6-stage Quality Control engine:
1. **Missing / NaN Value Handling:** Flags record as `MISSING` and prevents silent imputation.
2. **Geographic Bounding Validation:** Asserts coordinate is within Indian operational domain $[5.0^\circ\text{N} \le \text{Lat} \le 39.0^\circ\text{N}, 67.0^\circ\text{E} \le \text{Lon} \le 99.0^\circ\text{E}]$.
3. **Temporal Staleness Check:** Rejects future timestamps and flags observations older than 6 hours as `STALE`.
4. **Physical Meteorological Bounds:**
   - Temperature: $[-20^\circ\text{C}, 55^\circ\text{C}]$
   - Reflectivity: $[-10\text{ dBZ}, 80\text{ dBZ}]$
   - Lightning Peak Current: $[2\text{ kA}, 400\text{ kA}]$
   - CAPE: $[0, 7000\text{ J/kg}]$
5. **Rate of Change (Step-Check):** Flags sudden non-physical jumps ($\Delta T > 15^\circ\text{C/hr}$).
6. **Internal Consistency Check:** Asserts $T_{dew} \le T_{dry}$ and positive pressure gradients.
