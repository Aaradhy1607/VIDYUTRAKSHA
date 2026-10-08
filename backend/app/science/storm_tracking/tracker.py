"""
VIDYUTRAKSHA - Hungarian Storm Tracking & Kinematic Engine
Maintains storm object identities across time using Hungarian matching and Kalman-like kinematics.
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from scipy.optimize import linear_sum_assignment
from backend.app.science.storm_detection.detector import DetectedStormCell
from backend.app.science.storm_tracking.lifecycle import StormLifecycleEngine, LifecycleState


class TrackedStormObject:
    """Active storm track history and digital twin state."""
    def __init__(self, initial_cell: DetectedStormCell):
        self.storm_id = initial_cell.storm_id
        self.history: List[DetectedStormCell] = [initial_cell]
        self.first_detected = initial_cell.timestamp
        self.last_updated = initial_cell.timestamp
        self.centroid_lat = initial_cell.centroid_lat
        self.centroid_lon = initial_cell.centroid_lon
        self.speed_kmh = 0.0
        self.direction_deg = 0.0
        self.vx_kmh = 0.0
        self.vy_kmh = 0.0
        self.lifecycle_state = LifecycleState.INITIATING
        self.lifetime_minutes = 10
        self.missed_cycles = 0


class StormTracker:
    """Multi-target Hungarian association and trajectory estimation."""

    def __init__(
        self,
        max_distance_km: float = 65.0,  # Max allowable movement in 10-15 mins (~250 km/h upper limit)
        max_missed_cycles: int = 2
    ):
        self.max_distance_km = max_distance_km
        self.max_missed_cycles = max_missed_cycles
        self.active_tracks: Dict[str, TrackedStormObject] = {}
        self.next_id_counter = 1

    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine formula for great circle distance in km."""
        r = 6371.0
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        dphi = np.radians(lat2 - lat1)
        dlam = np.radians(lon2 - lon1)
        
        a = np.sin(dphi / 2.0)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2.0)**2
        c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
        return float(r * c)

    @staticmethod
    def calculate_bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate compass bearing (0-360°) from point 1 to point 2."""
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        dlam = np.radians(lon2 - lon1)
        
        y = np.sin(dlam) * np.cos(phi2)
        x = np.cos(phi1) * np.sin(phi2) - np.sin(phi1) * np.cos(phi2) * np.cos(dlam)
        bearing = (np.degrees(np.arctan2(y, x)) + 360.0) % 360.0
        return float(bearing)

    def update_tracks(
        self,
        detected_cells: List[DetectedStormCell],
        current_time: datetime,
        dt_minutes: float = 10.0
    ) -> List[DetectedStormCell]:
        """
        Associate new detections with existing active tracks via Hungarian cost optimization.
        """
        active_ids = list(self.active_tracks.keys())
        n_active = len(active_ids)
        n_new = len(detected_cells)
        
        if n_active == 0:
            # Initialize tracks for all detections
            for cell in detected_cells:
                track = TrackedStormObject(cell)
                self.active_tracks[cell.storm_id] = track
            return detected_cells
            
        if n_new == 0:
            # Mark all as missed
            for track_id in active_ids:
                self.active_tracks[track_id].missed_cycles += 1
                if self.active_tracks[track_id].missed_cycles > self.max_missed_cycles:
                    del self.active_tracks[track_id]
            return []
            
        # Build Cost Matrix (Distance + Area Difference + Intensity Difference)
        cost_matrix = np.full((n_active, n_new), 1e6)
        
        for i, track_id in enumerate(active_ids):
            track = self.active_tracks[track_id]
            last_cell = track.history[-1]
            
            # Predict expected position using previous velocity
            dt_hours = dt_minutes / 60.0
            pred_lat = track.centroid_lat + (track.vy_kmh * dt_hours / 111.13)
            pred_lon = track.centroid_lon + (track.vx_kmh * dt_hours / (111.13 * np.cos(np.radians(track.centroid_lat))))
            
            for j, new_cell in enumerate(detected_cells):
                dist_km = self.haversine_distance_km(pred_lat, pred_lon, new_cell.centroid_lat, new_cell.centroid_lon)
                
                if dist_km <= self.max_distance_km:
                    # Penalize large area jumps and intensity jumps
                    area_diff_ratio = abs(new_cell.area_km2 - last_cell.area_km2) / max(last_cell.area_km2, 10.0)
                    dbz_diff = abs(new_cell.max_reflectivity_dbz - last_cell.max_reflectivity_dbz)
                    
                    cost = dist_km + (area_diff_ratio * 15.0) + (dbz_diff * 0.5)
                    cost_matrix[i, j] = cost
                    
        # Solve Hungarian Assignment
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        matched_new = set()
        matched_active = set()
        
        for r, c in zip(row_ind, col_ind):
            if cost_matrix[r, c] < 500.0:  # Valid match threshold
                track_id = active_ids[r]
                track = self.active_tracks[track_id]
                new_cell = detected_cells[c]
                
                # Keep consistent ID
                new_cell.storm_id = track.storm_id
                
                # Calculate kinematics
                last_cell = track.history[-1]
                dist_km = self.haversine_distance_km(last_cell.centroid_lat, last_cell.centroid_lon, new_cell.centroid_lat, new_cell.centroid_lon)
                dt_hours = max((new_cell.timestamp - last_cell.timestamp).total_seconds() / 3600.0, 0.05)
                speed = float(dist_km / dt_hours)
                bearing = self.calculate_bearing_deg(last_cell.centroid_lat, last_cell.centroid_lon, new_cell.centroid_lat, new_cell.centroid_lon)
                
                # Smooth velocity
                new_cell.speed_kmh = round(float(np.clip(speed, 5.0, 140.0)), 1)
                new_cell.direction_deg = round(bearing, 1)
                
                # Velocity components in km/h
                rad = np.radians(bearing)
                track.vx_kmh = new_cell.speed_kmh * np.sin(rad)
                track.vy_kmh = new_cell.speed_kmh * np.cos(rad)
                
                # Lifecycle update
                lifetime_min = int((new_cell.timestamp - track.first_detected).total_seconds() / 60.0) + 10
                transition = StormLifecycleEngine.evaluate_lifecycle(
                    lifetime_min=lifetime_min,
                    area_prev_km2=last_cell.area_km2,
                    area_curr_km2=new_cell.area_km2,
                    dbz_prev=last_cell.max_reflectivity_dbz,
                    dbz_curr=new_cell.max_reflectivity_dbz,
                    flash_rate_prev=last_cell.flash_rate_min,
                    flash_rate_curr=new_cell.flash_rate_min,
                    dt_minutes=dt_minutes
                )
                new_cell.lifecycle_state = transition.current_state.value
                
                track.history.append(new_cell)
                track.centroid_lat = new_cell.centroid_lat
                track.centroid_lon = new_cell.centroid_lon
                track.speed_kmh = new_cell.speed_kmh
                track.direction_deg = new_cell.direction_deg
                track.last_updated = new_cell.timestamp
                track.missed_cycles = 0
                
                matched_new.add(c)
                matched_active.add(r)
                
        # Unmatched new cells -> create new tracks
        for j in range(n_new):
            if j not in matched_new:
                cell = detected_cells[j]
                track = TrackedStormObject(cell)
                self.active_tracks[cell.storm_id] = track
                
        # Unmatched active tracks -> increment missed count
        for i in range(n_active):
            if i not in matched_active:
                track_id = active_ids[i]
                self.active_tracks[track_id].missed_cycles += 1
                if self.active_tracks[track_id].missed_cycles > self.max_missed_cycles:
                    del self.active_tracks[track_id]
                    
        return detected_cells
