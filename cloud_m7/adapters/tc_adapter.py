"""
DARPA Transparent Computing (TC) CDM Dataset Adapter.

Normalizes DARPA TC Common Data Model (CDM) records from THEIA, Cadets, and TRACE
into CLOUD-M7 Canonical Provenance Events (Equation 1: E_i).

Supported CDM Records:
    - EVENT_FORK, EVENT_EXECUTE, EVENT_CLONE -> EventType.PROCESS
    - EVENT_OPEN, EVENT_READ, EVENT_WRITE, EVENT_UNLINK -> EventType.FILE
    - EVENT_CONNECT, EVENT_ACCEPT, EVENT_SENDTO, EVENT_RECVFROM -> EventType.SOCKET
"""

import json
import os
from typing import Any, Dict, List, Optional
import uuid

from cloud_m7.adapters.base import BaseDatasetAdapter
from cloud_m7.schema.event import ProvenanceEvent
from cloud_m7.schema.types import EventType, TierType


class DarpaTCAdapter(BaseDatasetAdapter):
    """Adapter for DARPA TC CDM JSON / BBN CDM records."""

    dataset_name: str = "DARPA_TC"

    def can_handle(self, sample_line_or_data: Any) -> bool:
        if isinstance(sample_line_or_data, str):
            lower = sample_line_or_data.lower()
            if "darpa_tc" in lower or "tc-" in lower or "predicateobject" in lower:
                return True
            try:
                sample_line_or_data = json.loads(sample_line_or_data)
            except Exception:
                for line in sample_line_or_data.splitlines():
                    line = line.strip()
                    if line:
                        try:
                            parsed = json.loads(line)
                            if isinstance(parsed, dict) and (str(parsed.get("type", "")).startswith("EVENT_") or "event" in parsed):
                                return True
                        except Exception:
                            pass
                return False

        if isinstance(sample_line_or_data, list) and sample_line_or_data:
            sample_line_or_data = sample_line_or_data[0]

        if isinstance(sample_line_or_data, dict):
            # Check for DARPA TC CDM markers
            if "type" in sample_line_or_data and str(sample_line_or_data["type"]).startswith("EVENT_"):
                return True
            if "event" in sample_line_or_data or "datum" in sample_line_or_data:
                return True
            if "subject" in sample_line_or_data and "predicateObject" in sample_line_or_data:
                return True
        return False

    def parse_records(
        self,
        data_source: Any,
        max_events: Optional[int] = None,
        default_tier: TierType = TierType.FOG,
    ) -> List[ProvenanceEvent]:
        events: List[ProvenanceEvent] = []
        lines = []

        if isinstance(data_source, str):
            try:
                parsed_all = json.loads(data_source)
                if isinstance(parsed_all, list):
                    lines = parsed_all
                elif isinstance(parsed_all, dict):
                    lines = [parsed_all]
            except Exception:
                if os.path.exists(data_source) and os.path.isfile(data_source):
                    try:
                        with open(data_source, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            try:
                                parsed_f = json.loads(content)
                                lines = parsed_f if isinstance(parsed_f, list) else [parsed_f]
                            except Exception:
                                lines = [l.strip() for l in content.splitlines() if l.strip()]
                    except Exception:
                        lines = [data_source]
                elif "\n" in data_source:
                    lines = [l.strip() for l in data_source.splitlines() if l.strip()]
                else:
                    lines = [data_source]
        elif isinstance(data_source, list):
            lines = data_source

        subj_parent_map: Dict[str, str] = {}

        for line in lines:
            if max_events and len(events) >= max_events:
                break

            record = line if isinstance(line, dict) else None
            if record is None:
                try:
                    record = json.loads(line)
                except Exception:
                    continue

            inner = record.get("event", record.get("datum", record))
            evt_type_str = str(record.get("type", inner.get("type", "EVENT_EXECUTE"))).upper()

            ts = float(inner.get("timestampNanos", inner.get("timestamp", 0.0)))
            if ts > 1e12:
                ts = ts / 1e9 if ts > 1e14 else ts / 1e3
            if ts == 0.0:
                ts = 1600000100.0 + len(events) * 0.4

            host_id = str(inner.get("hostId", inner.get("hostname", "tc-theia-gateway-01")))
            evt_uuid = str(inner.get("uuid", f"tc-{uuid.uuid4().hex[:12]}"))
            subject_id = str(inner.get("subject", ""))

            # Classify CDM event
            event_type = EventType.PROCESS
            action = "exec"
            entity = inner.get("predicateObjectPath", inner.get("predicateObject", "process"))
            is_attack = bool(inner.get("is_attack", False) or "attack" in str(inner).lower() or "bovia" in str(inner).lower() or "firefox" in str(inner).lower())

            if any(k in evt_type_str for k in ["OPEN", "READ", "WRITE", "MODIFY", "UNLINK", "FILE"]):
                event_type = EventType.FILE
                action = "write" if "WRITE" in evt_type_str else "read"
            elif any(k in evt_type_str for k in ["CONNECT", "ACCEPT", "SEND", "RECV", "SOCKET", "NET"]):
                event_type = EventType.SOCKET
                action = "connect" if "CONNECT" in evt_type_str or "SEND" in evt_type_str else "accept"
            else:
                action = "exec" if "EXEC" in evt_type_str else "fork"

            payload = {
                "action": action,
                "entity": str(entity),
                "is_attack": is_attack,
                "cdm_type": evt_type_str,
                "dataset_source": "DARPA_TC",
            }

            if event_type == EventType.SOCKET:
                payload["src_ip"] = inner.get("src_ip", "10.0.1.20")
                payload["src_port"] = int(inner.get("src_port", 50000))
                payload["dst_ip"] = inner.get("dst_ip", "172.16.0.10")
                payload["dst_port"] = int(inner.get("dst_port", 8080))
                payload["protocol"] = inner.get("protocol", "TCP")

            parents = []
            if subject_id and subject_id in subj_parent_map:
                parents.append(subj_parent_map[subject_id])
            elif events:
                parents.append(events[-1].uuid)

            if subject_id:
                subj_parent_map[subject_id] = evt_uuid

            event = ProvenanceEvent(
                uuid=evt_uuid,
                timestamp=ts,
                tier=default_tier,
                host_id=host_id,
                event_type=event_type,
                payload=payload,
                parents=parents,
            )
            events.append(event)

        return events
