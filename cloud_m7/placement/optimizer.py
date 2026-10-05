"""
Optimization Engine for Tier-Adaptive Placement.

Solves the multi-objective optimization problem:
    min_x J(x) = alpha * Lat(x) + beta * BW(x) + gamma * Priv(x) + delta * Cost(x)
    subject to:
        C_edge_cpu <= C_max_cpu
        C_edge_mem <= C_max_mem

Compares CLOUD-M7 Adaptive Placement against traditional baselines:
    - Pure Cloud Forensics (centralized raw log shipping)
    - Host-Only / Edge-Only Forensics
"""

from typing import Dict, List, Tuple
from cloud_m7.schema.types import TierType
from cloud_m7.placement.cost_model import (
    ForensicTask,
    MultiObjectiveWeights,
    PlacementMetrics,
    TaskType,
)


class PlacementOptimizer:
    """
    Evaluates and determines optimal tier placement of forensic pipeline tasks.
    """

    def __init__(
        self,
        weights: MultiObjectiveWeights = MultiObjectiveWeights(),
        edge_max_cpu_mcore: float = 800.0,  # e.g., Raspberry Pi 4 limits
        edge_max_mem_mb: float = 512.0,
    ):
        self.weights = weights
        self.edge_max_cpu_mcore = edge_max_cpu_mcore
        self.edge_max_mem_mb = edge_max_mem_mb

        # Latency profiles between tiers (in ms)
        self.latency_matrix = {
            (TierType.EDGE, TierType.EDGE): 0.5,
            (TierType.EDGE, TierType.FOG): 12.0,
            (TierType.FOG, TierType.CLOUD): 65.0,
            (TierType.EDGE, TierType.CLOUD): 110.0,
            (TierType.FOG, TierType.FOG): 2.0,
            (TierType.CLOUD, TierType.CLOUD): 1.0,
        }

    def evaluate_placement(
        self,
        tasks: List[ForensicTask],
        assignment: Dict[TaskType, TierType],
    ) -> PlacementMetrics:
        """
        Computes multi-objective metrics for a specific assignment x.
        """
        total_lat = 0.0
        total_bw_kbps = 0.0
        privacy_penalty = 0.0
        monetary_cost = 0.0

        edge_cpu_used = 0.0
        edge_mem_used = 0.0

        raw_event_rate = max((t.raw_event_rate_per_sec for t in tasks), default=100)
        bytes_per_event = 512

        # 1. Resource usage check on Edge
        for task in tasks:
            assigned_tier = assignment.get(task.name, TierType.CLOUD)
            if assigned_tier == TierType.EDGE:
                edge_cpu_used += task.required_cpu_mcore
                edge_mem_used += task.required_memory_mb

        # Check constraint C_edge <= C_max
        is_feasible = True
        violation_reason = None
        if edge_cpu_used > self.edge_max_cpu_mcore:
            is_feasible = False
            violation_reason = f"Edge CPU exceeded: {edge_cpu_used} > {self.edge_max_cpu_mcore} mcores"
        elif edge_mem_used > self.edge_max_mem_mb:
            is_feasible = False
            violation_reason = f"Edge Memory exceeded: {edge_mem_used} > {self.edge_max_mem_mb} MB"

        # 2. Pipeline Stage Effects on Bandwidth, Latency, Privacy, and Cost
        # Filter placement determines raw bandwidth egress:
        filter_tier = assignment.get(TaskType.PRIVACY_FILTER, TierType.CLOUD)
        reduction_tier = assignment.get(TaskType.GRAPH_REDUCTION, TierType.FOG)
        storage_tier = assignment.get(TaskType.LONG_TERM_STORAGE, TierType.CLOUD)

        # Baseline raw bandwidth in KB/s
        raw_bw_kbps = (raw_event_rate * bytes_per_event) / 1024.0

        # Bandwidth calculation
        if filter_tier == TierType.EDGE:
            # 60% noise filtered out right at Edge
            egress_from_edge = raw_bw_kbps * 0.40
            privacy_penalty += 5.0  # minimal privacy risk (raw data never leaves)
        else:
            # Raw events stream over edge link
            egress_from_edge = raw_bw_kbps
            privacy_penalty += 45.0  # raw telemetry exposed over upstream network

        if reduction_tier == TierType.EDGE:
            # Subgraph reduction at edge further reduces by 50%
            egress_from_edge *= 0.50
            total_bw_kbps = egress_from_edge
            total_lat += 5.0
        elif reduction_tier == TierType.FOG:
            # Reduction happens at Fog node
            egress_from_fog = egress_from_edge * 0.35  # intermediate summarization
            total_bw_kbps = egress_from_edge + egress_from_fog
            total_lat += self.latency_matrix[(TierType.EDGE, TierType.FOG)] + 10.0
            privacy_penalty += 15.0
        else:  # Reduction on Cloud
            total_bw_kbps = egress_from_edge * 2.0
            total_lat += self.latency_matrix[(TierType.EDGE, TierType.CLOUD)] + 35.0
            privacy_penalty += 75.0

        # Causal analytics latency & cost
        analytics_tier = assignment.get(TaskType.CAUSAL_ANALYTICS, TierType.CLOUD)
        if analytics_tier == TierType.CLOUD:
            # Cloud has massive parallel processing: fast query execution, small network hop
            total_lat += 15.0
            monetary_cost += 12.50  # Cloud compute & storage cost ($/day)
        elif analytics_tier == TierType.FOG:
            total_lat += 45.0
            monetary_cost += 4.00
        else:
            total_lat += 120.0  # Constrained edge device runs slow graph traversal
            monetary_cost += 0.50

        # Normalized cost function:
        # Normalize each metric to roughly 0..100 scale
        norm_lat = min(100.0, total_lat / 2.0)
        norm_bw = min(100.0, total_bw_kbps / 10.0)
        norm_priv = min(100.0, privacy_penalty)
        norm_cost = min(100.0, monetary_cost * 4.0)

        total_cost_j = (
            self.weights.alpha * norm_lat
            + self.weights.beta * norm_bw
            + self.weights.gamma * norm_priv
            + self.weights.delta * norm_cost
        )

        return PlacementMetrics(
            latency_ms=round(total_lat, 2),
            bandwidth_kbps=round(total_bw_kbps, 2),
            privacy_risk_score=round(privacy_penalty, 2),
            monetary_cost_usd_per_day=round(monetary_cost, 2),
            edge_cpu_used_mcore=round(edge_cpu_used, 1),
            edge_mem_used_mb=round(edge_mem_used, 1),
            total_cost_j=round(total_cost_j, 2),
            is_feasible=is_feasible,
            violation_reason=violation_reason,
        )

    def find_optimal_placement(
        self, tasks: List[ForensicTask]
    ) -> Tuple[Dict[TaskType, TierType], PlacementMetrics]:
        """
        Explores placement search space across Edge, Fog, Cloud to find assignment
        minimizing J(x) while satisfying edge hardware constraints C_edge <= C_max.
        """
        # Event capture must originate at Edge for edge telemetry
        tier_options = [TierType.EDGE, TierType.FOG, TierType.CLOUD]
        
        best_assignment: Optional[Dict[TaskType, TierType]] = None
        best_metrics: Optional[PlacementMetrics] = None
        min_j = float("inf")

        # Configurable tasks: Filter, Reduction, Fusion, Analytics, Storage
        for filter_tier in [TierType.EDGE, TierType.FOG]:
            for red_tier in [TierType.EDGE, TierType.FOG, TierType.CLOUD]:
                for fusion_tier in [TierType.FOG, TierType.CLOUD]:
                    for analytics_tier in [TierType.FOG, TierType.CLOUD]:
                        candidate = {
                            TaskType.EVENT_CAPTURE: TierType.EDGE,
                            TaskType.PRIVACY_FILTER: filter_tier,
                            TaskType.GRAPH_REDUCTION: red_tier,
                            TaskType.CROSS_TIER_FUSION: fusion_tier,
                            TaskType.CAUSAL_ANALYTICS: analytics_tier,
                            TaskType.LONG_TERM_STORAGE: TierType.CLOUD,
                        }
                        metrics = self.evaluate_placement(tasks, candidate)
                        if metrics.is_feasible and metrics.total_cost_j < min_j:
                            min_j = metrics.total_cost_j
                            best_assignment = candidate
                            best_metrics = metrics

        if best_assignment is None or best_metrics is None:
            # Fallback to safe default
            best_assignment = {
                TaskType.EVENT_CAPTURE: TierType.EDGE,
                TaskType.PRIVACY_FILTER: TierType.EDGE,
                TaskType.GRAPH_REDUCTION: TierType.FOG,
                TaskType.CROSS_TIER_FUSION: TierType.CLOUD,
                TaskType.CAUSAL_ANALYTICS: TierType.CLOUD,
                TaskType.LONG_TERM_STORAGE: TierType.CLOUD,
            }
            best_metrics = self.evaluate_placement(tasks, best_assignment)

        return best_assignment, best_metrics
