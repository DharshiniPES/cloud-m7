"""
Unit tests for Active Choke-Point Remediation and Policy Synthesis Engine.
"""

import pytest

from cloud_m7.fusion.active_remediation import (
    ActiveChokePointRemediator,
    RemediationMechanism,
)
from cloud_m7.fusion.interconnected_paths import ChokePoint


def test_active_remediation_synthesis():
    cp_network = ChokePoint(
        node_id="cp_fog_socket",
        tier="Fog",
        host_id="fog-gw-01",
        action="connect",
        entity="10.0.1.5:1883",
        paths_severed_count=4,
        total_paths_count=4,
        containment_efficiency_pct=100.0,
        is_cut_vertex=True,
        mitigation_recommendation="Sever socket flow",
    )

    cp_mqtt = ChokePoint(
        node_id="cp_mqtt_topic",
        tier="Fog",
        host_id="fog-broker-01",
        action="write",
        entity="sensors/vibration/data",
        paths_severed_count=3,
        total_paths_count=4,
        containment_efficiency_pct=75.0,
        is_cut_vertex=False,
        mitigation_recommendation="Quarantine MQTT topic",
    )

    remediator = ActiveChokePointRemediator(lambda_collateral_weight=0.5)

    policy_net = remediator.synthesize_remediation_policy(
        cp_network,
        node_metadata={"event_type": "Socket", "src_ip": "10.0.1.10", "dst_port": 1883},
    )
    assert policy_net.mechanism == RemediationMechanism.EBPF_TC
    assert "tc filter add dev eth0" in policy_net.executable_command
    assert policy_net.containment_efficacy_pct == 100.0
    assert policy_net.remediation_priority_score > 0

    plan = remediator.generate_remediation_plan([cp_network, cp_mqtt])
    assert plan.total_choke_points_analyzed == 2
    assert plan.optimal_choke_point_node == "cp_fog_socket"
    assert plan.overall_containment_pct == 100.0
    assert "#!/bin/bash" in plan.deployment_script
