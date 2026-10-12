"""
MITRE ATT&CK Matrix Motif Mapping Engine for Cross-Tier Provenance Graphs.

Translates low-level, heterogeneous operating system and network provenance events
(e.g., sys_clone, execve, connect, write) into high-level MITRE ATT&CK Enterprise
and ICS/IoT tactics and techniques.

Key Capabilities:
    1. Multi-Tier Semantic Alignment: Maps Edge, Fog, and Cloud telemetry to:
       - Initial Access (TA0001): T1190 Exploit Public-Facing Application
       - Execution (TA0002): T1059 Command and Scripting Interpreter
       - Privilege Escalation (TA0004): T1068 Exploitation for Privilege Escalation
       - Lateral Movement (TA0008): T1021 Remote Services / MQTT Pivot
       - Persistence (TA0003): T1543 Create or Modify System Process
       - Exfiltration (TA0010): T1048 Alternative Protocol / T1567 Cloud Storage
    2. Forensic Evidence Correlation: Links each MITRE technique to specific
       provenance event UUIDs, generating an audit-ready timeline.
    3. MITRE Attack Progression Matrix: Generates an ASCII/JSON matrix report
       demonstrating the adversary's step-by-step kill-chain across tiers.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

import networkx as nx


@dataclass
class MitreTechniqueMatch:
    """Represents a detected MITRE ATT&CK technique mapped from provenance telemetry."""
    tactic_id: str
    tactic_name: str
    technique_id: str
    technique_name: str
    tier: str
    host_id: str
    evidence_uuid: str
    action: str
    entity: str
    timestamp: float
    confidence_score: float
    reasoning: str


@dataclass
class MitreMappingReport:
    """Consolidated MITRE ATT&CK forensic mapping report for reconstructed attack paths."""
    total_techniques_mapped: int
    tactics_observed: List[str]
    kill_chain_coverage_pct: float
    matched_techniques: List[MitreTechniqueMatch]
    progression_summary: str


class MitreAttackMapper:
    """
    Analyzes provenance graphs and maps causal paths to MITRE ATT&CK tactics & techniques.
    """

    # MITRE ATT&CK Kill-Chain Stages (Standard ordering)
    TACTIC_LIFECYCLE = [
        "Initial Access",
        "Execution",
        "Privilege Escalation",
        "Persistence",
        "Lateral Movement",
        "Collection",
        "Exfiltration",
        "Impact",
    ]

    def __init__(self):
        pass

    def evaluate_node_for_mitre(
        self,
        node_id: str,
        data: Dict[str, Any],
        predecessors: List[Dict[str, Any]],
    ) -> List[MitreTechniqueMatch]:
        """
        Evaluates an individual provenance graph node and its local context
        against MITRE ATT&CK behavioral motifs.
        """
        matches: List[MitreTechniqueMatch] = []
        if not data.get("is_attack"):
            return matches

        tier = data.get("tier", "Unknown")
        host = data.get("host_id", "Unknown")
        event_type = data.get("event_type", "Process")
        action = str(data.get("action", "")).lower()
        entity = str(data.get("entity", "")).lower()
        ts = float(data.get("timestamp", 0.0))

        # 1. Initial Access: T1190 (Exploit Public-Facing App)
        # Condition: Edge sensor receiving network connection followed by command execution
        if tier == "Edge" and ("connect" in action or "accept" in action or "firmware" in entity):
            matches.append(
                MitreTechniqueMatch(
                    tactic_id="TA0001",
                    tactic_name="Initial Access",
                    technique_id="T1190",
                    technique_name="Exploit Public-Facing Application",
                    tier=tier,
                    host_id=host,
                    evidence_uuid=node_id,
                    action=action,
                    entity=entity,
                    timestamp=ts,
                    confidence_score=0.92,
                    reasoning=f"Unauthorized network ingress or firmware exploit detected on edge sensor {host}.",
                )
            )

        # 2. Execution: T1059 (Command and Scripting Interpreter)
        # Condition: Spawning sh, bash, python, or executing scripts
        if ("exec" in action or "fork" in action) and any(x in entity for x in ["sh", "bash", "python", "cmd", "busybox", "payload"]):
            matches.append(
                MitreTechniqueMatch(
                    tactic_id="TA0002",
                    tactic_name="Execution",
                    technique_id="T1059",
                    technique_name="Command and Scripting Interpreter",
                    tier=tier,
                    host_id=host,
                    evidence_uuid=node_id,
                    action=action,
                    entity=entity,
                    timestamp=ts,
                    confidence_score=0.95,
                    reasoning=f"Execution of shell/scripting interpreter binary '{entity}' on {host}.",
                )
            )

        # 3. Privilege Escalation: T1068 (Exploitation for Privilege Escalation)
        # Condition: Write to sensitive root paths or user escalation
        if ("write" in action or "modify" in action) and any(x in entity for x in ["/etc/shadow", "/etc/sudoers", "/root", "suid", "priv"]):
            matches.append(
                MitreTechniqueMatch(
                    tactic_id="TA0004",
                    tactic_name="Privilege Escalation",
                    technique_id="T1068",
                    technique_name="Exploitation for Privilege Escalation",
                    tier=tier,
                    host_id=host,
                    evidence_uuid=node_id,
                    action=action,
                    entity=entity,
                    timestamp=ts,
                    confidence_score=0.88,
                    reasoning=f"Modification of sensitive administrative resource '{entity}' on {host}.",
                )
            )

        # 4. Lateral Movement: T1021 (Remote Services) / MQTT Pivot
        # Condition: Cross-tier network socket connecting from Edge to Fog or Fog to Cloud
        if ("connect" in action or "send" in action) and (tier in ["Edge", "Fog"]) and any(x in entity for x in ["mqtt", "1883", "ssh", "22", "gateway", "broker"]):
            matches.append(
                MitreTechniqueMatch(
                    tactic_id="TA0008",
                    tactic_name="Lateral Movement",
                    technique_id="T1021",
                    technique_name="Remote Services: MQTT / SSH Pivot",
                    tier=tier,
                    host_id=host,
                    evidence_uuid=node_id,
                    action=action,
                    entity=entity,
                    timestamp=ts,
                    confidence_score=0.94,
                    reasoning=f"Cross-tier lateral pivot from {tier} host {host} towards intermediate service '{entity}'.",
                )
            )

        # 5. Persistence: T1543 (Create or Modify System Process)
        # Condition: Service creation, cron, or systemd modification
        if any(x in entity for x in ["systemd", "cron", "init.d", "service", "daemon"]):
            matches.append(
                MitreTechniqueMatch(
                    tactic_id="TA0003",
                    tactic_name="Persistence",
                    technique_id="T1543",
                    technique_name="Create or Modify System Process",
                    tier=tier,
                    host_id=host,
                    evidence_uuid=node_id,
                    action=action,
                    entity=entity,
                    timestamp=ts,
                    confidence_score=0.85,
                    reasoning=f"System daemon or persistent service persistence established via '{entity}' on {host}.",
                )
            )

        # 6. Exfiltration: T1048 / T1567 (Exfiltration Over Cloud Storage / Alternative Protocol)
        # Condition: Cloud tier API exfil, S3 push, or database dump
        if tier == "Cloud" and ("exfil" in action or "query_db" in action or "s3" in entity or "bucket" in entity or "database" in entity):
            matches.append(
                MitreTechniqueMatch(
                    tactic_id="TA0010",
                    tactic_name="Exfiltration",
                    technique_id="T1567",
                    technique_name="Exfiltration to Cloud Storage / Data Repository",
                    tier=tier,
                    host_id=host,
                    evidence_uuid=node_id,
                    action=action,
                    entity=entity,
                    timestamp=ts,
                    confidence_score=0.96,
                    reasoning=f"Unauthorized bulk data exfiltration targeting cloud endpoint '{entity}' on {host}.",
                )
            )

        return matches

    def map_attack_graph(self, attack_graph: nx.DiGraph) -> MitreMappingReport:
        """
        Maps an entire attack graph or reconstructed attack path into the MITRE ATT&CK framework.
        """
        all_matches: List[MitreTechniqueMatch] = []

        for node_id, data in attack_graph.nodes(data=True):
            preds = [attack_graph.nodes[p] for p in attack_graph.predecessors(node_id)]
            node_matches = self.evaluate_node_for_mitre(node_id, data, preds)
            all_matches.extend(node_matches)

        # Sort matches by timestamp to reflect true kill-chain sequence
        all_matches.sort(key=lambda m: m.timestamp)

        # Deduplicate identical (technique_id, host_id) matches
        deduped_matches: List[MitreTechniqueMatch] = []
        seen: Set[str] = set()
        for m in all_matches:
            key = f"{m.technique_id}:{m.host_id}:{m.evidence_uuid}"
            if key not in seen:
                seen.add(key)
                deduped_matches.append(m)

        tactics_observed = sorted(list({m.tactic_name for m in deduped_matches}))
        coverage_pct = round((len(tactics_observed) / len(self.TACTIC_LIFECYCLE)) * 100.0, 1)

        # Format human-readable progression summary
        summary_lines = [
            "MITRE ATT&CK Cross-Tier Kill-Chain Progression:",
            "=" * 60,
        ]
        for idx, m in enumerate(deduped_matches, start=1):
            summary_lines.append(
                f"[{idx}] {m.tactic_name} ({m.tactic_id}) -> {m.technique_name} ({m.technique_id})"
            )
            summary_lines.append(
                f"    Tier: {m.tier} | Host: {m.host_id} | Evidence UUID: {m.evidence_uuid[:8]}..."
            )
            summary_lines.append(f"    Detail: {m.reasoning}")

        summary_lines.append("=" * 60)
        summary_lines.append(
            f"Observed Tactics: {', '.join(tactics_observed)} ({coverage_pct}% lifecycle coverage)"
        )

        return MitreMappingReport(
            total_techniques_mapped=len(deduped_matches),
            tactics_observed=tactics_observed,
            kill_chain_coverage_pct=coverage_pct,
            matched_techniques=deduped_matches,
            progression_summary="\n".join(summary_lines),
        )
