"""
Unit tests for CLOUD-M7 Tier-Adaptive Placement Optimizer.
"""

from cloud_m7.placement.cost_model import (
    ForensicTask,
    MultiObjectiveWeights,
    TaskType,
)
from cloud_m7.placement.optimizer import PlacementOptimizer
from cloud_m7.schema.types import TierType


def test_placement_feasibility_constraint():
    optimizer = PlacementOptimizer(
        weights=MultiObjectiveWeights(),
        edge_max_cpu_mcore=300.0,
        edge_max_mem_mb=256.0,
    )
    # Tasks requiring heavy compute
    tasks = [
        ForensicTask(TaskType.EVENT_CAPTURE, required_cpu_mcore=100, required_memory_mb=64, raw_event_rate_per_sec=100),
        ForensicTask(TaskType.CAUSAL_ANALYTICS, required_cpu_mcore=500, required_memory_mb=1024, raw_event_rate_per_sec=100),
    ]

    # Placing CAUSAL_ANALYTICS on Edge should violate edge capacity constraints
    violating_assignment = {
        TaskType.EVENT_CAPTURE: TierType.EDGE,
        TaskType.CAUSAL_ANALYTICS: TierType.EDGE,
    }
    metrics = optimizer.evaluate_placement(tasks, violating_assignment)
    assert metrics.is_feasible is False
    assert "Edge CPU exceeded" in metrics.violation_reason or "Edge Memory exceeded" in metrics.violation_reason


def test_optimal_placement_discovery():
    optimizer = PlacementOptimizer()
    tasks = [
        ForensicTask(TaskType.EVENT_CAPTURE, required_cpu_mcore=150, required_memory_mb=64, raw_event_rate_per_sec=200),
        ForensicTask(TaskType.PRIVACY_FILTER, required_cpu_mcore=120, required_memory_mb=48, raw_event_rate_per_sec=200),
        ForensicTask(TaskType.GRAPH_REDUCTION, required_cpu_mcore=350, required_memory_mb=180, raw_event_rate_per_sec=100),
        ForensicTask(TaskType.CROSS_TIER_FUSION, required_cpu_mcore=600, required_memory_mb=512, raw_event_rate_per_sec=50),
        ForensicTask(TaskType.CAUSAL_ANALYTICS, required_cpu_mcore=1200, required_memory_mb=1024, raw_event_rate_per_sec=25),
        ForensicTask(TaskType.LONG_TERM_STORAGE, required_cpu_mcore=200, required_memory_mb=2048, raw_event_rate_per_sec=25),
    ]

    best_assignment, best_metrics = optimizer.find_optimal_placement(tasks)
    assert best_metrics.is_feasible is True
    # Verify filtering/reduction happens before deep cloud storage
    assert best_assignment[TaskType.EVENT_CAPTURE] == TierType.EDGE
    assert best_assignment[TaskType.LONG_TERM_STORAGE] == TierType.CLOUD
