"""
Unit tests for CLOUD-M7 Real Dataset Adapters and Normalizer Factory.
"""

import os
import pytest

from cloud_m7.adapters.factory import DatasetNormalizerFactory
from cloud_m7.adapters.optc_adapter import DarpaOpTCAdapter
from cloud_m7.adapters.tc_adapter import DarpaTCAdapter
from cloud_m7.adapters.ton_iot_adapter import TonIotAdapter
from cloud_m7.adapters.iot23_adapter import IoT23Adapter
from cloud_m7.schema.types import EventType, TierType


def test_darpa_optc_adapter():
    sample_jsonl = """{"id": "optc-1", "hostname": "optc-srv", "object": "PROCESS", "action": "CREATE", "timestamp": 1600000000.0, "properties": {"pid": 100, "image_path": "/bin/bash"}, "is_attack": false}
{"id": "optc-2", "hostname": "optc-srv", "object": "FLOW", "action": "CONNECT", "timestamp": 1600000001.0, "properties": {"src_ip": "10.0.1.5", "dst_ip": "172.16.0.10", "dst_port": 443}, "is_attack": true}"""
    adapter = DarpaOpTCAdapter()
    assert adapter.can_handle(sample_jsonl)
    events = adapter.parse_records(sample_jsonl)
    assert len(events) == 2
    assert events[0].event_type == EventType.PROCESS
    assert events[1].event_type == EventType.SOCKET
    assert events[1].payload["is_attack"] is True
    assert events[1].payload["dst_port"] == 443


def test_darpa_tc_adapter():
    sample_cdm = """[
      {"type": "EVENT_FORK", "event": {"uuid": "tc-1", "hostId": "tc-gw", "timestamp": 1600000000.0, "subject": "s1", "predicateObject": "/bin/daemon"}},
      {"type": "EVENT_CONNECT", "event": {"uuid": "tc-2", "hostId": "tc-gw", "timestamp": 1600000001.0, "subject": "s1", "src_ip": "10.0.1.5", "dst_ip": "10.0.2.1", "dst_port": 8080, "is_attack": true}}
    ]"""
    adapter = DarpaTCAdapter()
    assert adapter.can_handle(sample_cdm)
    events = adapter.parse_records(sample_cdm)
    assert len(events) == 2
    assert events[0].event_type == EventType.PROCESS
    assert events[1].event_type == EventType.SOCKET
    assert events[1].payload["is_attack"] is True


def test_ton_iot_adapter():
    sample_csv = """ts,src_ip,src_port,dst_ip,dst_port,proto,service,temperature,humidity,type,label
1600000000.0,192.168.1.100,49152,10.0.1.1,1883,TCP,mqtt,23.5,50.1,normal,0
1600000001.0,192.168.1.100,49154,10.0.1.1,1883,TCP,mqtt,25.0,52.0,backdoor,1"""
    adapter = TonIotAdapter()
    assert adapter.can_handle(sample_csv)
    events = adapter.parse_records(sample_csv)
    assert len(events) == 2
    assert events[0].payload["is_attack"] is False
    assert events[1].payload["is_attack"] is True
    assert "telemetry" in events[1].payload


def test_iot23_adapter():
    sample_tsv = """ts\tid.orig_h\tid.orig_p\tid.resp_h\tid.resp_p\tproto\tservice\tconn_state\tlabel\tdetailed-label
1600000000.0\t192.168.1.190\t49152\t10.0.1.1\t23\tTCP\ttelnet\tS0\tMalicious\tMirai"""
    adapter = IoT23Adapter()
    assert adapter.can_handle(sample_tsv)
    events = adapter.parse_records(sample_tsv)
    assert len(events) == 1
    assert events[0].event_type == EventType.SOCKET
    assert events[0].payload["is_attack"] is True
    assert events[0].payload["malware_label"] == "Mirai"


def test_normalizer_factory_auto_detection():
    factory = DatasetNormalizerFactory()
    sample_optc = '{"id": "optc-x", "object": "PROCESS", "action": "CREATE", "properties": {"command_line": "test"}}'
    events, fmt = factory.normalize(sample_optc)
    assert fmt == "DARPA_OpTC"
    assert len(events) == 1
    assert events[0].event_type == EventType.PROCESS
