"""
Interconnected Multi-Sensor Attack Graph & Choke-Point Analysis Engine.

Constructs an interconnected attack provenance graph showing how disparate
compromised edge devices/sensors converge through intermediate fog layers
to reach target cloud assets.

Key Capabilities:
    1. Multi-Source to Target Pathfinding: Traces all active causal trajectories
       from each individual edge sensor to cloud endpoints.
    2. Convergence Choke-Point Detection: Identifies critical articulation nodes
       and network bridges (cut-vertices) whose containment isolates all edge
       attackers from the cloud.
    3. Containment Efficiency Index (CEI): Quantifies the containment value of
       each defensive mitigation point.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx

from cloud_m7.fusion.causal_graph import ProvenanceGraphEngine
from cloud_m7.schema.types import TierType


@dataclass
class SensorAttackPath:
    """Represents a causal attack trajectory originating from a specific edge device."""
    sensor_id: str
    entry_node: str
    target_node: str
    path_nodes: List[str]
    hops: int
    traversed_hosts: List[str]
    path_description: str


@dataclass
class ChokePoint:
    """A critical convergence bottleneck in the multi-sensor attack graph."""
    node_id: str
    tier: str
    host_id: str
    action: str
    entity: str
    paths_severed_count: int
    total_paths_count: int
    containment_efficiency_pct: float
    is_cut_vertex: bool
    mitigation_recommendation: str


@dataclass
class InterconnectedAttackGraphResult:
    """Complete multi-sensor interconnected attack graph analysis."""
    originating_sensors: List[str]
    total_interconnected_nodes: int
    total_interconnected_edges: int
    sensor_paths: Dict[str, List[SensorAttackPath]]
    choke_points: List[ChokePoint]
    induced_attack_subgraph: nx.DiGraph


class InterconnectedAttackPathEngine:
    """
    Analyzes convergent multi-device attack trajectories across Edge, Fog, and Cloud.
    """

    def __init__(self, engine: ProvenanceGraphEngine):
        self.engine = engine
        self.graph = engine.global_graph

    def analyze_interconnected_attack_graph(
        self,
        cloud_target_uuid: Optional[str] = None,
    ) -> InterconnectedAttackGraphResult:
        """
        Extracts interconnected attack paths from all active edge sensors to cloud target,
        and computes choke-point containment bottlenecks.
        """
        if self.graph.number_of_nodes() == 0:
            self.graph = self.engine.fuse_global_graph()

        # 1. Identify target cloud alert if not provided
        if cloud_target_uuid is None:
            cloud_attack_nodes = [
                n for n, d in self.graph.nodes(data=True)
                if d.get("is_attack") and d.get("tier") == "Cloud"
            ]
            if not cloud_attack_nodes:
                cloud_attack_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("is_attack")]
            if not cloud_attack_nodes:
                empty_g = nx.DiGraph()
                return InterconnectedAttackGraphResult(
                    originating_sensors=[],
                    total_interconnected_nodes=0,
                    total_interconnected_edges=0,
                    sensor_paths={},
                    choke_points=[],
                    induced_attack_subgraph=empty_g,
                )
            cloud_target_uuid = max(
                cloud_attack_nodes, key=lambda n: self.graph.nodes[n].get("timestamp", 0)
            )

        # 2. Identify all attack root nodes on Edge devices
        causal_ancestors = nx.ancestors(self.graph, cloud_target_uuid)
        causal_ancestors.add(cloud_target_uuid)

        edge_attack_roots = []
        for n in causal_ancestors:
            data = self.graph.nodes[n]
            if data.get("tier") == "Edge" and data.get("is_attack"):
                # Root condition: no attack predecessors
                preds = [p for p in self.graph.predecessors(n) if self.graph.nodes[p].get("is_attack")]
                if len(preds) == 0:
                    edge_attack_roots.append(n)

        # If no strict 0-predecessor root, fallback to all edge attack nodes
        if not edge_attack_roots:
            edge_attack_roots = [
                n for n in causal_ancestors
                if self.graph.nodes[n].get("tier") == "Edge" and self.graph.nodes[n].get("is_attack")
            ]

        # 3. Find paths from each edge sensor to cloud target
        sensor_paths_dict: Dict[str, List[SensorAttackPath]] = {}
        all_path_nodes: Set[str] = set()
        all_path_edges: Set[Tuple[str, str]] = set()

        for root in edge_attack_roots:
            root_data = self.graph.nodes[root]
            sensor_id = root_data.get("host_id", "unknown-edge-device")

            try:
                # Find all simple paths (or shortest paths) from this sensor to cloud target
                paths = list(nx.all_simple_paths(self.graph, source=root, target=cloud_target_uuid, cutoff=16))
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                paths = []

            if not paths and nx.has_path(self.graph, root, cloud_target_uuid):
                paths = [nx.shortest_path(self.graph, source=root, target=cloud_target_uuid)]

            sensor_trajectories = []
            for path in paths:
                all_path_nodes.update(path)
                for i in range(len(path) - 1):
                    all_path_edges.add((path[i], path[i + 1]))

                hosts_in_path = []
                for node_id in path:
                    h = self.graph.nodes[node_id].get("host_id", "")
                    if h and (not hosts_in_path or hosts_in_path[-1] != h):
                        hosts_in_path.append(h)

                desc = f"Trajectory from {sensor_id} via {' -> '.join(hosts_in_path)}"
                sensor_trajectories.append(
                    SensorAttackPath(
                        sensor_id=sensor_id,
                        entry_node=root,
                        target_node=cloud_target_uuid,
                        path_nodes=path,
                        hops=len(path),
                        traversed_hosts=hosts_in_path,
                        path_description=desc,
                    )
                )

            if sensor_trajectories:
                sensor_paths_dict[sensor_id] = sensor_trajectories

        # 4. Construct Induced Interconnected Attack Subgraph
        induced_subgraph = self.graph.subgraph(all_path_nodes).copy()

        # 5. Bottleneck & Choke-Point Analysis
        total_unique_paths = sum(len(p_list) for p_list in sensor_paths_dict.values())
        choke_points: List[ChokePoint] = []

        if total_unique_paths > 0:
            # Check intermediate nodes (excluding source roots and final target)
            intermediate_nodes = [
                n for n in all_path_nodes if n != cloud_target_uuid and n not in edge_attack_roots
            ]

            for node in intermediate_nodes:
                data = self.graph.nodes[node]
                # Count how many sensor paths pass through this node
                severed_count = 0
                for s_id, p_list in sensor_paths_dict.items():
                    for p in p_list:
                        if node in p.path_nodes:
                            severed_count += 1

                efficiency_pct = round((severed_count / total_unique_paths) * 100.0, 1)

                # Check if it acts as an articulation cut-point in the undirected projection
                is_cut = False
                temp_g = induced_subgraph.copy()
                temp_g.remove_node(node)
                # If removing this node disconnects any edge root from target
                paths_still_exist = any(
                    nx.has_path(temp_g, r, cloud_target_uuid)
                    for r in edge_attack_roots if temp_g.has_node(r) and temp_g.has_node(cloud_target_uuid)
                )
                if not paths_still_exist and len(edge_attack_roots) > 0:
                    is_cut = True

                # Only report nodes with meaningful containment value (>= 50% or cut-point)
                if efficiency_pct >= 50.0 or is_cut:
                    mitigation = (
                        f"CRITICAL CHOKE-POINT: Isolate host '{data.get('host_id')}' or terminate "
                        f"{data.get('event_type')} '{data.get('action')}' on {data.get('entity')} to sever "
                        f"{efficiency_pct}% of cross-tier attack paths."
                    )
                    choke_points.append(
                        ChokePoint(
                            node_id=node,
                            tier=data.get("tier", "Unknown"),
                            host_id=data.get("host_id", "Unknown"),
                            action=data.get("action", "activity"),
                            entity=data.get("entity", "unknown"),
                            paths_severed_count=severed_count,
                            total_paths_count=total_unique_paths,
                            containment_efficiency_pct=efficiency_pct,
                            is_cut_vertex=is_cut,
                            mitigation_recommendation=mitigation,
                        )
                    )

            # Sort choke points by containment efficiency descending
            choke_points.sort(key=lambda cp: cp.containment_efficiency_pct, reverse=True)

        return InterconnectedAttackGraphResult(
            originating_sensors=list(sensor_paths_dict.keys()),
            total_interconnected_nodes=len(all_path_nodes),
            total_interconnected_edges=len(all_path_edges),
            sensor_paths=sensor_paths_dict,
            choke_points=choke_points,
            induced_attack_subgraph=induced_subgraph,
        )
