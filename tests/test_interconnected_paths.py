"""
Unit tests for the Interconnected Multi-Sensor Attack Graph Engine.
"""

import pytest
from cloud_m7.fusion.causal_graph import ProvenanceGraphEngine
from cloud_m7.fusion.interconnected_paths import InterconnectedAttackPathEngine
from cloud_m7.simulator.attack_scenario import MultiTierAttackSimulator


def test_multi_sensor_paths_to_cloud():
    # 1. Generate multi-vector telemetry (with 3 edge devices)
    sim = MultiTierAttackSimulator()
    events = sim.generate_full_simulation_dataset(benign_count=20, include_multi_vector=True)

    # 2. Ingest and fuse
    engine = ProvenanceGraphEngine(time_window_seconds=15.0)
    engine.add_events(events)
    engine.fuse_global_graph()

    # 3. Analyze interconnected multi-sensor attack paths
    path_engine = InterconnectedAttackPathEngine(engine)
    res = path_engine.analyze_interconnected_attack_graph()

    # Must detect multiple distinct originating sensors/actuators
    assert len(res.originating_sensors) >= 2
    assert "edge-sensor-01" in res.originating_sensors

    # Each originating sensor must have at least one causal trajectory to the cloud
    for sensor_id in res.originating_sensors:
        paths = res.sensor_paths[sensor_id]
        assert len(paths) >= 1
        assert paths[0].hops >= 3
        assert "cloud-api-prod" in paths[0].traversed_hosts or "cloud-db-cluster" in paths[0].traversed_hosts

    # Induced subgraph should have interconnected nodes and edges
    assert res.total_interconnected_nodes > 10
    assert res.total_interconnected_edges > 10
    assert res.induced_attack_subgraph.number_of_nodes() == res.total_interconnected_nodes


def test_choke_point_containment_bottlenecks():
    sim = MultiTierAttackSimulator()
    events = sim.generate_full_simulation_dataset(benign_count=15, include_multi_vector=True)

    engine = ProvenanceGraphEngine(time_window_seconds=15.0)
    engine.add_events(events)
    engine.fuse_global_graph()

    path_engine = InterconnectedAttackPathEngine(engine)
    res = path_engine.analyze_interconnected_attack_graph()

    # Must detect choke-points on Fog tier
    assert len(res.choke_points) > 0

    # Top choke-point should have high containment efficiency (severs >= 50% of paths)
    top_choke = res.choke_points[0]
    assert top_choke.containment_efficiency_pct >= 50.0
    assert top_choke.tier in ["Fog", "Cloud"]
    assert "CRITICAL CHOKE-POINT" in top_choke.mitigation_recommendation
