"""
Multi-Objective Cost Model for CLOUD-M7 Tier-Adaptive Placement.

Mathematical Specification (Equation 2):
    min_x J(x) = alpha * Lat(x) + beta * BW(x) + gamma * Priv(x) + delta * Cost(x)
    subject to C_edge <= C_max

Where:
    - x = {x_1, ..., x_m} : forensic task assignments, x_k in {Edge, Fog, Cloud}
    - Lat(x) : End-to-end processing & network round-trip latency (ms)
    - BW(x)  : Total cross-tier network bandwidth consumed (KB/s or MB)
    - Priv(x): Forensic privacy / data exposure risk penalty
    - Cost(x): Monetary cloud and infrastructural resource cost ($)
    - C_edge : Aggregate CPU and memory compute footprint consumed on edge nodes
    - C_max  : Maximum allowable compute threshold on edge devices
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from cloud_m7.schema.types import TierType


class TaskType(str, Enum):
    EVENT_CAPTURE = "EventCapture"
    PRIVACY_FILTER = "PrivacyFilter"
    GRAPH_REDUCTION = "GraphReduction"
    CROSS_TIER_FUSION = "CrossTierFusion"
    CAUSAL_ANALYTICS = "CausalAnalytics"
    LONG_TERM_STORAGE = "LongTermStorage"


@dataclass
class ForensicTask:
    """Represents a forensic pipeline stage to be assigned to a tier."""
    name: TaskType
    required_cpu_mcore: float  # e.g. in millicores (1000 = 1 CPU core)
    required_memory_mb: float  # RAM in Megabytes
    raw_event_rate_per_sec: int  # event generation rate
    event_payload_bytes: int = 512


@dataclass
class MultiObjectiveWeights:
    """Weights for the multi-objective optimization function."""
    alpha: float = 0.35  # Latency weight
    beta: float = 0.35   # Bandwidth weight
    gamma: float = 0.15  # Privacy weight
    delta: float = 0.15  # Infrastructure monetary cost weight

    def __post_init__(self):
        total = self.alpha + self.beta + self.gamma + self.delta
        if abs(total - 1.0) > 1e-4:
            # Normalize to sum to 1.0
            self.alpha /= total
            self.beta /= total
            self.gamma /= total
            self.delta /= total


@dataclass
class PlacementMetrics:
    """Evaluated system metrics for a given placement assignment."""
    latency_ms: float
    bandwidth_kbps: float
    privacy_risk_score: float
    monetary_cost_usd_per_day: float
    edge_cpu_used_mcore: float
    edge_mem_used_mb: float
    total_cost_j: float
    is_feasible: bool
    violation_reason: Optional[str] = None
