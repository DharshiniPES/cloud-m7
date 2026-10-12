"""
Unit tests for Causal Bridge Imputation Engine.
"""

import networkx as nx
import pytest

from cloud_m7.fusion.causal_bridge import CausalBridgeImputer


def test_causal_bridge_imputation():
    # Construct a partitioned graph where edge attack is disconnected from cloud alert
    g = nx.DiGraph()

    # Edge attack node
    g.add_node(
        "edge_node_1",
        tier="Edge",
        host_id="sensor-01",
        event_type="Socket",
        action="connect",
        entity="10.0.1.5:1883",
        dst_ip="10.0.1.5",
        dst_port=1883,
        protocol="TCP",
        timestamp=100.0,
        is_attack=True,
    )

    # Intermediate fog node (part of attack, reaches cloud target)
    g.add_node(
        "fog_node_1",
        tier="Fog",
        host_id="gateway-01",
        event_type="Process",
        action="exec",
        entity="/usr/bin/python3",
        src_ip="10.0.1.5",
        timestamp=102.0,
        is_attack=True,
    )

    # Cloud target alert node
    g.add_node(
        "cloud_alert_1",
        tier="Cloud",
        host_id="cloud-api",
        event_type="API",
        action="exfil_data",
        entity="s3://target-bucket",
        timestamp=105.0,
        is_attack=True,
    )

    # Fog node connects to cloud target
    g.add_edge("fog_node_1", "cloud_alert_1", relation="FLOW")

    # Before imputation: No path exists from edge_node_1 to cloud_alert_1
    assert not nx.has_path(g, "edge_node_1", "cloud_alert_1")

    # Run Causal Bridge Imputation
    imputer = CausalBridgeImputer(
        max_time_window_sec=20.0,
        sigma_t=5.0,
        confidence_threshold=0.55,
    )
    result = imputer.impute_missing_bridges(g, cloud_target_uuid="cloud_alert_1")

    # Verification:
    assert result.severed_components_detected == 1
    assert result.imputed_bridges_count == 1
    assert result.repaired_attack_paths_count == 1
    assert len(result.imputed_bridges) == 1

    bridge = result.imputed_bridges[0]
    assert bridge.source_uuid == "edge_node_1"
    assert bridge.target_uuid == "fog_node_1"
    assert bridge.confidence_score >= 0.55

    # Graph is now connected from edge to cloud!
    assert nx.has_path(result.repaired_graph, "edge_node_1", "cloud_alert_1")
