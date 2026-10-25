"""
DARPA OpTC (Operational Transparent Computing) Dataset Adapter.

Normalizes enterprise-scale audit logs from DARPA OpTC (JSON/JSONL/CAR format)
into CLOUD-M7 Canonical Provenance Events (Equation 1: E_i).

Supported Event Types:
    - PROCESS_CREATE / PROCESS_START -> EventType.PROCESS (exec/fork)
    - FILE_WRITE / FILE_READ / FILE_MODIFY -> EventType.FILE (write/read/modify)
    - NETWORK_FLOW / NETWORK_CONNECT -> EventType.SOCKET (connect/accept)
"""

import json
import os
from typing import Any, Dict, List, Optional
import uuid

from cloud_m7.adapters.base import BaseDatasetAdapter
from cloud_m7.schema.event import ProvenanceEvent
from cloud_m7.schema.types import EventType, TierType


class DarpaOpTCAdapter(BaseDatasetAdapter):
    """Adapter for DARPA OpTC JSON/JSONL enterprise audit logs."""

    dataset_name: str = "DARPA_OpTC"

    def can_handle(self, sample_line_or_data: Any) -> bool:
        if isinstance(sample_line_or_data, str):
            # Check string directly for OpTC signatures
            lower = sample_line_or_data.lower()
            if "optc" in lower:
                return True
            for line in sample_line_or_data.splitlines():
                line = line.strip()
                if line:
                    try:
                        parsed = json.loads(line)
                        if isinstance(parsed, dict) and any(k in parsed for k in ["object", "action", "command_line", "image_path", "datum"]):
                            return True
                    except Exception:
                        pass
            try:
                sample_line_or_data = json.loads(sample_line_or_data)
            except Exception:
                return False

        if isinstance(sample_line_or_data, list) and sample_line_or_data:
            sample_line_or_data = sample_line_or_data[0]

        if isinstance(sample_line_or_data, dict):
            # Check for OpTC CAR / CDM indicators
            keys = set(sample_line_or_data.keys())
            if any(k in keys for k in ["object", "action", "command_line", "image_path", "datum"]):
                return True
            if "event_type" in sample_line_or_data and any(x in str(sample_line_or_data.get("event_type", "")).upper() for x in ["PROCESS", "FLOW", "FILE"]):
                return True
        return False

    def parse_records(
        self,
        data_source: Any,
        max_events: Optional[int] = None,
        default_tier: TierType = TierType.CLOUD,
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

        prev_pid_map: Dict[str, str] = {}  # pid -> last event uuid

        for line in lines:
            if max_events and len(events) >= max_events:
                break

            record = line if isinstance(line, dict) else None
            if record is None:
                try:
                    record = json.loads(line)
                except Exception:
                    continue

            # Extract fields
            obj = str(record.get("object", record.get("event_type", "PROCESS"))).upper()
            action_raw = str(record.get("action", "")).lower()
            props = record.get("properties", {}) if isinstance(record.get("properties"), dict) else record

            ts = float(record.get("timestamp", record.get("time", 0.0)))
            if ts > 1e12:  # nanoseconds or milliseconds to seconds
                ts = ts / 1e9 if ts > 1e14 else ts / 1e3
            if ts == 0.0:
                ts = 1600000000.0 + len(events) * 0.5

            host_id = str(record.get("hostname", record.get("host_id", "optc-cloud-host-01")))
            evt_uuid = str(record.get("id", record.get("uuid", f"optc-{uuid.uuid4().hex[:12]}")))

            # Map EventType & Action
            event_type = EventType.PROCESS
            action = "exec"
            entity = props.get("image_path", props.get("command_line", "process"))
            is_attack = bool(record.get("is_attack", False) or "red_team" in str(record).lower() or "mimikatz" in str(record).lower())

            if "FILE" in obj:
                event_type = EventType.FILE
                action = "write" if "write" in action_raw or "create" in action_raw else "read"
                entity = props.get("file_path", props.get("path", "/var/log/syslog"))
            elif "FLOW" in obj or "NET" in obj or "SOCKET" in obj:
                event_type = EventType.SOCKET
                action = "connect" if "connect" in action_raw or "out" in action_raw else "accept"
                entity = f"{props.get('dst_ip', '192.168.1.100')}:{props.get('dst_port', 443)}"
            else:
                action = "exec" if "start" in action_raw or "create" in action_raw else "fork"
                entity = props.get("command_line", props.get("image_path", "cmd.exe"))

            payload = {
                "action": action,
                "entity": entity,
                "is_attack": is_attack,
                "raw_action": action_raw,
                "dataset_source": "DARPA_OpTC",
            }

            if event_type == EventType.SOCKET:
                payload["src_ip"] = props.get("src_ip", "10.0.1.15")
                payload["src_port"] = int(props.get("src_port", 49152))
                payload["dst_ip"] = props.get("dst_ip", "10.0.2.100")
                payload["dst_port"] = int(props.get("dst_port", 443))
                payload["protocol"] = props.get("protocol", "TCP")

            # Link causality via process lineage
            parents = []
            pid = str(props.get("pid", ""))
            ppid = str(props.get("ppid", ""))
            if ppid in prev_pid_map:
                parents.append(prev_pid_map[ppid])
            elif prev_pid_map and len(events) > 0 and len(parents) == 0:
                # Local sequential thread link
                parents.append(events[-1].uuid)

            if pid:
                prev_pid_map[pid] = evt_uuid

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
