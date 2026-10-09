"""
Multi-Tier Topology Configuration and Virtual Node Modeling.

Models Edge, Fog, and Cloud nodes with network latency and bandwidth constraints.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from cloud_m7.schema.types import TierType


@dataclass
class SimulatedNode:
    """Represents a virtualized host, container, or IoT device."""
    host_id: str
    tier: TierType
    ip_address: str
    cpu_capacity_mcore: float
    memory_capacity_mb: float
    os_type: str = "Linux (Debian/RTOS)"
    open_ports: List[int] = field(default_factory=list)


@dataclass
class VirtualLink:
    """Models a virtual bridge connecting two tiers or nodes."""
    source_node: str
    target_node: str
    latency_ms: float
    bandwidth_mbps: float
    packet_loss_rate: float = 0.0


class MultiTierTopology:
    """
    Manages the multi-tier simulated architecture across Edge, Fog, and Cloud.
    """

    def __init__(self):
        self.nodes: Dict[str, SimulatedNode] = {}
        self.links: List[VirtualLink] = []
        self._setup_default_topology()

    def _setup_default_topology(self) -> None:
        """Initializes a standard 3-tier distributed testbed."""
        # 1. Edge Tier (Resource-constrained sensors)
        self.nodes["edge-sensor-01"] = SimulatedNode(
            host_id="edge-sensor-01",
            tier=TierType.EDGE,
            ip_address="192.168.1.50",
            cpu_capacity_mcore=1000.0,  # 1 vCPU
            memory_capacity_mb=512.0,   # 512 MB RAM
            open_ports=[1883, 8080],
        )
        self.nodes["edge-sensor-02"] = SimulatedNode(
            host_id="edge-sensor-02",
            tier=TierType.EDGE,
            ip_address="192.168.1.51",
            cpu_capacity_mcore=1000.0,
            memory_capacity_mb=512.0,
            open_ports=[1883],
        )
        self.nodes["edge-actuator-03"] = SimulatedNode(
            host_id="edge-actuator-03",
            tier=TierType.EDGE,
            ip_address="192.168.1.52",
            cpu_capacity_mcore=800.0,
            memory_capacity_mb=256.0,
            open_ports=[502, 1883],
        )

        # 2. Fog Tier (Local cluster gateway / micro-datacenter)
        self.nodes["fog-gateway-01"] = SimulatedNode(
            host_id="fog-gateway-01",
            tier=TierType.FOG,
            ip_address="10.0.1.1",
            cpu_capacity_mcore=4000.0,  # 4 vCPUs
            memory_capacity_mb=4096.0,  # 4 GB RAM
            open_ports=[22, 1883, 8080, 9090],
        )

        # 3. Cloud Tier (Data center backend services)
        self.nodes["cloud-api-prod"] = SimulatedNode(
            host_id="cloud-api-prod",
            tier=TierType.CLOUD,
            ip_address="172.16.0.10",
            cpu_capacity_mcore=16000.0,  # 16 vCPUs
            memory_capacity_mb=32768.0,  # 32 GB RAM
            open_ports=[443, 8443],
        )
        self.nodes["cloud-db-cluster"] = SimulatedNode(
            host_id="cloud-db-cluster",
            tier=TierType.CLOUD,
            ip_address="172.16.0.25",
            cpu_capacity_mcore=32000.0,
            memory_capacity_mb=65536.0,
            open_ports=[5432],
        )

        # Virtual Links with throttled bandwidth & latency
        self.links.append(
            VirtualLink(
                source_node="edge-sensor-01",
                target_node="fog-gateway-01",
                latency_ms=12.5,
                bandwidth_mbps=10.0,
            )
        )
        self.links.append(
            VirtualLink(
                source_node="fog-gateway-01",
                target_node="cloud-api-prod",
                latency_ms=65.0,
                bandwidth_mbps=100.0,
            )
        )
        self.links.append(
            VirtualLink(
                source_node="cloud-api-prod",
                target_node="cloud-db-cluster",
                latency_ms=1.2,
                bandwidth_mbps=1000.0,
            )
        )

    def get_node(self, host_id: str) -> Optional[SimulatedNode]:
        return self.nodes.get(host_id)
