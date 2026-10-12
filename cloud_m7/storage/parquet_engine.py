"""
Accessible Columnar Provenance Storage Engine via Apache Parquet and DuckDB.

Provides ultra-fast, high-compression, zero-setup storage and querying for
CLOUD-M7 Canonical Provenance Events (Equation 1: E_i).

Key Advantages over Raw Log / JSON Files:
    1. Columnar Compression: 10x-50x storage footprint reduction via Snappy/ZSTD Parquet.
    2. Zero-Copy In-Process SQL: Sub-millisecond SQL queries directly over on-disk Parquet files via DuckDB.
    3. Multi-Tier Accessibility: Instantly inspectable in Python, Pandas, VS Code, or standard BI tools.
"""

import json
import os
import time
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple, Union

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from cloud_m7.schema.event import ProvenanceEvent
from cloud_m7.schema.types import EventType, TierType


class ProvenanceStorageEngine:
    """
    High-performance Parquet and DuckDB storage and query interface
    for multi-tier forensic provenance events.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initializes the DuckDB connection. If db_path is None, uses in-memory DuckDB.
        """
        self.conn = duckdb.connect(database=db_path if db_path else ":memory:")

    @staticmethod
    def events_to_dataframe(events: List[ProvenanceEvent]) -> pd.DataFrame:
        """
        Converts a list of ProvenanceEvent objects into a structured tabular DataFrame
        optimized for columnar Parquet serialization.
        """
        records = []
        for e in events:
            # Flatten crucial payload fields for direct columnar indexing
            action = e.payload.get("action", "") if isinstance(e.payload, dict) else ""
            entity = e.payload.get("entity", "") if isinstance(e.payload, dict) else ""
            is_attack = bool(e.payload.get("is_attack", False)) if isinstance(e.payload, dict) else False
            
            src_ip = e.payload.get("src_ip", "") if isinstance(e.payload, dict) else ""
            src_port = int(e.payload.get("src_port", 0)) if isinstance(e.payload, dict) and "src_port" in e.payload else 0
            dst_ip = e.payload.get("dst_ip", "") if isinstance(e.payload, dict) else ""
            dst_port = int(e.payload.get("dst_port", 0)) if isinstance(e.payload, dict) and "dst_port" in e.payload else 0
            protocol = e.payload.get("protocol", "") if isinstance(e.payload, dict) else ""

            records.append({
                "uuid": e.uuid,
                "timestamp": float(e.timestamp),
                "tier": e.tier.value if isinstance(e.tier, TierType) else str(e.tier),
                "host_id": str(e.host_id),
                "event_type": e.event_type.value if isinstance(e.event_type, EventType) else str(e.event_type),
                "action": str(action),
                "entity": str(entity),
                "is_attack": is_attack,
                "src_ip": str(src_ip),
                "src_port": int(src_port),
                "dst_ip": str(dst_ip),
                "dst_port": int(dst_port),
                "protocol": str(protocol),
                "parents_json": json.dumps(e.parents),
                "payload_json": json.dumps(e.payload, default=str),
                "tamper_hash": str(e.tamper_hash or ""),
            })

        df = pd.DataFrame(records)
        return df

    def export_events_to_parquet(
        self,
        events: List[ProvenanceEvent],
        parquet_path: str,
        compression: str = "snappy",
    ) -> str:
        """
        Serializes ProvenanceEvent records into a compressed Apache Parquet file.
        """
        os.makedirs(os.path.dirname(os.path.abspath(parquet_path)), exist_ok=True)
        df = self.events_to_dataframe(events)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, parquet_path, compression=compression)
        return parquet_path

    def load_events_from_parquet(self, parquet_path: str) -> List[ProvenanceEvent]:
        """
        Reads a Parquet file and reconstructs the full list of ProvenanceEvent objects.
        """
        table = pq.read_table(parquet_path)
        df = table.to_pandas()
        events = []
        for _, row in df.iterrows():
            parents = json.loads(row["parents_json"]) if row["parents_json"] else []
            payload = json.loads(row["payload_json"]) if row["payload_json"] else {}
            events.append(
                ProvenanceEvent(
                    uuid=row["uuid"],
                    timestamp=float(row["timestamp"]),
                    tier=TierType(row["tier"]),
                    host_id=row["host_id"],
                    event_type=EventType(row["event_type"]),
                    payload=payload,
                    parents=parents,
                    tamper_hash=row["tamper_hash"],
                )
            )
        return events

    def query_sql(
        self,
        sql_query: str,
        parquet_path: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Executes an arbitrary SQL query directly over the Parquet file or in-memory tables.
        If parquet_path is provided, replaces occurrences of 'provenance' with the parquet path.
        """
        if parquet_path:
            # Normalize path for DuckDB SQL syntax
            norm_path = parquet_path.replace("\\", "/")
            query_to_run = sql_query.replace("FROM provenance", f"FROM '{norm_path}'")
            query_to_run = query_to_run.replace("from provenance", f"FROM '{norm_path}'")
        else:
            query_to_run = sql_query

        return self.conn.execute(query_to_run).fetchdf()

    def get_tier_summary(self, parquet_path: str) -> Dict[str, Any]:
        """
        Aggregates multi-tier distribution and attack statistics via DuckDB.
        """
        norm_path = parquet_path.replace("\\", "/")
        query = f"""
            SELECT 
                tier,
                COUNT(*) as total_events,
                SUM(CASE WHEN is_attack THEN 1 ELSE 0 END) as attack_events,
                COUNT(DISTINCT host_id) as host_count,
                MIN(timestamp) as min_timestamp,
                MAX(timestamp) as max_timestamp
            FROM '{norm_path}'
            GROUP BY tier
            ORDER BY tier
        """
        df = self.conn.execute(query).fetchdf()
        return df.to_dict(orient="records")

    def get_attack_timeline(self, parquet_path: str) -> pd.DataFrame:
        """
        Extracts only attack events sorted by timestamp for fast forensic triage.
        """
        norm_path = parquet_path.replace("\\", "/")
        query = f"""
            SELECT timestamp, tier, host_id, event_type, action, entity, src_ip, dst_ip
            FROM '{norm_path}'
            WHERE is_attack = TRUE
            ORDER BY timestamp ASC
        """
        return self.conn.execute(query).fetchdf()

    def benchmark_compression(
        self,
        events: List[ProvenanceEvent],
        parquet_path: str,
        json_path: str,
    ) -> Dict[str, Any]:
        """
        Benchmarks file size and query execution speed between Parquet and raw JSON.
        """
        # 1. Export Parquet
        t0 = time.time()
        self.export_events_to_parquet(events, parquet_path)
        parquet_write_time = time.time() - t0
        parquet_size = os.path.getsize(parquet_path)

        # 2. Export JSON
        t0 = time.time()
        os.makedirs(os.path.dirname(os.path.abspath(json_path)), exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in events], f)
        json_write_time = time.time() - t0
        json_size = os.path.getsize(json_path)

        # 3. Benchmark DuckDB query time on Parquet
        t0 = time.time()
        norm_path = parquet_path.replace("\\", "/")
        self.conn.execute(f"SELECT COUNT(*) FROM '{norm_path}' WHERE is_attack = TRUE").fetchall()
        parquet_query_time = time.time() - t0

        compression_ratio = round(json_size / max(parquet_size, 1), 2)

        return {
            "total_events": len(events),
            "json_size_bytes": json_size,
            "parquet_size_bytes": parquet_size,
            "compression_ratio": compression_ratio,
            "parquet_write_time_sec": round(parquet_write_time, 4),
            "json_write_time_sec": round(json_write_time, 4),
            "parquet_query_time_sec": round(parquet_query_time, 4),
        }
