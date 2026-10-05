"""
Standardized Provenance Event Representation for CLOUD-M7.

Mathematical Specification (Equation 1):
    E_i = <UUID_i, tau_i, Tier_i, HostID_i, Type_i, P_i, pi_i>

Where:
    - UUID_i: Globally unique identifier for event E_i
    - tau_i: Logical or physical timestamp of event occurrence
    - Tier_i in {Edge, Fog, Cloud}: Source architectural tier
    - HostID_i: Unique identifier of generating host / container / VM
    - Type_i in {Process, File, Socket, API}: Abstract event category
    - P_i: Event payload dictionary containing granular telemetry attributes
    - pi_i: Set of causal parent event UUIDs establishing provenance edges
"""

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from cloud_m7.schema.types import EventType, TierType


@dataclass
class ProvenanceEvent:
    """
    Unified forensic provenance event tuple across Edge, Fog, and Cloud tiers.
    """
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    tier: TierType = TierType.EDGE
    host_id: str = "edge-node-01"
    event_type: EventType = EventType.PROCESS
    payload: Dict[str, Any] = field(default_factory=dict)
    parents: List[str] = field(default_factory=list)
    tamper_hash: Optional[str] = None

    def __post_init__(self):
        # Normalize tier and event_type enums if passed as strings
        if isinstance(self.tier, str) and not isinstance(self.tier, TierType):
            self.tier = TierType(self.tier)
        if isinstance(self.event_type, str) and not isinstance(self.event_type, EventType):
            self.event_type = EventType(self.event_type)
        if self.parents is None:
            self.parents = []
        elif not isinstance(self.parents, list):
            self.parents = list(self.parents)
            
        if self.tamper_hash is None:
            self.tamper_hash = self.compute_integrity_hash()

    def compute_integrity_hash(self) -> str:
        """
        Computes cryptographic SHA-256 hash across event attributes to ensure
        forensic integrity and non-repudiation across distributed tiers.
        """
        hash_payload = {
            "uuid": self.uuid,
            "timestamp": round(self.timestamp, 6),
            "tier": self.tier.value if isinstance(self.tier, TierType) else str(self.tier),
            "host_id": self.host_id,
            "event_type": self.event_type.value if isinstance(self.event_type, EventType) else str(self.event_type),
            "payload": self.payload,
            "parents": sorted(self.parents)
        }
        serialized = json.dumps(hash_payload, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def add_parent(self, parent_uuid: str) -> None:
        """Adds a causal parent event identifier and updates integrity hash."""
        if parent_uuid not in self.parents:
            self.parents.append(parent_uuid)
            self.tamper_hash = self.compute_integrity_hash()

    @property
    def is_network_event(self) -> bool:
        """Indicates if the event involves cross-host or cross-tier communication."""
        return self.event_type == EventType.SOCKET

    @property
    def network_tuple(self) -> Optional[Tuple[str, int, str, int, str]]:
        """
        Returns (src_ip, src_port, dst_ip, dst_port, protocol) if available in payload.
        Used for cross-tier E_network correlation.
        """
        if not self.is_network_event:
            return None
        src_ip = self.payload.get("src_ip", "")
        src_port = int(self.payload.get("src_port", 0))
        dst_ip = self.payload.get("dst_ip", "")
        dst_port = int(self.payload.get("dst_port", 0))
        proto = self.payload.get("protocol", "TCP")
        return (src_ip, src_port, dst_ip, dst_port, proto)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes event to Python dictionary."""
        return {
            "uuid": self.uuid,
            "timestamp": self.timestamp,
            "tier": self.tier.value,
            "host_id": self.host_id,
            "event_type": self.event_type.value,
            "payload": self.payload,
            "parents": self.parents,
            "tamper_hash": self.tamper_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvenanceEvent":
        """Instantiates ProvenanceEvent from a dictionary."""
        return cls(
            uuid=data["uuid"],
            timestamp=data["timestamp"],
            tier=TierType(data["tier"]),
            host_id=data["host_id"],
            event_type=EventType(data["event_type"]),
            payload=data.get("payload", {}),
            parents=data.get("parents", []),
            tamper_hash=data.get("tamper_hash"),
        )

    def to_json(self) -> str:
        """Serializes to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "ProvenanceEvent":
        """Deserializes from formatted JSON string."""
        return cls.from_dict(json.loads(json_str))
