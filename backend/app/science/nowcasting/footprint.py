"""
VIDYUTRAKSHA - Storm Footprint & Dispersion Cone of Uncertainty
Generates projected storm contours, expanding uncertainty envelopes, and probabilistic impact footprints.
"""
import numpy as np
from typing import Dict, Any, List, Tuple
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.affinity import translate, rotate, scale
from pydantic import BaseModel


class HorizonFootprint(BaseModel):
    horizon_minutes: int
    projected_centroid_lat: float
    projected_centroid_lon: float
    projected_area_km2: float
    projected_polygon_geojson: Dict[str, Any]
    uncertainty_cone_geojson: Dict[str, Any]
    p_lightning: float
    p_thunderstorm: float
    p_heavy_rain: float
    p_severe_wind: float
    confidence: float


class StormFootprintEngine:
    """Calculates kinematic extrapolation and uncertainty cone dispersion across horizons."""

    @staticmethod
    def project_cell(
        centroid_lat: float,
        centroid_lon: float,
        speed_kmh: float,
        direction_deg: float,
        polygon_geojson: Dict[str, Any],
        horizon_minutes: int,
        base_p_lightning: float = 0.85,
        base_p_thunderstorm: float = 0.90,
        base_p_heavy_rain: float = 0.75,
        base_p_severe_wind: float = 0.60
    ) -> HorizonFootprint:
        """
        Project storm position and expanding cone of uncertainty at lead time T.
        """
        # Advection displacement
        hours = horizon_minutes / 60.0
        dist_km = speed_kmh * hours
        
        rad = np.radians(direction_deg)
        dx_km = dist_km * np.sin(rad)
        dy_km = dist_km * np.cos(rad)
        
        # Convert km displacement to degrees
        km_per_deg_lat = 111.13
        km_per_deg_lon = 111.13 * np.cos(np.radians(centroid_lat))
        
        dlat = dy_km / km_per_deg_lat
        dlon = dx_km / km_per_deg_lon
        
        new_lat = centroid_lat + dlat
        new_lon = centroid_lon + dlon
        
        # Original polygon
        coords = polygon_geojson.get("coordinates", [[]])[0]
        if not coords or len(coords) < 3:
            # Generate default synthetic ellipse around centroid
            theta = np.linspace(0, 2*np.pi, 16)
            rx = 0.15
            ry = 0.12
            coords = [[centroid_lon + rx*np.cos(t), centroid_lat + ry*np.sin(t)] for t in theta]
            coords.append(coords[0])
            
        poly = Polygon(coords)
        
        # Translate polygon
        translated_poly = translate(poly, xoff=dlon, yoff=dlat)
        
        # Skill & confidence degradation over lead time (scientifically honest decay curve)
        # 15m: 95% skill, 30m: 85%, 60m: 68%, 120m: 48%, 180m: 32%
        decay_factors = {0: 1.0, 15: 0.94, 30: 0.84, 60: 0.68, 120: 0.48, 180: 0.32}
        decay = decay_factors.get(horizon_minutes, max(1.0 - 0.0035 * horizon_minutes, 0.25))
        
        p_light = round(float(np.clip(base_p_lightning * decay, 0.05, 0.98)), 2)
        p_storm = round(float(np.clip(base_p_thunderstorm * decay, 0.05, 0.99)), 2)
        p_rain = round(float(np.clip(base_p_heavy_rain * (decay * 0.95), 0.05, 0.95)), 2)
        p_wind = round(float(np.clip(base_p_severe_wind * (decay * 0.90), 0.05, 0.92)), 2)
        confidence = round(float(decay), 2)
        
        # Build expanding cone of uncertainty
        # Angular spread expands from +/- 10 deg at 15 min to +/- 35 deg at 180 min
        angle_spread_deg = min(10.0 + (horizon_minutes * 0.15), 40.0)
        radius_spread_km = dist_km * np.tan(np.radians(angle_spread_deg)) + (horizon_minutes * 0.1)
        r_deg_lon = radius_spread_km / km_per_deg_lon
        r_deg_lat = radius_spread_km / km_per_deg_lat
        
        cone_pts = []
        # Origin point at current position
        cone_pts.append([round(centroid_lon, 4), round(centroid_lat, 4)])
        # Arc around target position
        arc_angles = np.linspace(direction_deg - angle_spread_deg, direction_deg + angle_spread_deg, 9)
        for a in arc_angles:
            a_rad = np.radians(a)
            arc_dist = dist_km * 1.15
            pt_x = centroid_lon + (arc_dist * np.sin(a_rad)) / km_per_deg_lon
            pt_y = centroid_lat + (arc_dist * np.cos(a_rad)) / km_per_deg_lat
            cone_pts.append([round(pt_x, 4), round(pt_y, 4)])
        cone_pts.append([round(centroid_lon, 4), round(centroid_lat, 4)])
        
        proj_geojson = {
            "type": "Polygon",
            "coordinates": [[[round(c[0], 4), round(c[1], 4)] for c in translated_poly.exterior.coords]]
        }
        
        cone_geojson = {
            "type": "Polygon",
            "coordinates": [cone_pts]
        }
        
        return HorizonFootprint(
            horizon_minutes=horizon_minutes,
            projected_centroid_lat=round(new_lat, 4),
            projected_centroid_lon=round(new_lon, 4),
            projected_area_km2=round(poly.area * (km_per_deg_lat * km_per_deg_lon), 1),
            projected_polygon_geojson=proj_geojson,
            uncertainty_cone_geojson=cone_geojson,
            p_lightning=p_light,
            p_thunderstorm=p_storm,
            p_heavy_rain=p_rain,
            p_severe_wind=p_wind,
            confidence=confidence
        )
