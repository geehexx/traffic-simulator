import numpy as np
from traffic_sim.core.physics_numpy import PhysicsEngineNumpy


def test_physics_engine_numpy_basic():
    # 2 vehicles: [x, y, vx, vy]
    initial_state = np.array(
        [
            [0.0, 0.0, 10.0, 0.0],
            [5.0, 0.0, 0.0, 0.0],
        ]
    )
    vehicle_specs = np.zeros((2, 1))  # Placeholder, not used yet
    engine = PhysicsEngineNumpy(vehicle_specs, initial_state)
    actions = np.zeros((2, 1))  # Placeholder, not used yet
    dt = 1.0
    state = engine.step(actions, dt)
    # Vehicle 0 should move 10 units in x, vehicle 1 should not move
    assert np.allclose(state[0, 0], 10.0)
    assert np.allclose(state[1, 0], 5.0)
    print("Basic NumPy physics engine test passed.")
