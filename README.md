# CLOUD-M7: Tier-Adaptive Forensic Provenance

### Distributed Attack-Path Reconstruction across Edge, Fog, and Cloud
**B.Tech Capstone Project | Academic Batch: 2026–2027**  
**Department of Computer Science & Engineering**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Review 1 Prototype](https://img.shields.io/badge/Capstone-Review%201%20Verified-brightgreen.svg)]()

---

## 1. Executive Summary

Modern distributed enterprise and IoT architectures span three heterogeneous tiers:
1. **Edge Tier:** Resource-constrained devices, sensors, and micro-controllers.
2. **Fog Tier:** Intermediate regional cluster gateways and micro-datacenters.
3. **Cloud Tier:** Centralized high-capacity cloud data centers and global datastores.

When multi-stage cyberattacks (such as Advanced Persistent Threats) strike these distributed environments, forensic evidence becomes fragmented across isolated silos. Forwarding all raw audit events to the cloud incurs prohibitive bandwidth costs, excessive latency, privacy violations, and massive storage overhead.

**CLOUD-M7** resolves this fundamental dilemma through two core contributions:
- **Tier-Adaptive Placement Optimization:** Dynamically distributes forensic capture, filtering, reduction, and deep querying across Edge, Fog, and Cloud by minimizing a multi-objective cost function:
  $$\min_x J(x) = \alpha \cdot \text{Lat}(x) + \beta \cdot \text{BW}(x) + \gamma \cdot \text{Priv}(x) + \delta \cdot \text{Cost}(x) \quad \text{s.t. } C_{edge} \le C_{max}$$
- **Cross-Tier Causal Provenance Fusion Engine:** Stitches disconnected provenance subgraphs across tiers via network socket flow correlation ($E_{network}$):
  $$\mathcal{G}_{global} = \mathcal{G}_{edge} \cup \mathcal{G}_{fog} \cup \mathcal{G}_{cloud} \cup \mathcal{E}_{network}$$
  Isolates the minimal causal attack chain from initial entry to target impact using backward and forward causal traversal.

---

## 2. Multi-Tier Architecture & Attack Scenario

```
+---------------------------------------------------------------------------------------+
|                                    CLOUD-M7 ARCHITECTURE                              |
+---------------------------------------------------------------------------------------+
|  [Edge Tier: Devices/IoT]      |  [Fog Tier: Gateways]       |  [Cloud Tier: Data Centers]   |
|  * Low-latency capture         |  * Aggregation & reduction  |  * Global datastores          |
|  * In-memory privacy filter    |  * Bandwidth optimization   |  * Deep causal analytics      |
+--------------------------------+-----------------------------+-------------------------------+
                                  \                           /
                                   \                         /
            +---------------------------------------------------------------+
            |     Tier-Adaptive Placement & Cross-Tier Graph Fusion Engine  |
            +---------------------------------------------------------------+
                                           |
                                           v
            End-to-End Reconstructed Attack Trajectory:
            Edge Compromise  --->  Fog Lateral Pivot  --->  Cloud Data Exfiltration
```

### Validated Attack Scenario:
1. **Edge Sensor Compromise:** Attacker triggers memory corruption in `/usr/bin/iot_agent`, spawns elevated `/bin/sh`, drops reconnaissance script, reads gateway credentials, and opens outbound TCP socket `192.168.1.50:48210 -> 10.0.1.1:8080`.
2. **Fog Gateway Lateral Pivot:** Fog gateway accepts socket connection ($E_{network}$), attacker spawns unauthorized Python process, scrapes cloud IAM service-account token, and initiates pivot HTTPS socket `10.0.1.1:52110 -> 172.16.0.10:443`.
3. **Cloud Data Exfiltration:** Cloud API accepts ingress connection ($E_{network}$), authenticates stolen token, queries customer database dumping 50,000 records, archives to disk, and exfiltrates to adversary C2 IP `198.51.100.77:443`.

---

## 3. Repository Structure

```
capstone/
├── cloud_m7/                   # Core Python package
│   ├── schema/                 # Multi-Tier Event Representation (Equation 1)
│   │   ├── event.py            # Standardized ProvenanceEvent tuple
│   │   └── types.py            # Tier, Event, and Action enums
│   ├── placement/              # Tier-Adaptive Placement Optimization (Equation 2)
│   │   ├── cost_model.py       # Multi-objective formulation J(x)
│   │   └── optimizer.py        # Constraint solver and trade-off analyzer
│   ├── fusion/                 # Cross-Tier Causal Provenance Fusion (Equation 3)
│   │   ├── causal_graph.py     # NetworkX DAG stitching & E_network correlation
│   │   └── attack_path.py      # Backward/Forward causal traversal engine
│   ├── simulator/              # Simulated Multi-Tier Testbed
│   │   ├── topology.py         # Virtual Edge, Fog, Cloud hosts & links
│   │   └── attack_scenario.py  # Realistic multi-stage APT & benign generator
│   ├── visualization/          # High-resolution forensic visualizer
│   │   └── graph_plot.py       # Tier-zoned provenance graph generator
│   └── cli.py                  # Command-line interface
├── docs/                       # Capstone documentation
│   ├── architecture.md         # Detailed architectural breakdown
│   ├── review1_presentation_guide.md # Presentation script & Q&A for Review 1
│   └── roadmap_2year.md        # 2-year capstone implementation roadmap
├── scripts/                    # Helper and evaluation scripts
│   ├── run_demo.py             # Single-command demonstration runner
│   └── generate_evaluation.py  # Benchmark generator matching Table 1
├── tests/                      # Pytest automated test suite
│   ├── test_schema.py          # Event tuple and serialization tests
│   ├── test_placement.py       # Placement optimization & constraint tests
│   ├── test_fusion.py          # Cross-tier correlation and DAG tests
│   └── test_end_to_end.py      # Full pipeline integration tests
├── reports/                    # Generated attack graph diagrams and artifacts
│   └── attack_path_reconstruction.png
├── pyproject.toml              # Build and package metadata
├── requirements.txt            # Python dependencies
└── README.md                   # This project guide
```

---

## 4. Getting Started

### Prerequisites
- Python 3.10 or higher
- Git

### Installation
1. Clone or navigate into the repository:
   ```bash
   cd C:\Users\Dharshini\capstone
   ```
2. Activate the pre-configured virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(Or create a new one: `python -m venv .venv` and `pip install -r requirements.txt`)*

---

## 5. Running the Review 1 Prototype

### 1. Run Complete End-to-End Demo (One Command)
```powershell
python scripts/run_demo.py
```
This executes:
- Synthetic multi-tier telemetry generation (benign workloads + multi-stage APT).
- Cross-tier network socket correlation ($E_{network}$).
- Unified DAG fusion across Edge, Fog, and Cloud.
- Backward and forward causal traversal to reconstruct the exact 14-step attack path.
- Noise filtering: prunes >75% of background benign noise.
- Generates high-resolution visualization at `reports/attack_path_reconstruction.png`.
- Solves Tier-Adaptive Placement Optimization, demonstrating **90% bandwidth reduction** and **87.5% latency reduction**.

### 2. Run Comparative Evaluation (Matches Paper Table 1)
```powershell
python scripts/generate_evaluation.py
```

### 3. Run Automated Tests
```powershell
pytest -v
```
All 8 unit and integration tests pass cleanly.

---

## 6. Review 1 Checklist & Deliverables

- [x] Git repository initialized with clean history and `.gitignore`.
- [x] Unified Multi-Tier Provenance Schema ($E_i$) implemented with cryptographic hashing and JSON serialization.
- [x] Multi-Tier Topology & Attack Simulator implemented (Edge -> Fog -> Cloud).
- [x] Cross-Tier Causal Provenance Fusion Engine implemented using NetworkX.
- [x] Backward & Forward causal graph traversal isolating the minimal attack path.
- [x] Multi-objective tier placement optimizer implemented ($Lat, BW, Priv, Cost$).
- [x] High-resolution visualization generated (`reports/attack_path_reconstruction.png`).
- [x] Comprehensive review presentation guide and 2-year roadmap documented.
