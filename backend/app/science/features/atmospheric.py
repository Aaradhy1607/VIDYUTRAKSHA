"""
VIDYUTRAKSHA - Atmospheric Instability & Thermodynamic Feature Engine
Meteorologically rigorous implementation of sounding indices and convective parameters.
"""
import numpy as np
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel


class InstabilityIndices(BaseModel):
    cape_j_kg: float
    cin_j_kg: float
    lifted_index_c: float
    k_index_c: float
    total_totals_c: float
    precipitable_water_mm: float
    bulk_shear_0_6km_ms: float
    lapse_rate_700_500_c_km: float
    dewpoint_depression_sfc_c: float
    convective_trigger_potential: str  # LOW, MODERATE, HIGH, EXTREME


class AtmosphericPhysics:
    """Rigorous thermodynamic calculations for convective environments."""

    @staticmethod
    def calculate_vapor_pressure(temp_c: float) -> float:
        """Tetens formula for saturation vapor pressure in hPa."""
        return 6.112 * np.exp((17.67 * temp_c) / (temp_c + 243.5))

    @staticmethod
    def calculate_dewpoint(temp_c: float, rh_pct: float) -> float:
        """Calculate dew point temperature (°C) using Magnus-Tetens approximation."""
        rh = np.clip(rh_pct, 1.0, 100.0) / 100.0
        a = 17.27
        b = 237.7
        alpha = ((a * temp_c) / (b + temp_c)) + np.log(rh)
        return (b * alpha) / (a - alpha)

    @staticmethod
    def calculate_k_index(t850: float, t700: float, t500: float, td850: float, td700: float) -> float:
        """
        K-Index = (T850 - T500) + Td850 - (T700 - Td700)
        Standard indicator of airmass thunderstorm potential:
        < 20: Near zero potential
        20-25: Isolated thunderstorms
        26-30: Widely scattered thunderstorms
        31-35: Scattered thunderstorms
        > 35: High probability of severe thunderstorms
        """
        return (t850 - t500) + td850 - (t700 - td700)

    @staticmethod
    def calculate_total_totals(t850: float, t500: float, td850: float) -> float:
        """
        Total Totals Index (TT) = (T850 + Td850) - 2 * T500
        TT = Vertical Totals (T850 - T500) + Cross Totals (Td850 - T500)
        < 44: Thunderstorms unlikely
        44-49: Thunderstorms possible
        50-55: Severe thunderstorms likely
        > 55: Severe thunderstorms with tornadoes/large hail
        """
        return (t850 + td850) - (2.0 * t500)

    @staticmethod
    def calculate_lifted_index(t500_env: float, t_sfc: float, td_sfc: float, p_sfc_hpa: float = 1000.0) -> float:
        """
        Lifted Index (LI) = T500_env - T500_parcel (lifted pseudoadiabatically from surface)
        Negative LI denotes instability:
        0 to -2: Weakly unstable
        -3 to -5: Moderately unstable
        -6 or lower: Extremely unstable / severe thunderstorm potential
        """
        # Lifting condensation level (LCL) temperature approximation (Bolton 1980)
        t_k = t_sfc + 273.15
        td_k = td_sfc + 273.15
        t_lcl_k = (1.0 / (1.0 / (td_k - 56.0) + (np.log(t_k / td_k) / 800.0))) + 56.0
        
        # Approximate moist adiabatic parcel temperature at 500 hPa
        # Standard moist lapse rate approximation (~6.5 K/km from ~1.5km LCL to 5.5km 500hPa)
        z_approx_km = 5.5 - 1.5
        t500_parcel_c = (t_lcl_k - 273.15) - (6.0 * z_approx_km)
        
        return t500_env - t500_parcel_c

    @staticmethod
    def calculate_cape_cin(
        t_sfc: float,
        td_sfc: float,
        t850: float,
        t700: float,
        t500: float,
        t300: float,
        p_sfc: float = 1013.25
    ) -> Tuple[float, float]:
        """
        Calculate Convective Available Potential Energy (CAPE, J/kg) and Convective Inhibition (CIN, J/kg).
        Integrates buoyancy: B = g * (Tv_parcel - Tv_env) / Tv_env dz
        """
        g = 9.80665
        levels_p = [p_sfc, 850.0, 700.0, 500.0, 300.0]
        levels_t_env = [t_sfc, t850, t700, t500, t300]
        # Standard atmosphere geopotential heights (m)
        levels_z = [0.0, 1450.0, 3010.0, 5570.0, 9160.0]
        
        # Parcel trajectory approximation
        # Dry ascent to LCL (~1000m for typical boundary layer)
        t_parcel = [t_sfc]
        lcl_z = 125.0 * (t_sfc - td_sfc)  # Espy's equation for LCL height (m)
        
        for z in levels_z[1:]:
            if z <= lcl_z:
                # Dry adiabatic (9.8 K/km)
                tp = t_sfc - (9.8 * z / 1000.0)
            else:
                # Moist adiabatic (~6.2 K/km)
                tp_lcl = t_sfc - (9.8 * lcl_z / 1000.0)
                tp = tp_lcl - (6.2 * (z - lcl_z) / 1000.0)
            t_parcel.append(tp)
            
        cape = 0.0
        cin = 0.0
        
        for i in range(len(levels_z) - 1):
            dz = levels_z[i+1] - levels_z[i]
            # Mean temperature at layer
            tp_avg = (t_parcel[i] + t_parcel[i+1]) / 2.0 + 273.15
            te_avg = (levels_t_env[i] + levels_t_env[i+1]) / 2.0 + 273.15
            
            buoyancy = g * (tp_avg - te_avg) / te_avg
            if buoyancy > 0:
                cape += buoyancy * dz
            else:
                # Near surface negative buoyancy is CIN
                if levels_z[i+1] <= 3000.0:
                    cin += abs(buoyancy * dz)
                    
        return float(np.clip(cape, 0.0, 6500.0)), float(np.clip(cin, 0.0, 800.0))

    @staticmethod
    def calculate_bulk_shear(u_sfc: float, v_sfc: float, u_6km: float, v_6km: float) -> float:
        """
        Deep-layer vertical wind shear (0-6 km AGL, m/s).
        Key discriminator for storm mode:
        < 10 m/s: Single-cell / pulse thunderstorms
        10-20 m/s: Multicell clusters / squall lines
        > 20 m/s: Severe supercells with high tornado & severe hail potential
        """
        du = u_6km - u_sfc
        dv = v_6km - v_sfc
        return float(np.sqrt(du**2 + dv**2))

    @classmethod
    def evaluate_sounding(
        cls,
        t_sfc: float,
        td_sfc: float,
        t850: float,
        td850: float,
        t700: float,
        td700: float,
        t500: float,
        t300: float,
        pwat_mm: float,
        wind_sfc_ms: float = 3.0,
        wind_6km_ms: float = 18.0
    ) -> InstabilityIndices:
        """Compute full suite of operational atmospheric instability parameters."""
        k_index = cls.calculate_k_index(t850, t700, t500, td850, td700)
        tt = cls.calculate_total_totals(t850, t500, td850)
        li = cls.calculate_lifted_index(t500, t_sfc, td_sfc)
        cape, cin = cls.calculate_cape_cin(t_sfc, td_sfc, t850, t700, t500, t300)
        shear = abs(wind_6km_ms - wind_sfc_ms)  # 0-6 km bulk shear
        lapse_rate = abs(t700 - t500) / 2.56    # Lapse rate 700-500 hPa in °C/km
        dew_dep = t_sfc - td_sfc
        
        # Convective trigger evaluation
        if cape > 2500 and li < -6 and shear > 15:
            trigger = "EXTREME"
        elif cape > 1500 and li < -4:
            trigger = "HIGH"
        elif cape > 800 and li < -1:
            trigger = "MODERATE"
        else:
            trigger = "LOW"
            
        return InstabilityIndices(
            cape_j_kg=round(cape, 1),
            cin_j_kg=round(cin, 1),
            lifted_index_c=round(li, 1),
            k_index_c=round(k_index, 1),
            total_totals_c=round(tt, 1),
            precipitable_water_mm=round(pwat_mm, 1),
            bulk_shear_0_6km_ms=round(shear, 1),
            lapse_rate_700_500_c_km=round(lapse_rate, 2),
            dewpoint_depression_sfc_c=round(dew_dep, 1),
            convective_trigger_potential=trigger
        )
