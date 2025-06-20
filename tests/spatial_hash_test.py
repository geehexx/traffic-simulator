from __future__ import annotations


import pytest

import numpy as np
from traffic_sim.core.spatial_hash import spatial_hash_grid


def test_spatial_hash_grid_basic():
    positions = np.array([[0.1, 0.2], [1.5, 0.9], [2.2, 2.1], [0.9, 0.8], [2.0, 2.0]])
    cell_size = 1.0
    grid = spatial_hash_grid(positions, cell_size)
    # Check that all indices are present
    all_indices = sorted([i for indices in grid.values() for i in indices])
    assert all_indices == list(range(len(positions)))
    # Check that cells are correct
    assert sorted(grid[(0, 0)]) == [0, 3]
    assert grid[(1, 0)] == [1]
    assert sorted(grid[(2, 2)]) == [2, 4]
    print("Basic spatial hash grid test passed.")


if __name__ == "__main__":
    pytest.main([__file__])
