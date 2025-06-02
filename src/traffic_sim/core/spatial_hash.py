import numpy as np
from typing import Dict, List, Tuple


def spatial_hash_grid(positions: np.ndarray, cell_size: float) -> Dict[Tuple[int, int], List[int]]:
    """
    Assigns each position to a grid cell for broadphase collision detection.
    Args:
        positions (np.ndarray): Nx2 array of (x, y) positions
        cell_size (float): Size of each grid cell
    Returns:
        Dict[Tuple[int, int], List[int]]: Mapping from cell to list of indices
    """
    grid: Dict[Tuple[int, int], List[int]] = {}
    for idx, pos in enumerate(positions):
        cell = (int(pos[0] // cell_size), int(pos[1] // cell_size))
        if cell not in grid:
            grid[cell] = []
        grid[cell].append(idx)
    return grid


# Test for spatial hash grid
if __name__ == "__main__":
    positions = np.array([[0.1, 0.2], [1.5, 0.9], [2.2, 2.1], [0.9, 0.8], [2.0, 2.0]])
    cell_size = 1.0
    grid = spatial_hash_grid(positions, cell_size)
    for cell, indices in grid.items():
        print(f"Cell {cell}: {indices}")
