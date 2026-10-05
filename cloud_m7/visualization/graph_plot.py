"""
Publication-Quality Provenance Graph Visualization for CLOUD-M7.

Renders multi-tier DAGs across Edge, Fog, and Cloud layers with
highlighted attack path causal flows.
"""

from typing import Dict, List, Optional, Set, Tuple
import matplotlib
matplotlib.use("Agg")  # Headless backend for reliable server/script rendering
import matplotlib.pyplot as plt
import networkx as nx

from cloud_m7.fusion.attack_path import AttackPathResult
from cloud_m7.fusion.causal_graph import ProvenanceGraphEngine


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
        if attack_result:
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

        if attack_result:
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
