"""
Causal Bridge Imputation Engine for Lossy Edge-Fog-Cloud Networks.

Problem:
    In real-world Edge-Fog environments (e.g. lossy wireless links, LoRaWAN,
    cellular IoT, or intermittent gateway dropouts), telemetry packets are
    frequently dropped. When an intermediate network event or audit log is lost,
    standard backward/forward provenance graph slicing gets severed, creating
    disconnected causal graph partitions and concealing the true attack path.

Solution (Causal Bridge Imputation):
    1. Identifies severed causal frontiers across tier boundaries.
    2. Evaluates candidate bridging transitions (u in Tier_A, v in Tier_B) using
       a multi-factor probabilistic confidence metric:
           P(bridge(u, v)) = alpha * exp(-|tau_v - tau_u| / sigma_t)
                           + beta * Sim_endpoint(u, v)
                           + gamma * Sim_lineage(u, v)
    3. Imputes synthetic causal bridges (u -> v) with provenance metadata and
       confidence scores when P >= theta_threshold, repairing the attack path.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx

from cloud_m7.fusion.causal_graph import ProvenanceGraphEngine
from cloud_m7.schema.types import TierType


@dataclass
class ImputedBridgeEdge:
    """Represents a synthetically imputed causal transition edge."""
    source_uuid: str
    target_uuid: str
    source_tier: str
    target_tier: str
    source_host: str
    target_host: str
    time_delta: float
    endpoint_similarity: float
    confidence_score: float
    imputation_rationale: str


@dataclass
class CausalBridgeResult:
    """Summary result of the causal bridge imputation process."""
    severed_components_detected: int
    imputed_bridges_count: int
    repaired_attack_paths_count: int
    imputed_bridges: List[ImputedBridgeEdge]
    repaired_graph: nx.DiGraph


class CausalBridgeImputer:
    """
    Imputes missing causal transitions across tier boundaries in lossy network environments.
    """

    def __init__(
        self,
        max_time_window_sec: float = 30.0,
        sigma_t: float = 5.0,
        confidence_threshold: float = 0.65,
        alpha_time: float = 0.4,
        beta_endpoint: float = 0.4,
        gamma_lineage: float = 0.2,
    ):
        self.max_time_window = max_time_window_sec
        self.sigma_t = sigma_t
        self.confidence_threshold = confidence_threshold
        self.alpha = alpha_time
        self.beta = beta_endpoint
        self.gamma = gamma_lineage

    def compute_endpoint_similarity(self, u_data: Dict[str, Any], v_data: Dict[str, Any]) -> float:
        """
        Computes network endpoint alignment score between source event u and target event v.
        """
        score = 0.0
        u_dst_ip = u_data.get("dst_ip", "")
        v_src_ip = v_data.get("src_ip", "")
        v_host = v_data.get("host_id", "")
        u_host = u_data.get("host_id", "")

        # Check if destination IP of u matches source IP or host ID of v
        if u_dst_ip and (u_dst_ip in v_src_ip or u_dst_ip in v_host or v_src_ip in u_dst_ip):
            score += 0.6
        elif u_data.get("tier") != v_data.get("tier"):
            # Adjacent tier transition heuristic
            score += 0.3

        # Port and protocol alignment
        u_proto = u_data.get("protocol", "TCP")
        v_proto = v_data.get("protocol", "TCP")
        if u_proto and v_proto and u_proto.upper() == v_proto.upper():
            score += 0.2

        u_dst_port = u_data.get("dst_port", 0)
        v_dst_port = v_data.get("dst_port", 0)
        if u_dst_port and v_dst_port and u_dst_port == v_dst_port:
            score += 0.2

        return min(score, 1.0)

    def compute_lineage_similarity(self, u_data: Dict[str, Any], v_data: Dict[str, Any]) -> float:
        """
        Computes behavioral and semantic compatibility between events u and v.
        """
        score = 0.3  # Base structural compatibility
        # If both are marked as attack telemetry
        if u_data.get("is_attack") and v_data.get("is_attack"):
            score += 0.5
        # If event involves socket communication or process execution
        if u_data.get("event_type") in ["Socket", "API"] or v_data.get("event_type") in ["Socket", "Process"]:
            score += 0.2
        return min(score, 1.0)

    def impute_missing_bridges(
        self,
        graph: nx.DiGraph,
        cloud_target_uuid: Optional[str] = None,
    ) -> CausalBridgeResult:
        """
        Scans graph for disconnected attack nodes across tiers and imputes missing causal bridges.
        """
        repaired_g = graph.copy()

        # Identify target cloud alert
        if cloud_target_uuid is None:
            attack_nodes = [n for n, d in repaired_g.nodes(data=True) if d.get("is_attack")]
            cloud_attack = [n for n in attack_nodes if repaired_g.nodes[n].get("tier") == "Cloud"]
            cloud_target_uuid = max(
                cloud_attack if cloud_attack else attack_nodes,
                key=lambda n: repaired_g.nodes[n].get("timestamp", 0),
                default=None,
            )

        if cloud_target_uuid is None:
            return CausalBridgeResult(
                severed_components_detected=0,
                imputed_bridges_count=0,
                repaired_attack_paths_count=0,
                imputed_bridges=[],
                repaired_graph=repaired_g,
            )

        # Find all edge attack nodes
        edge_attack_nodes = [
            n for n, d in repaired_g.nodes(data=True)
            if d.get("tier") == "Edge" and d.get("is_attack")
        ]

        # Check which edge attack nodes currently have NO path to cloud target (severed)
        severed_edge_nodes = [
            n for n in edge_attack_nodes
            if not nx.has_path(repaired_g, n, cloud_target_uuid)
        ]

        imputed_bridges: List[ImputedBridgeEdge] = []
        tier_hierarchy = {"Edge": 1, "Fog": 2, "Cloud": 3}

        # For each severed edge node, find candidate intermediate Fog or Cloud nodes
        for u in severed_edge_nodes:
            u_data = repaired_g.nodes[u]
            u_time = u_data.get("timestamp", 0.0)
            u_tier = u_data.get("tier", "Edge")

            best_candidate: Optional[Tuple[str, float, ImputedBridgeEdge]] = None

            # Look for downstream candidate nodes in higher tiers that occurred after u
            for v, v_data in repaired_g.nodes(data=True):
                v_tier = v_data.get("tier", "Cloud")
                v_time = v_data.get("timestamp", 0.0)

                # Causal ordering: v must occur strictly after u within max_time_window
                delta_t = v_time - u_time
                if delta_t <= 0.0 or delta_t > self.max_time_window:
                    continue

                # Must move upward or laterally in tier hierarchy
                if tier_hierarchy.get(v_tier, 0) < tier_hierarchy.get(u_tier, 0):
                    continue

                # Candidate must be able to reach cloud target (or be the cloud target)
                if v != cloud_target_uuid and not nx.has_path(repaired_g, v, cloud_target_uuid):
                    continue

                # Compute components of confidence score
                time_decay = math.exp(-delta_t / self.sigma_t)
                sim_endpoint = self.compute_endpoint_similarity(u_data, v_data)
                sim_lineage = self.compute_lineage_similarity(u_data, v_data)

                confidence = (
                    self.alpha * time_decay
                    + self.beta * sim_endpoint
                    + self.gamma * sim_lineage
                )

                if confidence >= self.confidence_threshold:
                    if best_candidate is None or confidence > best_candidate[1]:
                        rationale = (
                            f"Imputed bridge: {u_tier} ({u_data.get('host_id')}) -> "
                            f"{v_tier} ({v_data.get('host_id')}) [Delta_t={round(delta_t, 2)}s, "
                            f"EndpointSim={round(sim_endpoint, 2)}, Conf={round(confidence, 3)}]"
                        )
                        bridge = ImputedBridgeEdge(
                            source_uuid=u,
                            target_uuid=v,
                            source_tier=u_tier,
                            target_tier=v_tier,
                            source_host=u_data.get("host_id", ""),
                            target_host=v_data.get("host_id", ""),
                            time_delta=delta_t,
                            endpoint_similarity=sim_endpoint,
                            confidence_score=round(confidence, 3),
                            imputation_rationale=rationale,
                        )
                        best_candidate = (v, confidence, bridge)

            if best_candidate:
                v_node, conf, bridge_obj = best_candidate
                # Add imputed edge to repaired graph
                repaired_g.add_edge(
                    u,
                    v_node,
                    relation="IMPUTED_CROSS_TIER_BRIDGE",
                    confidence=conf,
                    imputed=True,
                )
                imputed_bridges.append(bridge_obj)

        # Count newly restored paths
        repaired_paths_count = sum(
            1 for n in severed_edge_nodes if nx.has_path(repaired_g, n, cloud_target_uuid)
        )

        return CausalBridgeResult(
            severed_components_detected=len(severed_edge_nodes),
            imputed_bridges_count=len(imputed_bridges),
            repaired_attack_paths_count=repaired_paths_count,
            imputed_bridges=imputed_bridges,
            repaired_graph=repaired_g,
        )
