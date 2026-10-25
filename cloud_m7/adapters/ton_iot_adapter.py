"""
TON_IoT (UNSW Canberra Cyber) Dataset Adapter.

Normalizes authentic IoT telemetry and heterogeneous network attack logs from
the TON_IoT benchmark into CLOUD-M7 Canonical Provenance Events (Equation 1: E_i).

Supported Modalities:
    - IoT Sensor Telemetry (Temperature, Vibration, Pressure, Motion, Light) -> EventType.FILE / PROCESS
    - Industrial Network Traffic (MQTT, Modbus, HTTP, TCP/UDP) -> EventType.SOCKET
    - Attack Labels: DoS, DDoS, Ransomware, Backdoor, Injection, Scanning
"""

import csv
import io
import json
from typing import Any, Dict, List, Optional
import uuid

from cloud_m7.adapters.base import BaseDatasetAdapter
from cloud_m7.schema.event import ProvenanceEvent
from cloud_m7.schema.types import EventType, TierType


class TonIotAdapter(BaseDatasetAdapter):
    """Adapter for UNSW TON_IoT CSV/JSON sensor telemetry & network PCAP logs."""

    dataset_name: str = "TON_IoT"

    def can_handle(self, sample_line_or_data: Any) -> bool:
        if isinstance(sample_line_or_data, str):
            lower = sample_line_or_data.lower()
            if any(k in lower for k in ["ton_iot", "conn_state", "src_ip", "dst_ip", "ts", "label"]):
                if "," in sample_line_or_data or "\t" in sample_line_or_data:
                    return True
            try:
                data = json.loads(sample_line_or_data)
                if isinstance(data, dict) and any(k in data for k in ["temperature", "humidity", "motion", "conn_state", "service"]):
                    return True
            except Exception:
                pass
        elif isinstance(sample_line_or_data, dict):
            if any(k in sample_line_or_data for k in ["temperature", "humidity", "motion", "conn_state", "service"]):
                return True
        return False

    def parse_records(
        self,
        data_source: Any,
        max_events: Optional[int] = None,
        default_tier: TierType = TierType.EDGE,
    ) -> List[ProvenanceEvent]:
        events: List[ProvenanceEvent] = []
        rows: List[Dict[str, Any]] = []

        if isinstance(data_source, str):
            if "\n" in data_source:
                # String content
                # Try CSV first
                try:
                    reader = csv.DictReader(io.StringIO(data_source))
                    rows = list(reader)
                except Exception:
                    pass
                if not rows or None in rows[0]:
                    # Try JSON Lines
                    rows = []
                    for line in data_source.splitlines():
                        line = line.strip()
                        if line:
                            try:
                                rows.append(json.loads(line))
                            except Exception:
                                pass
            else:
                # File path
                try:
                    with open(data_source, "r", encoding="utf-8", errors="ignore") as f:
                        first_line = f.readline()
                        f.seek(0)
                        if "," in first_line or "\t" in first_line:
                            delimiter = "\t" if "\t" in first_line and "," not in first_line else ","
                            reader = csv.DictReader(f, delimiter=delimiter)
                            rows = list(reader)
                        else:
                            for line in f:
                                line = line.strip()
                                if line:
                                    try:
                                        rows.append(json.loads(line))
                                    except Exception:
                                        pass
                except Exception:
                    pass
        elif isinstance(data_source, list):
            rows = data_source

        prev_edge_uuid: Optional[str] = None

        for row in rows:
            if max_events and len(events) >= max_events:
                break

            # Timestamp extraction
            ts_raw = row.get("ts", row.get("timestamp", row.get("time", 0.0)))
            try:
                ts = float(ts_raw)
            except Exception:
                ts = 1600000000.0 + len(events) * 0.2

            if ts > 1e12:
                ts = ts / 1e9 if ts > 1e14 else ts / 1e3
            if ts == 0.0:
                ts = 1600000000.0 + len(events) * 0.2

            # Identify attack
            label_raw = str(row.get("type", row.get("label", "normal"))).lower()
            is_attack = label_raw not in ["normal", "0", "false", "benign"]

            src_ip = str(row.get("src_ip", row.get("id.orig_h", "192.168.1.50")))
            dst_ip = str(row.get("dst_ip", row.get("id.resp_h", "10.0.1.1")))
            src_port = int(float(row.get("src_port", row.get("id.orig_p", 1883))))
            dst_port = int(float(row.get("dst_port", row.get("id.resp_p", 1883))))
            proto = str(row.get("proto", "TCP")).upper()
            service = str(row.get("service", "mqtt")).lower()

            # Classify tier
            tier = default_tier
            host_id = f"ton-iot-{src_ip.replace('.', '-')}"

            # If telemetry fields exist (temperature, etc.), treat as sensor Process/File
            is_telemetry = any(k in row for k in ["temperature", "humidity", "motion", "light", "pressure"])
            evt_uuid = f"ton-{uuid.uuid4().hex[:12]}"

            if is_telemetry:
                event_type = EventType.FILE
                action = "write" if is_attack else "read"
                entity = f"/sensors/{service}/data.log"
                payload = {
                    "action": action,
                    "entity": entity,
                    "is_attack": is_attack,
                    "attack_type": label_raw,
                    "telemetry": {k: row[k] for k in ["temperature", "humidity", "motion", "light", "pressure"] if k in row},
                    "dataset_source": "TON_IoT",
                }
            else:
                event_type = EventType.SOCKET
                action = "connect" if is_attack else "send"
                entity = f"{dst_ip}:{dst_port}"
                payload = {
                    "action": action,
                    "entity": entity,
                    "src_ip": src_ip,
                    "src_port": src_port,
                    "dst_ip": dst_ip,
                    "dst_port": dst_port,
                    "protocol": proto,
                    "service": service,
                    "is_attack": is_attack,
                    "attack_type": label_raw,
                    "dataset_source": "TON_IoT",
                }

            parents = [prev_edge_uuid] if prev_edge_uuid else []
            prev_edge_uuid = evt_uuid

            event = ProvenanceEvent(
                uuid=evt_uuid,
                timestamp=ts,
                tier=tier,
                host_id=host_id,
                event_type=event_type,
                payload=payload,
                parents=parents,
            )
            events.append(event)

        return events
