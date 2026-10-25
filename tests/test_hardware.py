"""
Unit tests for CLOUD-M7 Physical Hardware Telemetry & Probe.
"""

import pytest
from cloud_m7.hardware.edge_probe import generate_hardware_event
from cloud_m7.hardware.fog_receiver import FogHardwareGatewayServer
from cloud_m7.schema.event import ProvenanceEvent


def test_hardware_event_generation():
    evt_dict = generate_hardware_event(
        event_type="Process",
        action="exec",
        entity="/usr/bin/iot_sensor_app",
        is_attack=False,
        extra_payload={"cpu_temp_c": 43.5},
        host_id="rpi-test-01",
    )
    assert evt_dict["tier"] == "Edge"
    assert evt_dict["host_id"] == "rpi-test-01"
    assert evt_dict["payload"]["cpu_temp_c"] == 43.5
    assert len(evt_dict["tamper_hash"]) == 64

    # Convert to ProvenanceEvent instance
    pe = ProvenanceEvent.from_dict(evt_dict)
    assert pe.host_id == "rpi-test-01"
    assert pe.tamper_hash is not None


def test_fog_hardware_gateway_server():
    server = FogHardwareGatewayServer(port=8089)
    # Server can initialize cleanly
    assert server.port == 8089
    FogHardwareGatewayServer.clear_buffer()
    assert len(FogHardwareGatewayServer.get_buffered_events()) == 0
