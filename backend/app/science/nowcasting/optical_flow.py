"""
VIDYUTRAKSHA - Optical Flow & Semi-Lagrangian Advection Nowcaster
Uses Farneback dense optical flow and backward advection for radar reflectivity field nowcasting.
"""
import numpy as np
import cv2
from typing import Tuple, List, Optional


class OpticalFlowNowcaster:
    """Compute dense motion fields and extrapolate radar echo fields."""

    @staticmethod
    def compute_motion_field(frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
        """
        Compute dense optical flow vector field (u, v in pixel displacement)
        using Farneback method.
        """
        f1_norm = np.clip(np.nan_to_num(frame1, nan=0.0) * (255.0 / 75.0), 0, 255).astype(np.uint8)
        f2_norm = np.clip(np.nan_to_num(frame2, nan=0.0) * (255.0 / 75.0), 0, 255).astype(np.uint8)
        
        # Farneback optical flow parameters tuned for meteorological radar echo advection
        flow = cv2.calcOpticalFlowFarneback(
            prev=f1_norm,
            next=f2_norm,
            flow=None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0
        )
        return flow  # Shape: (H, W, 2) where [..., 0] is dx (col), [..., 1] is dy (row)

    @staticmethod
    def extrapolate_field(current_frame: np.ndarray, flow_field: np.ndarray, steps: int = 1) -> np.ndarray:
        """
        Semi-Lagrangian backward advection of radar field across multiple time steps.
        """
        h, w = current_frame.shape[:2]
        # Generate coordinate grid
        grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
        
        # Backward advection map
        map_x = (grid_x - (flow_field[..., 0] * steps)).astype(np.float32)
        map_y = (grid_y - (flow_field[..., 1] * steps)).astype(np.float32)
        
        # Remap using bilinear interpolation
        extrapolated = cv2.remap(
            src=current_frame.astype(np.float32),
            map1=map_x,
            map2=map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0.0
        )
        
        # Diffusive dispersion / decay over longer extrapolation horizons
        if steps > 2:
            kernel_size = min(3 + 2 * (steps // 3), 9)
            sigma = 0.5 * steps
            extrapolated = cv2.GaussianBlur(extrapolated, (kernel_size, kernel_size), sigma)
            # Slight intensity decay representing finite convective cell lifetime (~45-60 min)
            decay_factor = max(1.0 - (0.04 * steps), 0.55)
            extrapolated = extrapolated * decay_factor
            
        return extrapolated
