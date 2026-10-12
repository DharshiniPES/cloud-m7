"""
Active Choke-Point Remediation & Zero-Blast-Radius Containment Engine.

Transforms passive forensic articulation choke points (E_cut) into active,
automated, zero-blast-radius containment policies.

Key Capabilities:
    1. Automated Policy Synthesis: Generates concrete mitigation rules:
       - eBPF / TC Network Drop Rules (for network bridge choke points)
       - Linux iptables Packet Filters (for socket choke points)
       - MQTT Broker Dynamic ACL Quarantine (for IoT sensor topic choke points)
       - Linux cgroup v2 Process Freeze (for compromised process choke points)
    2. Pareto Optimization & Blast-Radius Evaluation:
       Balances Containment Efficacy (CE) against Collateral Disruption Index (CDI):
           RPS = CE / (1.0 + lambda * CDI)
    3. Executable Remediation Script Generation:
       Produces shell scripts and JSON policy bundles ready for immediate deployment.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from cloud_m7.fusion.interconnected_paths import ChokePoint


class RemediationMechanism(str, Enum):
    """Enforcement mechanisms for active choke-point containment."""
    EBPF_TC = "eBPF_Traffic_Control"
    IPTABLES = "iptables_Firewall"
    MQTT_ACL = "MQTT_Topic_Quarantine"
    CGROUP_FREEZE = "Linux_cgroup_Freeze"
    API_REVOKE = "Cloud_IAM_Revocation"


@dataclass
class RemediationPolicy:
    """Actionable mitigation policy synthesized for a specific choke point."""
    choke_point_node_id: str
    target_tier: str
    target_host: str
    mechanism: RemediationMechanism
    containment_efficacy_pct: float
    collateral_disruption_index: float
    remediation_priority_score: float
    executable_command: str
    rollback_command: str
    policy_description: str


@dataclass
class RemediationPlan:
    """Complete active containment plan covering multi-tier choke points."""
    total_choke_points_analyzed: int
    optimal_choke_point_node: str
    overall_containment_pct: float
    average_collateral_index: float
    policies: List[RemediationPolicy]
    deployment_script: str


class ActiveChokePointRemediator:
    """
    Synthesizes zero-blast-radius containment policies from identified choke points.
    """

    def __init__(self, lambda_collateral_weight: float = 0.5):
        self.lambda_weight = lambda_collateral_weight

    def synthesize_remediation_policy(
        self,
        choke_point: ChokePoint,
        node_metadata: Optional[Dict[str, Any]] = None,
    ) -> RemediationPolicy:
        """
        Synthesizes a concrete mitigation policy for an individual choke point.
        """
        meta = node_metadata or {}
        tier = choke_point.tier
        host = choke_point.host_id
        action = choke_point.action.lower()
        entity = choke_point.entity
        event_type = meta.get("event_type", "Process")

        # Determine optimal enforcement mechanism
        if "connect" in action or "socket" in event_type.lower() or "network" in event_type.lower():
            mechanism = RemediationMechanism.EBPF_TC
            src_ip = meta.get("src_ip", "10.0.1.0/24")
            dst_port = meta.get("dst_port", 1883)
            cmd = f"tc filter add dev eth0 ingress bpf da obj /opt/cloud_m7/ebpf_drop.o sec drop_host src {src_ip} port {dst_port}"
            rollback = f"tc filter del dev eth0 ingress pref 1"
            cdi = 0.05  # Highly targeted eBPF rule has minimal collateral disruption
            desc = f"Install eBPF TC drop filter on {host} targeting ingress packets from {src_ip}:{dst_port}."

        elif "mqtt" in entity.lower() or "sensor" in entity.lower() or "topic" in action:
            mechanism = RemediationMechanism.MQTT_ACL
            topic = entity if "/" in entity else f"sensors/{entity}/data"
            cmd = f"mosquitto_ctrl dynsec setAnonymousGroupACL deny write {topic}"
            rollback = f"mosquitto_ctrl dynsec setAnonymousGroupACL allow write {topic}"
            cdi = 0.12  # Moderate disruption: only specific MQTT topic quarantined
            desc = f"Quarantine MQTT broker topic '{topic}' on Fog Gateway {host} to sever sensor telemetry injection."

        elif "auth" in action or "token" in action or tier == "Cloud":
            mechanism = RemediationMechanism.API_REVOKE
            cmd = f"aws iam update-access-key --access-key-id {entity} --status Inactive"
            rollback = f"aws iam update-access-key --access-key-id {entity} --status Active"
            cdi = 0.02
            desc = f"Revoke compromised credential / token '{entity}' on Cloud API endpoint {host}."

        elif "exec" in action or "fork" in action or "process" in event_type.lower():
            mechanism = RemediationMechanism.CGROUP_FREEZE
            pid = meta.get("pid", 1402)
            cmd = f"echo 1 > /sys/fs/cgroup/system.slice/cloud_m7_proc_{pid}.slice/cgroup.freeze"
            rollback = f"echo 0 > /sys/fs/cgroup/system.slice/cloud_m7_proc_{pid}.slice/cgroup.freeze"
            cdi = 0.08  # Freezes only target process slice
            desc = f"Freeze malicious process '{entity}' (PID: {pid}) via Linux cgroup v2 on {host}."

        else:
            mechanism = RemediationMechanism.IPTABLES
            cmd = f"iptables -I FORWARD -m string --string '{entity}' --algo bm -j DROP"
            rollback = f"iptables -D FORWARD -m string --string '{entity}' --algo bm -j DROP"
            cdi = 0.20
            desc = f"Apply iptables packet-filter on {host} matching pattern '{entity}'."

        # Compute Remediation Priority Score (RPS)
        ce = choke_point.containment_efficiency_pct
        rps = round(ce / (1.0 + self.lambda_weight * cdi), 2)

        return RemediationPolicy(
            choke_point_node_id=choke_point.node_id,
            target_tier=tier,
            target_host=host,
            mechanism=mechanism,
            containment_efficacy_pct=ce,
            collateral_disruption_index=cdi,
            remediation_priority_score=rps,
            executable_command=cmd,
            rollback_command=rollback,
            policy_description=desc,
        )

    def generate_remediation_plan(
        self,
        choke_points: List[ChokePoint],
        graph_nodes_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> RemediationPlan:
        """
        Synthesizes a prioritized containment plan across all detected choke points.
        """
        if not choke_points:
            return RemediationPlan(
                total_choke_points_analyzed=0,
                optimal_choke_point_node="None",
                overall_containment_pct=0.0,
                average_collateral_index=0.0,
                policies=[],
                deployment_script="# No choke points detected for remediation.\n",
            )

        meta_dict = graph_nodes_metadata or {}
        policies: List[RemediationPolicy] = []

        for cp in choke_points:
            node_meta = meta_dict.get(cp.node_id, {})
            policy = self.synthesize_remediation_policy(cp, node_meta)
            policies.append(policy)

        # Sort policies by Remediation Priority Score descending
        policies.sort(key=lambda p: p.remediation_priority_score, reverse=True)

        optimal_policy = policies[0]
        avg_cdi = round(sum(p.collateral_disruption_index for p in policies) / len(policies), 3)

        # Generate deployable bash script
        script_lines = [
            "#!/bin/bash",
            "# ===========================================================================",
            "# CLOUD-M7 Automated Active Choke-Point Containment Script",
            f"# Optimal Target: Host {optimal_policy.target_host} ({optimal_policy.target_tier})",
            f"# Containment Efficacy: {optimal_policy.containment_efficacy_pct}%",
            f"# Collateral Disruption Index: {optimal_policy.collateral_disruption_index}",
            "# ===========================================================================",
            "set -euo pipefail",
            "",
            f"echo '[*] Deploying CLOUD-M7 active containment at choke-point {optimal_policy.choke_point_node_id}...' ",
            f"# Mechanism: {optimal_policy.mechanism.value}",
            f"{optimal_policy.executable_command}",
            "echo '[+] Choke-point successfully isolated. Attack path severed.'",
            "",
            "# Rollback function:",
            "# To revert this containment rule:",
            f"# {optimal_policy.rollback_command}",
            "",
        ]

        return RemediationPlan(
            total_choke_points_analyzed=len(choke_points),
            optimal_choke_point_node=optimal_policy.choke_point_node_id,
            overall_containment_pct=optimal_policy.containment_efficacy_pct,
            average_collateral_index=avg_cdi,
            policies=policies,
            deployment_script="\n".join(script_lines),
        )
