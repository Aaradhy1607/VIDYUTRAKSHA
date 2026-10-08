"""
Tests for Atmospheric Thermodynamic Calculations & Sounding Indices
"""
import pytest
import numpy as np
from backend.app.science.features.atmospheric import AtmosphericPhysics


def test_dewpoint_calculation():
    temp_c = 30.0
    rh_pct = 70.0
    td = AtmosphericPhysics.calculate_dewpoint(temp_c, rh_pct)
    assert 23.0 <= td <= 25.0
    assert td < temp_c


def test_k_index_calculation():
    # Typical severe thunderstorm profile
    t850, t700, t500 = 22.0, 10.0, -10.0
    td850, td700 = 18.0, 6.0
    ki = AtmosphericPhysics.calculate_k_index(t850, t700, t500, td850, td700)
    # (22 - (-10)) + 18 - (10 - 6) = 32 + 18 - 4 = 46.0
    assert ki == 46.0


def test_total_totals_calculation():
    t850, t500, td850 = 22.0, -12.0, 18.0
    tt = AtmosphericPhysics.calculate_total_totals(t850, t500, td850)
    # (22 + 18) - 2 * (-12) = 40 + 24 = 64.0
    assert tt == 64.0


def test_cape_cin_calculation():
    cape, cin = AtmosphericPhysics.calculate_cape_cin(
        t_sfc=35.0,
        td_sfc=24.0,
        t850=22.0,
        t700=10.0,
        t500=-10.0,
        t300=-35.0
    )
    assert cape > 1000.0  # Strongly positive buoyant energy
    assert cin >= 0.0


def test_bulk_shear_calculation():
    shear = AtmosphericPhysics.calculate_bulk_shear(u_sfc=2.0, v_sfc=3.0, u_6km=16.0, v_6km=18.0)
    # du = 14, dv = 15, sqrt(14^2 + 15^2) = sqrt(196 + 225) = sqrt(421) ~ 20.5 m/s
    assert 20.0 <= shear <= 21.0
