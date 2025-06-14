from __future__ import annotations

"""Tests for track test."""


import math

import pytest

from traffic_sim.core.track import StadiumTrack


def test_stadium_dimensions_basic():
    track = StadiumTrack(total_length_m=1000.0, straight_fraction=0.30)
    R = track.radius_m
    S = track.straight_length_m
    # Check reconstruction of total length: L = 2πR + 2S
    L_recon = 2 * math.pi * R + 2 * S
    assert pytest.approx(L_recon, rel=1e-9) == 1000.0


@pytest.mark.parametrize("V,e,f", [(120.0, 0.08, 0.10), (100.0, 0.06, 0.12)])
def test_safe_radius_and_speed_consistency(V, e, f):
    track = StadiumTrack(total_length_m=1000.0, straight_fraction=0.30)
    Rmin = track.safe_radius_min_m(V, e, f)
    Vsafe = math.sqrt(127.0 * Rmin * (e + f))
    assert pytest.approx(Vsafe, rel=1e-12) == V


def test_length_needed_formula_inverts_radius():
    track = StadiumTrack(total_length_m=1000.0, straight_fraction=0.30)
    target_R = 250.0
    L_needed = track.needed_length_for_radius_m(target_R)
    # Recompute radius from that length with same straight fraction
    recon_R = (L_needed * (1.0 - track.straight_fraction)) / (2.0 * math.pi)
    assert pytest.approx(recon_R, rel=1e-12) == target_R


def test_position_heading_continuity():
    track = StadiumTrack(total_length_m=1000.0, straight_fraction=0.30)
    L = track.total_length
    # Check that small steps along s produce small spatial changes (no NaNs; finite)
    s_vals = [i * (L / 200.0) for i in range(201)]
    prev = None
    for s in s_vals:
        x, y, th = track.position_heading(s)
        assert math.isfinite(x) and math.isfinite(y) and math.isfinite(th)
        if prev is not None:
            dx = x - prev[0]
            dy = y - prev[1]
            assert dx * dx + dy * dy < 1e8  # arbitrary large cap to catch explosions
        prev = (x, y, th)


def test_bbox_m():
    """Test the bbox_m method."""
    track = StadiumTrack(total_length_m=1000.0, straight_fraction=0.30)
    width, height = track.bbox_m()

    # Check that bbox dimensions are reasonable
    assert width > 0
    assert height > 0
    assert width > height  # Stadium should be wider than tall
    assert width == track.straight_length_m + 2.0 * track.radius_m
    assert height == 2.0 * track.radius_m


def test_safe_speed_kmh():
    """Test the safe_speed_kmh method."""
    track = StadiumTrack(total_length_m=1000.0, straight_fraction=0.30)
    e, f = 0.08, 0.10

    safe_speed = track.safe_speed_kmh(e, f)

    # Check that safe speed is reasonable
    assert safe_speed > 0
    assert safe_speed < 200  # Should be reasonable for a track

    # Check the formula: V_safe = sqrt(127 R (e + f))
    expected = math.sqrt(127.0 * track.radius_m * (e + f))
    assert pytest.approx(safe_speed, rel=1e-12) == expected


if __name__ == "__main__":
    pytest.main([__file__])
