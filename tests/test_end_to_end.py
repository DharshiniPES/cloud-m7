"""
End-to-end integration test for the full CLOUD-M7 pipeline.
"""

from cloud_m7.fusion.attack_path import AttackPathReconstructor
from cloud_m7.fusion.causal_graph import ProvenanceGraphEngine
from cloud_m7.simulator.attack_scenario import MultiTierAttackSimulator


def test_end_to_end_attack_reconstruction():
    # 1. Generate full dataset (benign + multi-stage attack)
    sim = MultiTierAttackSimulator()
    events = sim.generate_full_simulation_dataset(benign_count=20)
    assert len(events) >= 30

    # 2. Ingest and fuse
    engine = ProvenanceGraphEngine(time_window_seconds=15.0)
    engine.add_events(events)
    g = engine.fuse_global_graph()

    assert g.number_of_nodes() == len(events)
    assert g.number_of_edges() > 0

    # 3. Reconstruct
    reconstructor = AttackPathReconstructor(engine)
    result = reconstructor.reconstruct_attack_path()

    assert result is not None
    assert result.path_length >= 5
    # Must span Edge, Fog, and Cloud tiers
    assert "Edge" in result.traversed_tiers
    assert "Fog" in result.traversed_tiers
    assert "Cloud" in result.traversed_tiers
    assert result.reduction_percentage > 50.0  # Successfully filtered benign noise
