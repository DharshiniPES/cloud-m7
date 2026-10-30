"""
CLOUD-M7 Advanced Systems Package.
Contains 6 Defense-Grade Capabilities:
1. In-Kernel eBPF LSM Hooks & Hardware Performance Counters (HPC) Microarchitectural Auditing
2. Shannon Entropy Reduction (Dependency Explosion Pruning) & Temporal GNN Anomaly Scoring
3. Autonomous Reinforcement Learning Defense Agent (MDP Q-Learning / PPO)
4. Zero-Knowledge Provenance Verification (ZK-SNARK Arithmetic Constraint Circuit)
5. Adversarial Provenance Camouflage & Anti-Forensics Invariant Shield
6. OASIS STIX 2.1 Threat Intelligence Bundling & Event-Time Streaming Engine
"""

from .ebpf_hpc import EbpfHpcTelemetryEngine
from .gnn_entropy import EntropyGraphPruner, TemporalGnnAnomalyScorer
from .rl_containment import AutonomousRlContainmentAgent
from .zk_provenance import ZkProvenanceVerifier
from .adversarial_shield import AdversarialCamouflageSuite, ProvenanceInvariantShield
from .stix_stream import StixThreatIntelGenerator, EventTimeStreamingEngine

__all__ = [
    "EbpfHpcTelemetryEngine",
    "EntropyGraphPruner",
    "TemporalGnnAnomalyScorer",
    "AutonomousRlContainmentAgent",
    "ZkProvenanceVerifier",
    "AdversarialCamouflageSuite",
    "ProvenanceInvariantShield",
    "StixThreatIntelGenerator",
    "EventTimeStreamingEngine",
]
