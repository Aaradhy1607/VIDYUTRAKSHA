"""
VIDYUTRAKSHA - Route & Transportation Corridor Weather Hazard Exposure Engine
Evaluates dynamic convective risk along travel corridors without claiming false deterministic safety.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from shapely.geometry import LineString, Point, Polygon
from pydantic import BaseModel


class WaypointRisk(BaseModel):
    waypoint_index: int
    lat: float
    lon: float
    name: str
    p_lightning: float
    p_heavy_rain: float
    p_severe_wind: float
    risk_score: float
    alert_tier: str
    impact_window_minutes: str


class CorridorSafetyReport(BaseModel):
    corridor_name: str
    origin: str
    destination: str
    total_distance_km: float
    overall_hazard_exposure: str  # LOW, ELEVATED, HIGH, SEVERE
    max_risk_score: float
    highest_risk_section: str
    lightning_strike_probability: float
    estimated_transit_delay_minutes: int
    safe_travel_advisory: str
    waypoints_analysis: List[WaypointRisk]


class CorridorHazardEngine:
    """Evaluates spatial-temporal storm intersections along transportation corridors."""

    @classmethod
    def evaluate_corridor(
        cls,
        origin_name: str,
        origin_coord: Tuple[float, float],
        dest_name: str,
        dest_coord: Tuple[float, float],
        active_storms: List[Dict[str, Any]],
        num_waypoints: int = 6
    ) -> CorridorSafetyReport:
        """
        Compute weather hazard exposure along route segments.
        """
        lat1, lon1 = origin_coord
        lat2, lon2 = dest_coord
        
        # Calculate great-circle distance
        r = 6371.0
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1))*np.cos(np.radians(lat2))*np.sin(dlon/2)**2
        total_dist_km = float(r * 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)))
        
        # Interpolate waypoints
        waypoints: List[WaypointRisk] = []
        max_risk = 0.0
        max_risk_name = f"{origin_name} Section"
        max_p_lightning = 0.0
        
        for i in range(num_waypoints):
            frac = i / max(num_waypoints - 1, 1)
            w_lat = lat1 + frac * (lat2 - lat1)
            w_lon = lon1 + frac * (lon2 - lon1)
            w_point = Point(w_lon, w_lat)
            
            # Intermediate waypoint name
            if i == 0:
                w_name = f"{origin_name} (Origin)"
            elif i == num_waypoints - 1:
                w_name = f"{dest_name} (Destination)"
            else:
                w_name = f"Corridor KM {int(frac * total_dist_km)}"
                
            # Check proximity to all active storms
            min_storm_dist_km = 999.0
            matching_storm = None
            
            for storm in active_storms:
                s_lat = storm.get("centroid_lat", 28.6)
                s_lon = storm.get("centroid_lon", 77.2)
                sd_lat = np.radians(s_lat - w_lat)
                sd_lon = np.radians(s_lon - w_lon)
                sa = np.sin(sd_lat/2)**2 + np.cos(np.radians(w_lat))*np.cos(np.radians(s_lat))*np.sin(sd_lon/2)**2
                s_dist_km = float(r * 2 * np.arctan2(np.sqrt(sa), np.sqrt(1-sa)))
                
                if s_dist_km < min_storm_dist_km:
                    min_storm_dist_km = s_dist_km
                    matching_storm = storm
                    
            # Compute exposure at waypoint
            if min_storm_dist_km < 15.0:  # Direct impact zone
                p_light = matching_storm.get("p_lightning", 0.88)
                p_rain = matching_storm.get("p_heavy_rain", 0.82)
                p_wind = matching_storm.get("p_severe_wind", 0.74)
                w_risk = matching_storm.get("risk_score", 84.0)
                tier = matching_storm.get("severity_tier", "RED")
                impact_window = "0 - 25 min (IMMINENT)"
            elif min_storm_dist_km < 40.0:  # Outer convective fringe
                p_light = matching_storm.get("p_lightning", 0.88) * 0.55
                p_rain = matching_storm.get("p_heavy_rain", 0.82) * 0.45
                p_wind = matching_storm.get("p_severe_wind", 0.74) * 0.35
                w_risk = matching_storm.get("risk_score", 84.0) * 0.50
                tier = "YELLOW"
                impact_window = "30 - 60 min"
            else:
                p_light, p_rain, p_wind, w_risk, tier = 0.08, 0.12, 0.05, 12.0, "GREEN"
                impact_window = "No active convective cell"
                
            if w_risk > max_risk:
                max_risk = w_risk
                max_risk_name = w_name
            if p_light > max_p_lightning:
                max_p_lightning = p_light
                
            waypoints.append(WaypointRisk(
                waypoint_index=i,
                lat=round(w_lat, 4),
                lon=round(w_lon, 4),
                name=w_name,
                p_lightning=round(p_light, 2),
                p_heavy_rain=round(p_rain, 2),
                p_severe_wind=round(p_wind, 2),
                risk_score=round(w_risk, 1),
                alert_tier=tier,
                impact_window_minutes=impact_window
            ))
            
        # Overall corridor exposure classification
        if max_risk >= 75.0:
            overall_exposure = "SEVERE"
            delays = 45
            advisory = "SEVERE CONVECTIVE HAZARD: High probability of lightning strikes & squall winds. Recommend delaying non-emergency travel."
        elif max_risk >= 50.0:
            overall_exposure = "HIGH"
            delays = 25
            advisory = "HIGH WEATHER EXPOSURE: Thunderstorm approaching corridor. Exercise caution, anticipate reduced visibility and localized ponding."
        elif max_risk >= 25.0:
            overall_exposure = "ELEVATED"
            delays = 10
            advisory = "ELEVATED WATCH: Convective clouds developing along route. Monitor live nowcasts."
        else:
            overall_exposure = "LOW"
            delays = 0
            advisory = "NORMAL CONDITIONS: No convective weather hazards currently obstructing transit."
            
        return CorridorSafetyReport(
            corridor_name=f"{origin_name} to {dest_name}",
            origin=origin_name,
            destination=dest_name,
            total_distance_km=round(total_dist_km, 1),
            overall_hazard_exposure=overall_exposure,
            max_risk_score=round(max_risk, 1),
            highest_risk_section=max_risk_name,
            lightning_strike_probability=round(max_p_lightning, 2),
            estimated_transit_delay_minutes=delays,
            safe_travel_advisory=advisory,
            waypoints_analysis=waypoints
        )
