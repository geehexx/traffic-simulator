"""Tests for track properties test."""

from __future__ import annotations


"""Tests for track properties test."""


import pytest

import math

import hypothesis.strategies as st
from hypothesis import given, settings

from traffic_sim.core.track import StadiumTrack


@given(
    L=st.floats(min_value=200.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    r=st.floats(min_value=0.0, max_value=0.9, allow_nan=False, allow_infinity=False),
)
@settings(deadline=None, max_examples=100)
def test_length_reconstructs(L, r):
    track = StadiumTrack(total_length_m=L, straight_fraction=r)
    R = track.radius_m
    S = track.straight_length_m
    L_recon = 2 * math.pi * R + 2 * S
    assert abs(L_recon - L) <= 1e-6 * max(1.0, L)


@given(
    V=st.floats(min_value=30.0, max_value=200.0),
    e=st.floats(min_value=0.0, max_value=0.12),
    f=st.floats(min_value=0.02, max_value=0.20),
)
@settings(deadline=None, max_examples=100)
def test_safe_speed_inverse(V, e, f):
    track = StadiumTrack(total_length_m=1000.0, straight_fraction=0.30)
    Rmin = track.safe_radius_min_m(V, e, f)
    Vsafe = (
        track.safe_speed_kmh(e, f)
        if abs(track.radius_m - Rmin) < 1e-9
        else math.sqrt(127.0 * Rmin * (e + f))
    )
    assert abs(Vsafe - V) <= 1e-8 * max(1.0, V)


if __name__ == "__main__":
    pytest.main([__file__])
