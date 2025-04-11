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
    eps = 1e-4
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


