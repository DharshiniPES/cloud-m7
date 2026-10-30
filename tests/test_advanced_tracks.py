"""
Comprehensive Automated Unit and Integration Tests for All 6 Advanced Capabilities.
"""

import pytest
import networkx as nx
from cloud_m7.advanced.ebpf_hpc import EbpfHpcTelemetryEngine
from cloud_m7.advanced.gnn_entropy import EntropyGraphPruner, TemporalGnnAnomalyScorer
from cloud_m7.advanced.rl_containment import AutonomousRlContainmentAgent
from cloud_m7.advanced.zk_provenance import ZkProvenanceVerifier
from cloud_m7.advanced.adversarial_shield import AdversarialCamouflageSuite, ProvenanceInvariantShield
from cloud_m7.advanced.stix_stream import StixThreatIntelGenerator, EventTimeStreamingEngine


def test_track1_ebpf_hpc_and_tpm():
    engine = EbpfHpcTelemetryEngine()
    
    # 1. Capture eBPF LSM record
    rec = engine.capture_ebpf_lsm_event(is_exploit=True)
    assert rec.is_anomaly is True
    assert rec.kernel_stack_depth > 10
    
    # 2. Hardware Performance Counters
    hpc_nominal = engine.sample_hardware_counters(is_under_attack=False)
    assert hpc_nominal.is_microarchitectural_anomaly is False
    assert hpc_nominal.ipc > 0.7
    
    hpc_attack = engine.sample_hardware_counters(is_under_attack=True)
    assert hpc_attack.is_microarchitectural_anomaly is True
    assert hpc_attack.cache_miss_rate > 10.0
    
    # 3. TPM 2.0 Quote Attestation
    quote = engine.generate_tpm2_quote(event_hash="test_sha256_hash")
    assert quote.pcr_index == 10
    assert quote.attestation_verified is True
    assert len(quote.tpm_signature) > 10


def test_track2_entropy_pruning_and_gnn():
    g = nx.DiGraph()
    # Build benign star-mesh topology with an attack chain
    for i in range(15):
        g.add_node(f"node_{i}", tier="Edge", action="log_read", is_attack=False)
    for i in range(1, 15):
        g.add_edge("node_0", f"node_{i}", action="read")

    # Add attack chain
    g.add_node("atk_1", tier="Edge", action="execve", is_attack=True)
    g.add_node("atk_2", tier="Fog", action="socket_connect", is_attack=True)
    g.add_edge("atk_1", "atk_2", action="pivot", is_attack=True)

    attack_nodes = {"atk_1", "atk_2"}
    pruner = EntropyGraphPruner(entropy_threshold=0.5)
    pruned_g, res = pruner.prune_dependency_explosion(g, attack_nodes)

    assert res.attack_chain_preserved is True
    assert "atk_1" in pruned_g and "atk_2" in pruned_g
    assert pruned_g.number_of_edges() <= g.number_of_edges()

    # Temporal GNN scoring
    gnn = TemporalGnnAnomalyScorer(embedding_dim=16)
    scores = gnn.score_graph_anomalies(g)
    assert len(scores) == g.number_of_nodes()
    # Attack nodes should have highest anomaly scores
    top_nodes = [s.node_id for s in scores[:3]]
    assert "atk_1" in top_nodes or "atk_2" in top_nodes


def test_track3_rl_containment_agent():
    agent = AutonomousRlContainmentAgent()
    summary = agent.train_agent(episodes=60)
    
    assert summary.episodes_trained == 60
    assert len(summary.simulation_trajectory) > 0
    # Final step should reach contained stable state
    final_step = summary.simulation_trajectory[-1]
    assert "CONTAINED" in final_step.next_state_name or "CONTAINED" in final_step.state_name
    assert "DROP_CHOKE_SOCKET" in summary.optimal_policy["S2: FOG_GATEWAY_PIVOT"]


def test_track4_zk_provenance_verifier():
    verifier = ZkProvenanceVerifier()
    proof = verifier.generate_zk_proof(path_length=14, choke_point_severed=True)
    
    assert proof.num_constraints == 2840
    assert proof.public_inputs["containment_proven"] == "1"
    assert verifier.verify_proof(proof) is True

    # Tampered claim verification should fail
    proof_tampered = verifier.generate_zk_proof(path_length=14, choke_point_severed=False)
    assert verifier.verify_proof(proof_tampered) is False


def test_track5_adversarial_shield():
    g = nx.DiGraph()
    g.add_node("edge_cam", tier="Edge", action="exec", is_attack=True)
    g.add_node("fog_gw", tier="Fog", action="connect", is_attack=True)
    g.add_edge("edge_cam", "fog_gw", action="socket_connect", time_delta=1.5)

    # 1. Inject Graph Inflation Noise
    tampered_g, report = AdversarialCamouflageSuite.inject_graph_inflation(g, dummy_count=10)
    assert tampered_g.number_of_nodes() == g.number_of_nodes() + 10

    # 2. Invariant Shield Neutralization
    shield = ProvenanceInvariantShield()
    cleaned_g, verification = shield.verify_and_shield(tampered_g)
    assert verification.synthetic_inflation_nodes_pruned == 10
    assert cleaned_g.number_of_nodes() == g.number_of_nodes()
    assert len(verification.invariants_verified) == 4


def test_track6_stix_and_streaming():
    stix_gen = StixThreatIntelGenerator()
    dummy_steps = [
        {"tier": "Edge", "action": "execve", "host_id": "rpi-01", "description": "Firmware tampering"},
        {"tier": "Fog", "action": "connect", "host_id": "fog-gw", "description": "Lateral pivot"},
    ]
    bundle = stix_gen.generate_stix_bundle(dummy_steps, choke_point_node="fog-gateway-01")
    assert bundle.spec_version == "2.1"
    assert bundle.objects_count >= 4
    assert "bundle--" in bundle.bundle_id
    assert "threat-actor--" in bundle.stix_json_string

    # Streaming Engine
    stream_eng = EventTimeStreamingEngine()
    metrics = stream_eng.benchmark_stream_ingestion(total_events=25_000)
    assert metrics.events_ingested == 25_000
    assert metrics.throughput_events_per_sec > 50_000
