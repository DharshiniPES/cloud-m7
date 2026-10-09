"""
Publication-Quality Provenance Graph Visualization for CLOUD-M7.

Renders multi-tier DAGs across Edge, Fog, and Cloud layers with
highlighted attack path causal flows.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import matplotlib
matplotlib.use("Agg")  # Headless backend for reliable server/script rendering
import matplotlib.pyplot as plt
import networkx as nx

from cloud_m7.fusion.attack_path import AttackPathResult
from cloud_m7.fusion.causal_graph import ProvenanceGraphEngine
from cloud_m7.fusion.iterative_discovery import IterativeDiscoveryResult


class Visualizer:
    """
    Renders multi-tier provenance graphs and attack reconstruction paths.
    """

    def __init__(self, engine: ProvenanceGraphEngine):
        self.engine = engine
        self.graph = engine.global_graph

    def render_attack_graph(
        self,
        output_filepath: str,
        attack_result: Optional[AttackPathResult] = None,
        iterative_result: Optional[IterativeDiscoveryResult] = None,
        title: str = "CLOUD-M7: Cross-Tier Causal Attack-Path Reconstruction",
    ) -> str:
        """
        Generates and saves a publication-quality diagram showing multi-tier nodes,
        cross-tier socket correlations, and highlighted attack trajectory.
        """
        if self.graph.number_of_nodes() == 0:
            self.graph = self.engine.fuse_global_graph()

        plt.figure(figsize=(16, 9), dpi=300)

        # 1. Define tiered layout coordinates
        pos: Dict[str, Tuple[float, float]] = {}
        tier_nodes = {"Edge": [], "Fog": [], "Cloud": []}

        for n, data in self.graph.nodes(data=True):
            tier = data.get("tier", "Edge")
            tier_nodes.setdefault(tier, []).append(n)

        # Sort each tier's nodes by timestamp for clean vertical flow
        for tier, nodes in tier_nodes.items():
            nodes.sort(key=lambda n: self.graph.nodes[n].get("timestamp", 0))

        tier_base_x = {"Edge": 1.8, "Fog": 5.0, "Cloud": 8.2}

        # Identify attack node set early for positioning
        attack_node_set_for_pos: Set[str] = set()
        if iterative_result:
            attack_node_set_for_pos = set(iterative_result.all_attack_nodes)
        elif attack_result:
            attack_node_set_for_pos = {s.uuid for s in attack_result.attack_steps}

        for tier, nodes in tier_nodes.items():
            base_x = tier_base_x.get(tier, 5.0)
            count = len(nodes)
            for i, n in enumerate(nodes):
                # Spread vertically between 1.2 and 8.8
                y = 1.2 + (7.6 * (i + 1) / (count + 1)) if count > 0 else 5.0
                # Separate benign nodes to the left, attack nodes to the right of each column
                if n in attack_node_set_for_pos:
                    x = base_x + 0.55
                else:
                    x = base_x - 0.55
                pos[n] = (x, y)

        # 2. Draw Tier Background Zones
        plt.axvspan(0.5, 3.2, color="#E8F5E9", alpha=0.5, label="Edge Tier (Devices/IoT)")
        plt.axvspan(3.3, 6.7, color="#FFF3E0", alpha=0.5, label="Fog Tier (Gateways/Clusters)")
        plt.axvspan(6.8, 9.5, color="#EDE7F6", alpha=0.5, label="Cloud Tier (Data Centers)")

        # 3. Determine attack path elements
        attack_node_set: Set[str] = set()
        attack_edge_set: Set[Tuple[str, str]] = set()

        if iterative_result:
            attack_node_set = set(iterative_result.all_attack_nodes)
            attack_edge_set = set(iterative_result.all_attack_edges)
        elif attack_result:
            path_uuids = [step.uuid for step in attack_result.attack_steps]
            attack_node_set = set(path_uuids)
            for i in range(len(path_uuids) - 1):
                attack_edge_set.add((path_uuids[i], path_uuids[i + 1]))

        # 4. Partition nodes for custom coloring
        benign_nodes = [n for n in self.graph.nodes() if n not in attack_node_set]
        attack_nodes = [n for n in self.graph.nodes() if n in attack_node_set]

        # Draw Benign nodes
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            nodelist=benign_nodes,
            node_color="#90CAF9",
            node_size=500,
            alpha=0.6,
            edgecolors="#1565C0",
            linewidths=1.2,
        )

        # Draw Malicious / Attack nodes
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            nodelist=attack_nodes,
            node_color="#E53935",
            node_size=750,
            alpha=0.95,
            edgecolors="#B71C1C",
            linewidths=2.5,
        )

        # 5. Partition edges
        benign_edges = [e for e in self.graph.edges() if e not in attack_edge_set]
        attack_edges = [e for e in self.graph.edges() if e in attack_edge_set]

        # Draw Benign edges
        nx.draw_networkx_edges(
            self.graph,
            pos,
            edgelist=benign_edges,
            edge_color="#B0BEC5",
            arrows=True,
            arrowsize=12,
            arrowstyle="-|>",
            width=1.0,
            alpha=0.5,
        )

        # Draw Malicious / Attack causal edges
        nx.draw_networkx_edges(
            self.graph,
            pos,
            edgelist=attack_edges,
            edge_color="#D50000",
            arrows=True,
            arrowsize=20,
            arrowstyle="-|>",
            width=3.2,
            connectionstyle="arc3,rad=0.08",
        )

        # 6. Add Node Labels for Attack Steps
        labels = {}
        for n, data in self.graph.nodes(data=True):
            if n in attack_node_set and attack_result:
                # Find step order
                for s in attack_result.attack_steps:
                    if s.uuid == n:
                        labels[n] = f"Step {s.order}\n{s.action}"
                        break
            elif n in attack_node_set and iterative_result:
                action = data.get("action", "")
                labels[n] = f"Atk: {action}"
            else:
                action = data.get("action", "")
                labels[n] = action if len(action) <= 10 else action[:8] + ".."

        nx.draw_networkx_labels(
            self.graph,
            pos,
            labels=labels,
            font_size=8,
            font_family="sans-serif",
            font_weight="bold",
        )

        plt.title(
            title,
            fontsize=15,
            fontweight="bold",
            pad=18,
            color="#212121",
        )
        plt.xlim(0.0, 10.0)
        plt.ylim(0.0, 10.0)
        plt.axis("off")
        plt.legend(loc="upper left", framealpha=0.9, fontsize=10)
        plt.tight_layout()

        plt.savefig(output_filepath, bbox_inches="tight")
        plt.close()

        return output_filepath

    def render_interconnected_graph(
        self,
        output_filepath: str,
        interconnected_result: Any,
        title: str = "CLOUD-M7: Interconnected Multi-Sensor Attack Paths & Choke-Point Analysis",
    ) -> str:
        """
        Renders the convergent multi-sensor attack graph, highlighting distinct
        originating edge devices and the critical Fog convergence choke points.
        """
        subgraph = interconnected_result.induced_attack_subgraph
        if subgraph.number_of_nodes() == 0:
            return output_filepath

        plt.figure(figsize=(18, 10), dpi=300)

        # 1. Custom layout grouping edge sensors vertically
        pos: Dict[str, Tuple[float, float]] = {}
        sensor_nodes: Dict[str, List[str]] = {}
        fog_nodes: List[str] = []
        cloud_nodes: List[str] = []

        choke_node_ids = {cp.node_id for cp in interconnected_result.choke_points if cp.containment_efficiency_pct >= 80.0}

        for n, data in subgraph.nodes(data=True):
            tier = data.get("tier", "Edge")
            host = data.get("host_id", "")
            if tier == "Edge":
                sensor_nodes.setdefault(host, []).append(n)
            elif tier == "Fog":
                fog_nodes.append(n)
            else:
                cloud_nodes.append(n)

        # Layout Edge devices in distinct vertical bands
        sensor_list = sorted(list(sensor_nodes.keys()))
        num_sensors = max(1, len(sensor_list))
        for s_idx, s_host in enumerate(sensor_list):
            nodes = sorted(sensor_nodes[s_host], key=lambda x: subgraph.nodes[x].get("timestamp", 0))
            band_y_min = 1.0 + (8.0 * s_idx / num_sensors)
            band_y_max = 1.0 + (8.0 * (s_idx + 1) / num_sensors) - 0.5
            count = len(nodes)
            for i, n in enumerate(nodes):
                y = band_y_min + ((band_y_max - band_y_min) * (i + 1) / (count + 1)) if count > 0 else (band_y_min + band_y_max) / 2
                x = 1.5 + (0.4 * (i % 2))
                pos[n] = (x, y)

        # Layout Fog nodes in center
        fog_nodes = sorted(fog_nodes, key=lambda x: subgraph.nodes[x].get("timestamp", 0))
        fog_count = len(fog_nodes)
        for i, n in enumerate(fog_nodes):
            y = 1.5 + (7.0 * (i + 1) / (fog_count + 1)) if fog_count > 0 else 5.0
            pos[n] = (5.0, y)

        # Layout Cloud nodes on right
        cloud_nodes = sorted(cloud_nodes, key=lambda x: subgraph.nodes[x].get("timestamp", 0))
        cloud_count = len(cloud_nodes)
        for i, n in enumerate(cloud_nodes):
            y = 2.0 + (6.0 * (i + 1) / (cloud_count + 1)) if cloud_count > 0 else 5.0
            pos[n] = (8.5, y)

        # 2. Draw Tier Background Zones
        plt.axvspan(0.5, 3.2, color="#E8F5E9", alpha=0.5, label="Edge Devices / Sensor Grid")
        plt.axvspan(3.3, 6.7, color="#FFF3E0", alpha=0.5, label="Fog Gateways (Convergence Layer)")
        plt.axvspan(6.8, 9.5, color="#EDE7F6", alpha=0.5, label="Centralized Cloud Datastore")

        # 3. Draw Nodes with distinct colors for Choke Points vs regular attack nodes
        regular_nodes = [n for n in subgraph.nodes() if n not in choke_node_ids]
        choke_nodes = [n for n in subgraph.nodes() if n in choke_node_ids]

        # Draw regular attack nodes
        nx.draw_networkx_nodes(
            subgraph,
            pos,
            nodelist=regular_nodes,
            node_color="#E53935",
            node_size=650,
            alpha=0.9,
            edgecolors="#B71C1C",
            linewidths=2.0,
        )

        # Draw Choke-point articulation nodes with bright highlight
        if choke_nodes:
            nx.draw_networkx_nodes(
                subgraph,
                pos,
                nodelist=choke_nodes,
                node_color="#FFD600",
                node_size=1000,
                alpha=0.98,
                edgecolors="#E65100",
                linewidths=3.5,
            )

        # Draw directed causal edges
        nx.draw_networkx_edges(
            subgraph,
            pos,
            edgelist=list(subgraph.edges()),
            edge_color="#D50000",
            arrows=True,
            arrowsize=22,
            arrowstyle="-|>",
            width=2.8,
            connectionstyle="arc3,rad=0.06",
        )

        # Labels
        labels = {}
        for n, data in subgraph.nodes(data=True):
            action = data.get("action", "")
            host = data.get("host_id", "")
            if n in choke_node_ids:
                labels[n] = f"CHOKE-POINT\n{action}\n({host})"
            else:
                labels[n] = f"{host}\n{action}"

        nx.draw_networkx_labels(
            subgraph,
            pos,
            labels=labels,
            font_size=7.5,
            font_family="sans-serif",
            font_weight="bold",
        )

        plt.title(
            title,
            fontsize=15,
            fontweight="bold",
            pad=18,
            color="#212121",
        )
        plt.xlim(0.0, 10.0)
        plt.ylim(0.0, 10.0)
        plt.axis("off")
        plt.legend(loc="upper left", framealpha=0.9, fontsize=10)
        plt.tight_layout()

        plt.savefig(output_filepath, bbox_inches="tight")
        plt.close()

        return output_filepath
