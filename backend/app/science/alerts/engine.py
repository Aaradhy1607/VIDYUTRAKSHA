"""
VIDYUTRAKSHA - Operational Alert Engine & CAP Protocol Generator
Issues Common Alerting Protocol (CAP) v1.2 compliant JSON alerts for NDMA & State SDMAs.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class CAPAlert(BaseModel):
    identifier: str
    sender: str = "VIDYUTRAKSHA-EARLY-WARNING@IMD-NDMA.GOV.IN"
    sent: str
    status: str = "Actual"  # Actual, Exercise, Test
    msgType: str = "Alert"  # Alert, Update, Cancel
    scope: str = "Public"
    event: str  # Severe Thunderstorm & Lightning Warning
    urgency: str  # Immediate, Expected, Future, Past
    severity: str  # Extreme, Severe, Moderate, Minor
    certainty: str  # Observed, Very Likely, Likely, Possible
    headline: str
    description: str
    instruction: str
    areaDesc: str
    risk_score: float
    alert_tier: str  # GREEN, YELLOW, ORANGE, RED
    polygon_geojson: Optional[Dict[str, Any]] = None
    affected_population: int
    expires: str


class AlertEngine:
    """Generates standardized operational warning bulletins and CAP alerts."""

    @classmethod
    def generate_cap_alert(
        cls,
        storm_id: str,
        district_name: str,
        state_name: str,
        risk_score: float,
        alert_tier: str,
        p_lightning: float,
        p_severe_wind: float,
        p_heavy_rain: float,
        lead_time_min: int,
        affected_pop: int = 450000,
        polygon_geojson: Optional[Dict[str, Any]] = None
    ) -> CAPAlert:
        """Construct standard CAP-compliant meteorological alert payload."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=max(lead_time_min + 30, 60))
        
        # Urgency & Severity mapping
        if alert_tier == "RED":
            severity = "Extreme"
            urgency = "Immediate"
            certainty = "Very Likely" if p_lightning >= 0.8 else "Likely"
            headline = f"RED ALERT: Imminent Severe Thunderstorm & High-Frequency Lightning Threat for {district_name}"
            instructions = (
                "1. Take immediate indoor shelter in substantial buildings.\n"
                "2. Stay away from windows, open electrical equipment, and metal structures.\n"
                "3. Avoid open fields, elevated areas, and isolated trees.\n"
                "4. Suspend outdoor aviation, metro surface corridors, and ground operations."
            )
        elif alert_tier == "ORANGE":
            severity = "Severe"
            urgency = "Expected"
            certainty = "Likely"
            headline = f"ORANGE ALERT: Severe Thunderstorm & Lightning Expected in {district_name} (Lead Time: ~{lead_time_min} min)"
            instructions = (
                "1. Prepare for high-intensity lightning strikes and localized waterlogging.\n"
                "2. Seek safe shelter before storm arrives.\n"
                "3. Secure loose outdoor objects."
            )
        elif alert_tier == "YELLOW":
            severity = "Moderate"
            urgency = "Future"
            certainty = "Possible"
            headline = f"YELLOW WATCH: Convective Development & Lightning Watch for {district_name}"
            instructions = "Stay weather-aware and monitor continuous nowcast updates."
        else:
            severity = "Minor"
            urgency = "Past"
            certainty = "Unlikely"
            headline = f"GREEN: Normal Weather Conditions in {district_name}"
            instructions = "No immediate severe thunderstorm threat."
            
        desc = (
            f"VIDYUTRAKSHA Multi-Modal Nowcasting System detected severe convective cell {storm_id} "
            f"approaching {district_name}, {state_name}. "
            f"Risk Score: {risk_score:.1f}/100. "
            f"P(Lightning): {p_lightning*100:.0f}%, P(Severe Wind): {p_severe_wind*100:.0f}%, P(Heavy Rain): {p_heavy_rain*100:.0f}%. "
            f"Estimated arrival in {lead_time_min} minutes."
        )
        
        return CAPAlert(
            identifier=f"IN-IMD-VR-{now.strftime('%Y%m%d%H%M')}-{district_name.replace(' ', '_')[:12]}",
            sent=now.isoformat(),
            event="Severe Thunderstorm & Lightning Warning",
            urgency=urgency,
            severity=severity,
            certainty=certainty,
            headline=headline,
            description=desc,
            instruction=instructions,
            areaDesc=f"{district_name}, {state_name}",
            risk_score=risk_score,
            alert_tier=alert_tier,
            polygon_geojson=polygon_geojson,
            affected_population=affected_pop,
            expires=expires.isoformat()
        )
