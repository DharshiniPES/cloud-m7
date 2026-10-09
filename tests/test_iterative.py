"""
Unit tests for the Novel Iterative Multi-Root Forensic Discovery Engine.
"""

import pytest
from cloud_m7.fusion.causal_graph import ProvenanceGraphEngine
from cloud_m7.fusion.iterative_discovery import IterativeAttackDiscoveryEngine
from cloud_m7.simulator.attack_scenario import MultiTierAttackSimulator


def test_iterative_discovery_multi_vector():
    # 1. Generate multi-vector telemetry (Primary on edge-sensor-01 + Secondary on edge-sensor-02)
    sim = MultiTierAttackSimulator()
    events = sim.generate_full_simulation_dataset(benign_count=20, include_multi_vector=True)

    # 2. Ingest into graph engine
    engine = ProvenanceGraphEngine(time_window_seconds=15.0)
    engine.add_events(events)
    engine.fuse_global_graph()

    # 3. Run iterative discovery with hyperparameters
    iter_engine = IterativeAttackDiscoveryEngine(
        engine,
        max_iterations=5,
        impact_threshold_epsilon=5.0,  # 5% threshold
        causal_attenuation=0.85,
    )

    result = iter_engine.discover_all_attack_points()

    assert result.converged is True
    # Should run at least 2 iterations and discover both vectors
    assert len(result.discovered_vectors) >= 2
    assert result.total_iterations_run >= 2

    # Vector 1 should originate on edge-sensor-01
    v1 = result.discovered_vectors[0]
    assert v1.entry_host == "edge-sensor-01"
    assert v1.iteration == 1

    # Vector 2 should originate on edge-sensor-02
    v2 = result.discovered_vectors[1]
    assert v2.entry_host == "edge-sensor-02"
    assert v2.iteration == 2

    # Marginal impact gain in iteration 1 is 100%, iteration 2 is > 5%
    assert result.iteration_history[0].marginal_impact_gain_pct == 100.0
    assert result.iteration_history[1].marginal_impact_gain_pct > 0.0

    # Total impact score should be positive and non-zero
    assert result.total_impact_score > 0.0


def test_hyperparameter_max_iterations_ceiling():
    sim = MultiTierAttackSimulator()
    events = sim.generate_full_simulation_dataset(benign_count=10, include_multi_vector=True)

    engine = ProvenanceGraphEngine(time_window_seconds=15.0)
    engine.add_events(events)
    engine.fuse_global_graph()

    # Set max_iterations hyperparameter to strictly 1
    iter_engine = IterativeAttackDiscoveryEngine(
        engine,
        max_iterations=1,
        impact_threshold_epsilon=1.0,
    )

    result = iter_engine.discover_all_attack_points()

    # Must terminate after exactly 1 iteration
    assert result.total_iterations_run == 1
    assert len(result.discovered_vectors) == 1
    assert "max_iterations limit" in result.convergence_reason


def test_hyperparameter_epsilon_convergence():
    sim = MultiTierAttackSimulator()
    # Single attack vector only
    events = sim.generate_full_simulation_dataset(benign_count=15, include_multi_vector=False)

    engine = ProvenanceGraphEngine(time_window_seconds=15.0)
    engine.add_events(events)
    engine.fuse_global_graph()

    iter_engine = IterativeAttackDiscoveryEngine(
        engine,
        max_iterations=5,
        impact_threshold_epsilon=10.0,
    )

    result = iter_engine.discover_all_attack_points()

    # Since there's only 1 attack vector, it discovers Vector 1 in Iteration 1,
    # and converges in Iteration 2 because no further high-impact vectors exist
    assert result.converged is True
    assert len(result.discovered_vectors) == 1
    assert result.total_iterations_run <= 2
