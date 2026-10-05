"""
Unit tests for CLOUD-M7 Provenance Event Schema.
"""

import pytest
from cloud_m7.schema.event import ProvenanceEvent
from cloud_m7.schema.types import EventType, TierType


def test_event_initialization_and_hash():
    event = ProvenanceEvent(
        uuid="test-uuid-001",
        timestamp=1000.0,
        tier=TierType.EDGE,
        host_id="edge-test-01",
        event_type=EventType.PROCESS,
        payload={"action": "exec", "cmd": "ps aux"},
    )
    assert event.uuid == "test-uuid-001"
    assert event.tier == TierType.EDGE
    assert event.event_type == EventType.PROCESS
    assert event.tamper_hash is not None
    assert len(event.tamper_hash) == 64  # SHA-256


def test_serialization_and_deserialization():
    event = ProvenanceEvent(
        uuid="test-uuid-002",
        timestamp=1005.5,
        tier="Fog",
        host_id="fog-gw-01",
        event_type="Socket",
        payload={
            "action": "connect",
            "src_ip": "10.0.1.1",
            "src_port": 5000,
            "dst_ip": "172.16.0.10",
            "dst_port": 443,
        },
        parents=["parent-uuid-001"],
    )
    # Check enum normalization
    assert event.tier == TierType.FOG
    assert event.event_type == EventType.SOCKET

    # JSON roundtrip
    json_str = event.to_json()
    recovered = ProvenanceEvent.from_json(json_str)

    assert recovered.uuid == event.uuid
    assert recovered.timestamp == event.timestamp
    assert recovered.tier == event.tier
    assert recovered.host_id == event.host_id
    assert recovered.event_type == event.event_type
    assert recovered.parents == event.parents
    assert recovered.tamper_hash == event.tamper_hash


def test_network_tuple_extraction():
    event = ProvenanceEvent(
        uuid="test-uuid-003",
        event_type=EventType.SOCKET,
        payload={
            "action": "connect",
            "src_ip": "192.168.1.10",
            "src_port": 40000,
            "dst_ip": "10.0.1.1",
            "dst_port": 8080,
            "protocol": "TCP",
        },
    )
    assert event.is_network_event is True
    tup = event.network_tuple
    assert tup == ("192.168.1.10", 40000, "10.0.1.1", 8080, "TCP")
