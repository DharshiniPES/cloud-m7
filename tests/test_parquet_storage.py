"""
Unit tests for Parquet + DuckDB Accessible Provenance Storage Engine.
"""

import os
import tempfile
import pytest

from cloud_m7.schema.event import ProvenanceEvent
from cloud_m7.schema.types import EventType, TierType
from cloud_m7.storage.parquet_engine import ProvenanceStorageEngine


@pytest.fixture
def sample_events():
    e1 = ProvenanceEvent(
        uuid="evt-001",
        timestamp=100.0,
        tier=TierType.EDGE,
        host_id="sensor-01",
        event_type=EventType.PROCESS,
        payload={"action": "exec", "entity": "/bin/sh", "is_attack": True},
    )
    e2 = ProvenanceEvent(
        uuid="evt-002",
        timestamp=102.5,
        tier=TierType.FOG,
        host_id="gateway-01",
        event_type=EventType.SOCKET,
        payload={
            "action": "connect",
            "entity": "10.0.1.5:1883",
            "src_ip": "10.0.1.10",
            "src_port": 49152,
            "dst_ip": "10.0.1.5",
            "dst_port": 1883,
            "protocol": "TCP",
            "is_attack": True,
        },
        parents=["evt-001"],
    )
    e3 = ProvenanceEvent(
        uuid="evt-003",
        timestamp=105.0,
        tier=TierType.CLOUD,
        host_id="cloud-srv-01",
        event_type=EventType.API,
        payload={"action": "exfil_data", "entity": "s3://sensitive-logs", "is_attack": True},
        parents=["evt-002"],
    )
    e4 = ProvenanceEvent(
        uuid="evt-004",
        timestamp=99.0,
        tier=TierType.EDGE,
        host_id="sensor-02",
        event_type=EventType.FILE,
        payload={"action": "read", "entity": "/tmp/temp.dat", "is_attack": False},
    )
    return [e1, e2, e3, e4]


def test_parquet_export_and_load(sample_events):
    with tempfile.TemporaryDirectory() as tmpdir:
        parquet_path = os.path.join(tmpdir, "test_events.parquet")
        engine = ProvenanceStorageEngine()

        # Export to Parquet
        out_path = engine.export_events_to_parquet(sample_events, parquet_path)
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0

        # Load back from Parquet
        loaded = engine.load_events_from_parquet(parquet_path)
        assert len(loaded) == len(sample_events)
        assert loaded[0].uuid == "evt-001"
        assert loaded[1].parents == ["evt-001"]
        assert loaded[2].tier == TierType.CLOUD


def test_duckdb_sql_querying(sample_events):
    with tempfile.TemporaryDirectory() as tmpdir:
        parquet_path = os.path.join(tmpdir, "test_events.parquet")
        engine = ProvenanceStorageEngine()
        engine.export_events_to_parquet(sample_events, parquet_path)

        # SQL Query via DuckDB
        norm_path = parquet_path.replace("\\", "/")
        df = engine.query_sql(f"SELECT host_id, tier FROM '{norm_path}' WHERE is_attack = TRUE ORDER BY timestamp")
        assert len(df) == 3
        assert list(df["tier"]) == ["Edge", "Fog", "Cloud"]

        # Summary query
        summary = engine.get_tier_summary(parquet_path)
        assert len(summary) == 3
        tier_names = [s["tier"] for s in summary]
        assert "Edge" in tier_names
        assert "Fog" in tier_names
        assert "Cloud" in tier_names


def test_compression_benchmark(sample_events):
    with tempfile.TemporaryDirectory() as tmpdir:
        parquet_path = os.path.join(tmpdir, "bench.parquet")
        json_path = os.path.join(tmpdir, "bench.json")
        engine = ProvenanceStorageEngine()

        res = engine.benchmark_compression(sample_events, parquet_path, json_path)
        assert res["total_events"] == 4
        assert res["json_size_bytes"] > 0
        assert res["parquet_size_bytes"] > 0
        assert res["compression_ratio"] > 0
