# CLOUD-M7: Tier-Adaptive Forensic Provenance

### Distributed Attack-Path Reconstruction across Edge, Fog, and Cloud
**B.Tech Capstone Project | Academic Batch: 2026–2027**  
**Department of Computer Science & Engineering**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 13 Passed](https://img.shields.io/badge/pytest-13%20passed-brightgreen.svg)]()
[![Status: Review 1 Verified](https://img.shields.io/badge/Capstone-Review%201%20Novelties%20Verified-brightgreen.svg)]()

---

## 1. Executive Summary

Modern distributed enterprise and IoT architectures span three heterogeneous tiers:
1. **Edge Tier:** Resource-constrained devices, sensors, and micro-controllers.
2. **Fog Tier:** Intermediate regional cluster gateways and micro-datacenters.
3. **Cloud Tier:** Centralized high-capacity cloud data centers and global datastores.

When multi-stage cyberattacks (such as Advanced Persistent Threats) strike these distributed environments, forensic evidence becomes fragmented across isolated silos. Forwarding all raw audit events to the cloud incurs prohibitive bandwidth costs (uplink exhaustion), excessive latency, privacy violations (GDPR/HIPAA), and massive storage overhead.

**CLOUD-M7** resolves this fundamental dilemma through four interconnected contributions:
- **Tier-Adaptive Placement Optimization:** Dynamically distributes forensic capture, filtering, reduction, and deep querying across Edge, Fog, and Cloud by minimizing a multi-objective cost function:
  $$\min_x J(x) = \alpha \cdot \text{Lat}(x) + \beta \cdot \text{BW}(x) + \gamma \cdot \text{Priv}(x) + \delta \cdot \text{Cost}(x) \quad \text{s.t. } C_{edge} \le C_{max}$$
  Achieves **90.0% bandwidth savings** and **87.5% latency reduction**.
- **Cross-Tier Causal Provenance Fusion Engine:** Stitches disconnected provenance subgraphs across tiers via network socket flow correlation ($\mathcal{E}_{network}$):
  $$\mathcal{G}_{global} = \mathcal{G}_{edge} \cup \mathcal{G}_{fog} \cup \mathcal{G}_{cloud} \cup \mathcal{E}_{network}$$
- **[NOVELTY 1] Hyperparameter-Tuned Iterative Multi-Root Discovery:** Traditional forensic tools execute a single-pass backward BFS and stop at the first root cause found, missing stealthy secondary attack vectors. Our engine iteratively discovers multiple concurrent entry points using hyperparameter tuning ($K_{max}, \epsilon, \lambda$) and marginal impact comparison:
  $$\Delta I_k = \text{Impact}(R_k) \cdot e^{-\lambda \cdot k} \ge \epsilon$$
- **[NOVELTY 2] Interconnected Multi-Sensor Graph & Critical Choke-Point Analysis:** Traces convergent attack paths originating from multiple heterogeneous edge sensors to the cloud target. Using graph articulation cut-point theory, it pinpoints critical bottleneck nodes:
  $$E_{cut}(v) = \frac{|\{p \in \mathcal{P}_{multi} \mid v \in p\}|}{|\mathcal{P}_{multi}|}$$
  Discovered that isolating `fog-gateway-01:socket_connect` achieves **100.0% containment efficiency** against all 3 multi-sensor attack paths.

---

## 2. Multi-Tier Architecture & Attack Scenario

```
+---------------------------------------------------------------------------------------+
|                                    CLOUD-M7 ARCHITECTURE                              |
+---------------------------------------------------------------------------------------+
|  [Edge Tier: Sensors/Actuators]|  [Fog Tier: Gateways]       |  [Cloud Tier: Data Centers]   |
|  * edge-sensor-01              |  * fog-gateway-01           |  * cloud-api-prod             |
|  * edge-sensor-02              |  * In-network socket fusion |  * cloud-db-cluster           |
|  * edge-actuator-03            |  * Choke-point containment  |  * Crown jewel datastores     |
|  * In-memory privacy filter    |  * Bandwidth optimization   |  * Deep causal analytics      |
+--------------------------------+-----------------------------+-------------------------------+
                                  \                           /
                                   \                         /
            +---------------------------------------------------------------+
            |     Tier-Adaptive Placement & Cross-Tier Graph Fusion Engine  |
            +---------------------------------------------------------------+
                                           |
                                           v
            End-to-End Reconstructed Convergent Attack Trajectories:
  [Edge Sensor 01] --(Vector 1)--> [Fog Gateway 01] ----> [Cloud Database Exfiltration]
  [Edge Sensor 02] --(Vector 2)-->        ^
  [Edge Actuator 03] -(Vector 3)->        | (★ 100% Containment Choke-Point ★)
```

### Validated Attack Scenario:
1. **Edge Sensor Compromise (Vector 1):** Attacker triggers memory corruption in `/usr/bin/iot_agent` on `edge-sensor-01`, spawns elevated `/bin/sh`, drops staging script, reads gateway credentials, and opens outbound TCP socket `192.168.1.50:48210 -> 10.0.1.1:8080`.
2. **Concurrent Vectors (Vector 2 & 3):** Concurrent firmware command-injection exploit on `edge-sensor-02` and unauthorized control-bus injection on `edge-actuator-03`.
3. **Fog Gateway Lateral Pivot:** Fog gateway accepts socket connection ($\mathcal{E}_{network}$), attacker executes unauthorized Python process, scrapes cloud IAM service-account token, and initiates pivot HTTPS socket `10.0.1.1:52110 -> 172.16.0.10:443`.
4. **Cloud Data Exfiltration:** Cloud API accepts ingress connection, authenticates stolen token, queries customer database dumping 50,000 records, archives to disk, and exfiltrates to adversary C2 IP `198.51.100.77:443`.

---

## 3. Dataset & Experimental Setup

- **Origin of Dataset:** High-fidelity multi-tier telemetry engine (`cloud_m7/simulator/`) modeling realistic operating system telemetry (Linux syscalls, POSIX file operations, BSD sockets, REST APIs).
- **Dataset Composition (70 Total Provenance Events):**
  - **40 Benign Events:** Background sensor telemetry, periodic gateway keep-alives, routine administrative database queries.
  - **14 Primary Attack Events (Vector 1):** End-to-end memory corruption exploit chain from edge to cloud.
  - **8 Secondary Attack Events (Vector 2):** Concurrent edge firmware injection.
  - **8 Secondary Attack Events (Vector 3):** Edge actuator control-bus manipulation.
- **Controlled Ground Truth:** Essential for Review 1 to mathematically prove 100% path recall and 0% false positive stitching.
- **Benchmark Roadmap:** Designed to ingest **DARPA OpTC**, **DARPA TC**, and **TON_IoT** benchmarks in Phase 2 (Semester 6).

---

## 4. Repository Structure

```
capstone/
├── cloud_m7/                   # Core Python package
│   ├── schema/                 # Unified Multi-Tier Event Representation (Tuple E_i)
│   │   ├── event.py            # Standardized ProvenanceEvent tuple + SHA-256 hash
│   │   └── types.py            # Tier, Event, and Action enums
│   ├── placement/              # Tier-Adaptive Placement Optimization
│   │   ├── cost_model.py       # Multi-objective cost formulation J(x)
│   │   └── optimizer.py        # Constraint solver and trade-off analyzer
│   ├── fusion/                 # Cross-Tier Causal Provenance Fusion Engine
│   │   ├── causal_graph.py     # NetworkX DAG stitching & E_network correlation
│   │   ├── attack_path.py      # Backward/Forward causal traversal engine
│   │   ├── iterative_discovery.py # [NOVELTY 1] Iterative Multi-Root Discovery Engine
│   │   └── interconnected_paths.py# [NOVELTY 2] Multi-Sensor Graph & Choke-Point Engine
│   ├── simulator/              # Simulated Multi-Tier Testbed
│   │   ├── topology.py         # Virtual Edge, Fog, Cloud hosts & links
│   │   └── attack_scenario.py  # Realistic multi-stage APT & benign generator
│   ├── visualization/          # High-resolution forensic visualizer
│   │   └── graph_plot.py       # Reconstructed and interconnected graph plotters
│   └── cli.py                  # Command-line interface with stages 1 to 7
├── docs/                       # Capstone documentation
│   ├── architecture.md         # Detailed architectural specification
│   ├── review1_presentation_guide.md # Complete slide-by-slide deck & defense script
│   └── roadmap_2year.md        # 2-year capstone implementation roadmap
├── scripts/                    # Demonstration, evaluation, & presentation scripts
│   ├── run_demo.py             # Single-command demonstration runner
│   ├── generate_evaluation.py  # Benchmark generator matching paper Table 1
│   └── generate_presentation.py# Automated PowerPoint deck generator (.pptx)
├── tests/                      # Pytest automated test suite (13 tests)
│   ├── test_schema.py          # Event tuple and serialization tests
│   ├── test_placement.py       # Placement optimization & constraint tests
│   ├── test_fusion.py          # Cross-tier correlation and DAG tests
│   ├── test_iterative.py       # [NOVELTY 1] Iterative discovery & hyperparameter tests
│   ├── test_interconnected_paths.py # [NOVELTY 2] Multi-sensor & choke-point tests
│   └── test_end_to_end.py      # Full pipeline integration tests
├── reports/                    # Generated presentation, diagrams, and evaluation artifacts
│   ├── CLOUD-M7_Review1_Presentation.pptx # Professional 16:9 PowerPoint Deck
│   ├── attack_path_reconstruction.png    # Reconstructed 14-hop causal path
│   └── interconnected_attack_paths.png   # Multi-sensor graph with gold choke points
├── run_demo.bat                # Windows 1-click demo launcher
├── run_evaluation.bat          # Windows 1-click evaluation table launcher
├── run_tests.bat               # Windows 1-click pytest launcher
├── generate_presentation.bat  # Windows 1-click PowerPoint generator
├── pyproject.toml              # Build and package metadata
├── requirements.txt            # Python dependencies (includes python-pptx)
└── README.md                   # This comprehensive project guide
```

---

## 5. Getting Started & Running the Prototype

### Prerequisites
- Python 3.11 or higher
- Git

### One-Click Windows Launchers:
Double click or run any of the batch files:
- `.\run_demo.bat`: Runs full end-to-end simulation, optimization, novelties, and graph plotting.
- `.\run_evaluation.bat`: Prints literature comparison matrix and quantitative placement trade-offs.
- `.\run_tests.bat`: Executes all 13 automated unit and integration tests.
- `.\generate_presentation.bat`: Generates the PowerPoint presentation (`reports/CLOUD-M7_Review1_Presentation.pptx`).

### Direct PowerShell Commands:
```powershell
cd C:\Users\Dharshini\capstone

# 1. Run full demonstration pipeline
.\.venv\Scripts\python.exe scripts\run_demo.py

# 2. Display literature benchmark & optimization table
.\.venv\Scripts\python.exe scripts\generate_evaluation.py

# 3. Run automated tests (13/13 passing)
.\.venv\Scripts\pytest.exe -v

# 4. Generate PowerPoint deck
.\.venv\Scripts\python.exe scripts\generate_presentation.py
```

---

## 6. Quantitative Results Summary

| Metric | Centralized Baseline | CLOUD-M7 Result | Improvement |
| :--- | :---: | :---: | :---: |
| **Network Bandwidth** | 500.0 KB/s | **50.0 KB/s** | **90.0% Reduction (10x)** |
| **Ingestion Latency** | 160.0 ms | **20.0 ms** | **87.5% Faster** |
| **Privacy Exposure Penalty** | 120.0 pts | **5.0 pts** | **95.8% Mitigation** |
| **Noise Pruning Ratio** | 0.0% | **80.0%** | **4x Signal-to-Noise Ratio** |
| **Choke-Point Containment** | Manual (Host-by-Host) | **100.0% (1 Node)** | **Optimal Isolation** |
| **Discovered Attack Roots** | 1 (Single) | **3 (Iterative)** | **Comprehensive Coverage** |
| **Automated Tests** | - | **13 Passed in 0.88s** | **100% Code Quality** |

---

## 7. Review 1 Checklist & Deliverables

- [x] Remote GitHub repository configured and synced: `https://github.com/DharshiniPES/cloud-m7`
- [x] Unified Multi-Tier Provenance Schema ($\mathcal{E}_i$) with SHA-256 integrity hashing and JSON serialization.
- [x] Multi-Tier Topology & Attack Simulator across 3 Edge nodes, 1 Fog Gateway, and 2 Cloud nodes (70 events).
- [x] Tier-Adaptive Placement Optimization algorithm ($\min J(x)$) saving 90% bandwidth and 87.5% latency.
- [x] Cross-Tier Causal Provenance Fusion Engine with NetworkX DAG stitching ($\mathcal{G}_{global}$).
- [x] **[Novelty 1]** Hyperparameter-tuned iterative multi-root discovery engine ($K_{max}, \epsilon, \lambda, \Delta I_k$).
- [x] **[Novelty 2]** Multi-sensor interconnected attack graph & articulation choke-point analysis (100% containment).
- [x] Visual high-resolution graph generators (`reports/attack_path_reconstruction.png` and `reports/interconnected_attack_paths.png`).
- [x] Professional 16:9 PowerPoint presentation deck (`reports/CLOUD-M7_Review1_Presentation.pptx`).
- [x] 13 automated pytest unit and integration tests passing cleanly.
- [x] 2-year capstone roadmap (Phase 1 to Phase 4) documented.
