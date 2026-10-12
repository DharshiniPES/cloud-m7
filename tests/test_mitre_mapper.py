"""
Unit tests for MITRE ATT&CK Matrix Motif Mapping Engine.
"""

import networkx as nx
import pytest

from cloud_m7.fusion.mitre_mapper import MitreAttackMapper


def test_mitre_attack_motif_mapping():
    g = nx.DiGraph()

    # Step 1: Initial access on edge
    g.add_node(
        "edge_exploit",
        tier="Edge",
        host_id="sensor-01",
        event_type="Socket",
        action="connect",
        entity="firmware-listener",
        timestamp=100.0,
        is_attack=True,
    )

    # Step 2: Execution on edge
    g.add_node(
        "edge_sh_spawn",
        tier="Edge",
        host_id="sensor-01",
        event_type="Process",
        action="exec",
        entity="/bin/sh",
        timestamp=101.0,
        is_attack=True,
    )
    g.add_edge("edge_exploit", "edge_sh_spawn")

    # Step 3: Lateral movement to Fog MQTT
    g.add_node(
        "fog_mqtt_pivot",
        tier="Fog",
        host_id="gateway-01",
        event_type="Socket",
        action="connect",
        entity="mqtt-broker-1883",
        timestamp=104.0,
        is_attack=True,
    )
    g.add_edge("edge_sh_spawn", "fog_mqtt_pivot")

    # Step 4: Exfiltration to Cloud
    g.add_node(
        "cloud_s3_exfil",
        tier="Cloud",
        host_id="cloud-api",
        event_type="API",
        action="exfil_data",
        entity="s3://target-bucket",
        timestamp=110.0,
        is_attack=True,
    )
    g.add_edge("fog_mqtt_pivot", "cloud_s3_exfil")

    mapper = MitreAttackMapper()
    report = mapper.map_attack_graph(g)

    assert report.total_techniques_mapped >= 3
    assert "Initial Access" in report.tactics_observed
    assert "Execution" in report.tactics_observed
    assert "Lateral Movement" in report.tactics_observed
    assert "Exfiltration" in report.tactics_observed
    assert report.kill_chain_coverage_pct > 0.0
    assert "MITRE ATT&CK Cross-Tier Kill-Chain Progression" in report.progression_summary
