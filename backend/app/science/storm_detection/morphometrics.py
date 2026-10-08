"""
VIDYUTRAKSHA - Storm Morphometrics & Geometry
Computes spatial geometry, area in km², eccentricity, orientation, and polygon contours.
"""
import numpy as np
import cv2
from typing import Dict, Any, List, Tuple, Optional
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import unary_union
from pydantic import BaseModel


class StormMorphology(BaseModel):
    centroid_lat: float
    centroid_lon: float
    area_km2: float
    perimeter_km: float
    eccentricity: float
    orientation_deg: float
    max_intensity: float
    mean_intensity: float
    polygon_geojson: Dict[str, Any]
    bounding_box: List[float]  # [min_lon, min_lat, max_lon, max_lat]


class StormMorphometrics:
    """Compute physical dimensions and geometric contours on latitude/longitude coordinate grid."""

    @staticmethod
    def grid_to_geo(row: float, col: float, grid_bbox: List[float], grid_shape: Tuple[int, int]) -> Tuple[float, float]:
        """Convert array row, col to geographic (lat, lon)."""
        min_lon, min_lat, max_lon, max_lat = grid_bbox
        nrows, ncols = grid_shape
        # row 0 is top (max_lat), row nrows-1 is bottom (min_lat)
        lat = max_lat - (row / max(nrows - 1, 1)) * (max_lat - min_lat)
        lon = min_lon + (col / max(ncols - 1, 1)) * (max_lon - min_lon)
        return float(lat), float(lon)

    @classmethod
    def calculate_cell_geometry(
        cls,
        binary_mask: np.ndarray,
        intensity_grid: np.ndarray,
        grid_bbox: List[float],
        cell_label: int = 1,
        min_area_km2: float = 15.0
    ) -> Optional[StormMorphology]:
        """Extract polygon contour, area, centroid, and orientation from a labeled cluster."""
        cell_pixels = (binary_mask == cell_label).astype(np.uint8)
        if np.sum(cell_pixels) == 0:
            return None
            
        # Find contours using OpenCV
        contours, _ = cv2.findContours(cell_pixels, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
            
        # Pick largest external contour for cell
        main_contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(main_contour) < 2:  # Too small in pixel space
            return None
            
        # Moments for centroid
        M = cv2.moments(main_contour)
        if M["m00"] == 0:
            return None
            
        col_c = M["m10"] / M["m00"]
        row_c = M["m01"] / M["m00"]
        cent_lat, cent_lon = cls.grid_to_geo(row_c, col_c, grid_bbox, binary_mask.shape)
        
        # Convert contour points to geo-polygon coordinates
        geo_coords = []
        for pt in main_contour:
            c, r = pt[0][0], pt[0][1]
            lat_pt, lon_pt = cls.grid_to_geo(r, c, grid_bbox, binary_mask.shape)
            geo_coords.append([lon_pt, lat_pt])
            
        if len(geo_coords) < 3:
            return None
            
        # Close polygon
        if geo_coords[0] != geo_coords[-1]:
            geo_coords.append(geo_coords[0])
            
        poly = Polygon(geo_coords)
        if not poly.is_valid:
            poly = poly.buffer(0)
            if poly.is_empty:
                return None
                
        # Area estimation in km² (approx 1° lat ~ 111 km, 1° lon ~ 111 * cos(lat) km)
        lat_rad = np.radians(cent_lat)
        km_per_deg_lat = 111.13
        km_per_deg_lon = 111.13 * np.cos(lat_rad)
        
        # Pixel area in km²
        nrows, ncols = binary_mask.shape
        min_lon, min_lat, max_lon, max_lat = grid_bbox
        dlat = (max_lat - min_lat) / nrows
        dlon = (max_lon - min_lon) / ncols
        pixel_area_km2 = (dlat * km_per_deg_lat) * (dlon * km_per_deg_lon)
        area_km2 = float(np.sum(cell_pixels) * pixel_area_km2)
        
        if area_km2 < min_area_km2:
            return None
            
        # Intensity statistics
        masked_intensity = intensity_grid[cell_pixels > 0]
        max_int = float(np.max(masked_intensity)) if len(masked_intensity) > 0 else 0.0
        mean_int = float(np.mean(masked_intensity)) if len(masked_intensity) > 0 else 0.0
        
        # Perimeter and orientation/eccentricity
        perimeter_km = float(poly.length * 0.5 * (km_per_deg_lat + km_per_deg_lon))
        
        if len(main_contour) >= 5:
            ellipse = cv2.fitEllipse(main_contour)
            (center, (axis_a, axis_b), angle) = ellipse
            major_axis = max(axis_a, axis_b)
            minor_axis = min(axis_a, axis_b)
            eccentricity = float(np.sqrt(1.0 - (minor_axis / max(major_axis, 1e-3))**2)) if major_axis > 0 else 0.0
            orientation = float(angle)
        else:
            eccentricity = 0.5
            orientation = 0.0
            
        geojson_geom = {
            "type": "Polygon",
            "coordinates": [[[round(c[0], 4), round(c[1], 4)] for c in poly.exterior.coords]]
        }
        
        bounds = poly.bounds  # (minx, miny, maxx, maxy)
        
        return StormMorphology(
            centroid_lat=round(cent_lat, 4),
            centroid_lon=round(cent_lon, 4),
            area_km2=round(area_km2, 1),
            perimeter_km=round(perimeter_km, 1),
            eccentricity=round(eccentricity, 2),
            orientation_deg=round(orientation, 1),
            max_intensity=round(max_int, 1),
            mean_intensity=round(mean_int, 1),
            polygon_geojson=geojson_geom,
            bounding_box=[round(bounds[0], 4), round(bounds[1], 4), round(bounds[2], 4), round(bounds[3], 4)]
        )
