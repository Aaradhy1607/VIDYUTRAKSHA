# VIDYUTRAKSHA — Operational Limitations & Meteorological Edge Cases

## 1. Physical Sensor Constraints

### Radar Beam Blockage in Complex Orography
- **Issue:** Doppler Weather Radars (DWR) situated in sub-Himalayan valleys (e.g. Jammu, Srinagar, Dehradun) experience partial ground clutter and terrain blockage at lower elevation angles ($0.5^\circ - 1.5^\circ$).
- **Mitigation:** The system detects beam blockage masks and shifts feature weights to INSAT-3D rapid-scan Infrared Brightness Temperatures (BTD: $T_{10.8\mu m} - T_{6.7\mu m}$) and NCMRWF mesoscale thermodynamic lapse rate fields.

### Satellite Brightness Temperature Latency
- **Issue:** Cloud-top cooling observed via INSAT-3D thermal infrared typically lags initial boundary layer convective updrafts by 10–15 minutes before an anvil cloud expands.
- **Mitigation:** Surface AWS boundary-layer convergence lines and high-frequency IITM Lightning LMS intracloud (IC) flashes provide the earliest physical indicators before satellite signatures manifest.

---

## 2. Lead-Time Skill Decay Beyond 60 Minutes

- **Issue:** Pure optical-flow extrapolation assumes Lagrangian persistence of storm intensity. In reality, deep convective cells have a natural physical lifecycle ($\sim 45-60\text{ min}$ for single cells, $\sim 2-4\text{ hours}$ for multicell squall lines), undergoing rapid dissipation or secondary initiation along cold pool gust fronts.
- **Mitigation:**
  - Skill is transparently exposed to users (CSI decays from $0.796$ at +15m to $0.435$ at +120m).
  - Multi-modal fusion transitions from radar extrapolation dominance to NWP mesoscale thermodynamic dominance as lead time extends beyond 60 minutes.
