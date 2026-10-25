"""
Aposemat IoT-23 Dataset Adapter.

Normalizes real IoT malware infection captures (Mirai, Torii, Kenjiro, Hakai, Gafgyt)
from the Stratosphere Lab IoT-23 benchmark into CLOUD-M7 Canonical Provenance Events.

Format: Zeek (Bro) conn.log TSV / CSV or labeled JSON records.
"""

import csv
import io
import json
from typing import Any, Dict, List, Optional
import uuid

from cloud_m7.adapters.base import BaseDatasetAdapter
from cloud_m7.schema.event import ProvenanceEvent
from cloud_m7.schema.types import EventType, TierType


class IoT23Adapter(BaseDatasetAdapter):
    """Adapter for Aposemat IoT-23 Zeek conn.log network malware flows."""

    dataset_name: str = "IoT_23"

    def can_handle(self, sample_line_or_data: Any) -> bool:
        if isinstance(sample_line_or_data, str):
            lower = sample_line_or_data.lower()
            if any(k in lower for k in ["id.orig_h", "id.resp_h", "orig_bytes", "resp_bytes", "conn_state", "detailed-label"]):
                return True
            if "iot-23" in lower:
                return True
        elif isinstance(sample_line_or_data, dict):
            if any(k in sample_line_or_data for k in ["id.orig_h", "id.resp_h", "detailed-label"]):
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
            lines = [l for l in data_source.splitlines() if not l.startswith("#") and l.strip()]
            cleaned_text = "\n".join(lines)
            if "\t" in cleaned_text:
                reader = csv.DictReader(io.StringIO(cleaned_text), delimiter="\t")
                rows = list(reader)
            elif "," in cleaned_text:
                reader = csv.DictReader(io.StringIO(cleaned_text), delimiter=",")
                rows = list(reader)
            else:
                for line in lines:
                    try:
                        rows.append(json.loads(line))
                    except Exception:
                        pass
        elif isinstance(data_source, list):
            rows = data_source

        prev_uuid: Optional[str] = None

        for row in rows:
            if max_events and len(events) >= max_events:
                break

            # Handle Zeek field naming
            src_ip = str(row.get("id.orig_h", row.get("src_ip", "192.168.1.190")))
            dst_ip = str(row.get("id.resp_h", row.get("dst_ip", "10.0.1.1")))
            
            try:
                src_port = int(float(row.get("id.orig_p", row.get("src_port", 49152))))
            except Exception:
                src_port = 49152

            try:
                dst_port = int(float(row.get("id.resp_p", row.get("dst_port", 23))))
            except Exception:
                dst_port = 23

            proto = str(row.get("proto", "TCP")).upper()
            service = str(row.get("service", "-")).lower()
            if service == "-":
                service = "telnet" if dst_port in [23, 2323] else ("http" if dst_port in [80, 8080] else "raw_tcp")

            ts_raw = row.get("ts", row.get("timestamp", 0.0))
            try:
                ts = float(ts_raw)
            except Exception:
                ts = 1600000000.0 + len(events) * 0.1

            label_raw = str(row.get("label", row.get("detailed-label", "Benign"))).lower()
            is_attack = "benign" not in label_raw and label_raw not in ["-", "0", "false"]

            evt_uuid = f"iot23-{uuid.uuid4().hex[:12]}"
            host_id = f"iot23-pi-{src_ip.replace('.', '-')}"

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
                "malware_label": row.get("detailed-label", row.get("label", "Mirai")),
                "dataset_source": "Aposemat_IoT_23",
            }

            parents = [prev_uuid] if prev_uuid else []
            prev_uuid = evt_uuid

            event = ProvenanceEvent(
                uuid=evt_uuid,
                timestamp=ts,
                tier=default_tier,
                host_id=host_id,
                event_type=EventType.SOCKET,
                payload=payload,
                parents=parents,
            )
            events.append(event)

        return events
