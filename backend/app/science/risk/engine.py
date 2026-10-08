"""
VIDYUTRAKSHA - Transparent Multi-Factor Risk & Vulnerability Engine
Computes transparent 0-100 risk score combining multi-hazard probabilities,
storm intensification, population exposure, lead time, and uncertainty.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class RiskAssessment(BaseModel):
    risk_score: float  # 0 to 100
    alert_level: str   # GREEN, YELLOW, ORANGE, RED
    lightning_factor: float
    storm_intensity_factor: float
    population_exposure_tier: str  # LOW, MODERATE, HIGH, EXTREME
    population_exposure_weight: float
    lead_time_urgency_factor: float
    confidence_weight: float
    contributing_breakdown: Dict[str, Any]


# Representative population densities and vulnerability weights for Indian districts
DISTRICT_POPULATION_EXPOSURE = {
    "North West Delhi": {"density_km2": 8200, "exposure_tier": "EXTREME", "weight": 1.35},
    "Central Delhi": {"density_km2": 9300, "exposure_tier": "EXTREME", "weight": 1.40},
    "Gurugram": {"density_km2": 1200, "exposure_tier": "HIGH", "weight": 1.20},
    "Noida / Gautam Buddha Nagar": {"density_km2": 1100, "exposure_tier": "HIGH", "weight": 1.20},
    "Khurda (Bhubaneswar)": {"density_km2": 800, "exposure_tier": "HIGH", "weight": 1.18},
    "Cuttack": {"density_km2": 670, "exposure_tier": "MODERATE", "weight": 1.12},
    "Mumbai Suburban": {"density_km2": 21000, "exposure_tier": "EXTREME", "weight": 1.50},
    "Thane": {"density_km2": 1150, "exposure_tier": "HIGH", "weight": 1.22},
    "Kolkata": {"density_km2": 24000, "exposure_tier": "EXTREME", "weight": 1.50},
    "Bengaluru Urban": {"density_km2": 4400, "exposure_tier": "EXTREME", "weight": 1.30},
    "Hyderabad": {"density_km2": 18000, "exposure_tier": "EXTREME", "weight": 1.45},
    "DEFAULT_RURAL": {"density_km2": 350, "exposure_tier": "MODERATE", "weight": 1.00}
}


class RiskEngine:
    """Calculates operational threat scores and impact vulnerability."""

    @classmethod
    def calculate_risk(
        cls,
        p_lightning: float,
        p_thunderstorm: float,
        p_heavy_rain: float,
        p_severe_wind: float,
        max_reflectivity_dbz: float,
        flash_rate_min: float,
        growth_rate_area_pct: float,
        horizon_minutes: int,
        confidence: float,
        district_name: str = "North West Delhi"
    ) -> RiskAssessment:
        """
        Synthesize multi-hazard probabilities into an explainable 0-100 Risk Score:
        Risk = Hazard_Index * Vulnerability_Exposure * Urgency_Factor * (1 + Uncertainty_Penalty)
        """
        # 1. Hazard Probability Index (0 - 45 pts)
        hazard_index = (
            (p_lightning * 0.35) +
            (p_thunderstorm * 0.30) +
            (p_heavy_rain * 0.20) +
            (p_severe_wind * 0.15)
        ) * 45.0
        
        # 2. Storm Physical Intensification & Severity (0 - 30 pts)
        dbz_component = min(max(max_reflectivity_dbz - 30.0, 0.0) / 30.0, 1.0) * 15.0
        flash_component = min(flash_rate_min / 30.0, 1.0) * 10.0
        growth_component = min(max(growth_rate_area_pct, 0.0) / 60.0, 1.0) * 5.0
        physical_severity = dbz_component + flash_component + growth_component
        
        # 3. Urgency / Lead Time Factor (0 - 15 pts)
        # Immediate threats (15-30m) have higher imminent urgency than 180m
        if horizon_minutes <= 15:
            urgency_pts = 15.0
        elif horizon_minutes <= 30:
            urgency_pts = 12.0
        elif horizon_minutes <= 60:
            urgency_pts = 8.0
        elif horizon_minutes <= 120:
            urgency_pts = 5.0
        else:
            urgency_pts = 2.0
            
        # 4. Population Exposure Multiplier
        district_info = DISTRICT_POPULATION_EXPOSURE.get(district_name, DISTRICT_POPULATION_EXPOSURE["DEFAULT_RURAL"])
        pop_weight = district_info["weight"]
        
        # Raw composite score
        base_score = (hazard_index + physical_severity + urgency_pts)
        scaled_score = base_score * (0.8 + 0.2 * pop_weight) * (0.85 + 0.15 * confidence)
        
        final_risk_score = round(float(min(max(scaled_score, 0.0), 100.0)), 1)
        
        # Determine Alert Level
        if final_risk_score >= 75.0:
            alert_level = "RED"      # Severe / Imminent threat
        elif final_risk_score >= 50.0:
            alert_level = "ORANGE"   # High risk
        elif final_risk_score >= 25.0:
            alert_level = "YELLOW"   # Elevated risk
        else:
            alert_level = "GREEN"    # Low risk
            
        breakdown = {
            "hazard_index_pts": round(hazard_index, 1),
            "physical_severity_pts": round(physical_severity, 1),
            "lead_time_urgency_pts": round(urgency_pts, 1),
            "population_density_km2": district_info["density_km2"],
            "district_exposure_tier": district_info["exposure_tier"],
            "confidence_score_pct": round(confidence * 100.0, 1)
        }
        
        return RiskAssessment(
            risk_score=final_risk_score,
            alert_level=alert_level,
            lightning_factor=round(p_lightning * 100.0, 1),
            storm_intensity_factor=round(max_reflectivity_dbz, 1),
            population_exposure_tier=district_info["exposure_tier"],
            population_exposure_weight=pop_weight,
            lead_time_urgency_factor=round(urgency_pts, 1),
            confidence_weight=confidence,
            contributing_breakdown=breakdown
        )
