# CLOUD-M7: 2-Year Capstone Project Roadmap (2026–2027)

**Academic Batch:** 2026–2027 (B.Tech Computer Science & Engineering)  
**Project:** CLOUD-M7: Tier-Adaptive Forensic Provenance

---

## Phase Breakdown Across 4 Semesters

```
+-------------------------------------------------------------------------------------------------+
|                                    2-YEAR CAPSTONE ROADMAP                                      |
+------------------------------------+------------------------------------------------------------+
| Semester 5 (Current - Review 1 & 2)| Foundation, Formal Schema, Simulator & Placement Optimizer|
| Semester 6                         | Containerized Docker Testbed, eBPF & Dataset Ingestion     |
| Semester 7                         | Reinforcement Learning (RL) Placement & Physical Testbeds  |
| Semester 8 (Final Review & Thesis) | Real-time SOC Web Dashboard, Final Paper & Thesis Defense   |
+------------------------------------+------------------------------------------------------------+
```

---

### Semester 5 (Year 1, Term 1): Architectural Foundation & Core Engine
* **Review 1 (Current Milestone):**
  - [x] Git repository initialization and project architecture setup.
  - [x] Standardized Multi-Tier Provenance Schema ($\mathcal{E}_i$) with cryptographic SHA-256 tamper-evident hashing.
  - [x] Multi-tier topology simulator modeling Edge (IoT), Fog (gateways), and Cloud (clusters).
  - [x] Simulated multi-stage Advanced Persistent Threat (APT): Edge Compromise $\rightarrow$ Fog Lateral Pivot $\rightarrow$ Cloud Data Exfiltration.
  - [x] Cross-Tier Causal Provenance Fusion Engine using NetworkX.
  - [x] Multi-objective Tier-Adaptive Placement Optimizer minimizing $J(x)$.
  - [x] Publication-quality visualization generator (`reports/attack_path_reconstruction.png`).
  - [x] Pytest automated test suite (8/8 tests passing).
* **Review 2 Deliverables:**
  - Formalization of provenance reduction algorithms (Full-Dependency Graph reduction, node folding).
  - Ingestion parser for standard JSON / CSV audit logs.
  - Initial conference paper draft.

---

### Semester 6 (Year 1, Term 2): Containerized Testbed & Real Datasets
* **Review 3 Deliverables:**
  - Transition from synthetic simulator to containerized multi-tier Docker environment:
    - Edge container (throttled vCPU & memory, simulating ARM/IoT node).
    - Fog container (regional Linux bridge with latency injection via `tc netem`).
    - Cloud container (Kubernetes microservice deployment with PostgreSQL database).
  - Ingestion of public security benchmark datasets:
    - **DARPA Transparent Computing (OpTC)** host provenance benchmark.
    - **TON_IoT & Edge-IIoTset** network & telemetry datasets.
    - **AWS CloudTrail & Kubernetes Audit Logs** for cloud control-plane events.
  - Systematic benchmarking of graph construction throughput (events/sec) and memory footprint.

---

### Semester 7 (Year 2, Term 1): Dynamic RL Placement & Physical Edge Hardware
* **Review 4 Deliverables:**
  - Implementation of Reinforcement Learning (RL) placement agent (e.g. Q-Learning / PPO) to dynamically adapt task allocation under shifting network bandwidth and edge load.
  - Physical testbed deployment:
    - Deploying edge capture agent on physical hardware (Raspberry Pi 4 / NVIDIA Jetson).
    - Deploying intermediate gateway on local edge cluster.
  - Privacy-preserving graph masking (differential privacy / k-anonymity on provenance attributes).

---

### Semester 8 (Year 2, Term 2): Interactive SOC Dashboard, Evaluation & Thesis
* **Final Review & Capstone Defense:**
  - Web-based interactive 3D graph visualization dashboard (React / Three.js or Streamlit + Cytoscape) for Security Operations Center (SOC) analysts.
  - Comprehensive empirical evaluation report:
    - Latency benchmarks across edge-fog-cloud hops.
    - Bandwidth savings analysis under varying event volumes (100 to 50,000 events/sec).
    - False positive / false negative rate of reconstructed attack paths.
  - Final Capstone Thesis submission and research paper submission to top-tier venue (e.g., IEEE S&P, ACM CCS, IEEE TIFS, or IEEE Cloud).
