"""
Unit tests for CLOUD-M7 Cross-Tier Causal Provenance Fusion.
"""

from cloud_m7.fusion.causal_graph import ProvenanceGraphEngine
from cloud_m7.fusion.attack_path import AttackPathReconstructor
from cloud_m7.schema.event import ProvenanceEvent
from cloud_m7.schema.types import EventType, TierType


def test_cross_tier_network_correlation():
    engine = ProvenanceGraphEngine(time_window_seconds=5.0)

    # Edge outbound socket
    e_edge = ProvenanceEvent(
        uuid="edge-sock-01",
        timestamp=100.0,
        tier=TierType.EDGE,
        host_id="edge-01",
        event_type=EventType.SOCKET,
        payload={
            "action": "connect",
            "src_ip": "192.168.1.10",
            "src_port": 45000,
            "dst_ip": "10.0.1.1",
            "dst_port": 8080,
            "protocol": "TCP",
        },
    )

    # Fog inbound socket matching 5-tuple within time window
    e_fog = ProvenanceEvent(
        uuid="fog-sock-01",
        timestamp=100.02,
        tier=TierType.FOG,
        host_id="fog-01",
        event_type=EventType.SOCKET,
        payload={
            "action": "accept",
            "src_ip": "192.168.1.10",
            "src_port": 45000,
            "dst_ip": "10.0.1.1",
            "dst_port": 8080,
            "protocol": "TCP",
        },
    )

    engine.add_events([e_edge, e_fog])
    edges = engine.correlate_cross_tier_network()

    assert len(edges) == 1
    assert edges[0] == ("edge-sock-01", "fog-sock-01")

    # Global graph fusion
    g = engine.fuse_global_graph()
    assert g.has_edge("edge-sock-01", "fog-sock-01")


def test_backward_and_forward_traversal():
    engine = ProvenanceGraphEngine()

    e1 = ProvenanceEvent(uuid="e1", timestamp=1.0, tier=TierType.EDGE, event_type=EventType.PROCESS)
    e2 = ProvenanceEvent(uuid="e2", timestamp=2.0, tier=TierType.EDGE, event_type=EventType.FILE, parents=["e1"])
    e3 = ProvenanceEvent(uuid="e3", timestamp=3.0, tier=TierType.EDGE, event_type=EventType.PROCESS, parents=["e2"])

    engine.add_events([e1, e2, e3])
    engine.fuse_global_graph()

    reconstructor = AttackPathReconstructor(engine)

    # Backward from e3 should yield e1 and e2
    ancestors = reconstructor.backward_trace("e3")
    assert ancestors == {"e1", "e2", "e3"}

    # Forward from e1 should yield e2 and e3
    descendants = reconstructor.forward_trace("e1")
    assert descendants == {"e1", "e2", "e3"}
