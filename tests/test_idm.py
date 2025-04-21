from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def test_idm_braking_when_too_close():
    cfg = load_config()
    cfg["vehicles"]["count"] = 2
    sim = Simulation(cfg)
    # Place follower just behind leader with small gap and higher speed
    sim.vehicles[0].state.s_m = 0.0
    sim.vehicles[0].state.v_mps = 10.0
    sim.vehicles[1].state.s_m = 2.0  # small gap ahead (leader)
    sim.vehicles[1].state.v_mps = 0.5
    # Step the sim
    sim.step(0.2)
    # Expect follower acceleration to be negative (braking)
    assert sim.vehicles[0].state.a_mps2 < 0.0

