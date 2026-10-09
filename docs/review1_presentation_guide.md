# CLOUD-M7: Complete Capstone Review 1 Presentation Slides & Defense Guide

**B.Tech Capstone Project | Department of Computer Science & Engineering**  
**Project Title:** CLOUD-M7: Tier-Adaptive Forensic Provenance: Distributed Attack-Path Reconstruction across Edge, Fog, and Cloud  
**Academic Batch:** 2026–2027  
**Candidate:** Dharshini  
**Repository:** https://github.com/DharshiniPES/cloud-m7  

---

## Complete Slide-by-Slide Presentation Content

### SLIDE 1: Title Slide
- **Title:** CLOUD-M7: Tier-Adaptive Forensic Provenance
- **Subtitle:** Distributed Attack-Path Reconstruction across Edge, Fog, and Cloud
- **Project Domain:** Cyber Forensics, Distributed Systems, Cloud & IoT Security
- **Candidate:** Dharshini | B.Tech CSE (Batch 2026–2027)
- **Evaluator Context:** Review 1 (Architecture, Placement Optimization, Iterative Causal Discovery, & Multi-Sensor Graph Analysis)
- **Speaker Notes:**
  > *"Good morning respected panel members. In modern computing, enterprise workloads and smart cyber-physical systems no longer live solely on isolated cloud servers. Applications span resource-constrained Edge sensors, intermediate Fog gateways, and massive Cloud datastores. My capstone project, CLOUD-M7, addresses an urgent, unsolved problem in cyber forensics: how to automatically reconstruct end-to-end multi-stage cyberattacks across all three tiers without overwhelming network bandwidth, causing high latency, or exposing private sensor data."*

---

### SLIDE 2: Problem Statement & Motivation
- **The Modern Multi-Tier Threat Landscape:** Advanced Persistent Threats (APTs) exploit small edge IoT sensors, pivot laterally through local Fog gateways, and ultimately exfiltrate high-value crown jewel databases in the Cloud.
- **Why Existing Forensic Approaches Fail:**
  1. **Host-Centric Forensic Tools (auditd, CamFlow, Sysmon):** Completely blind to cross-network pivots. Once an attacker leaves an edge host, the causal provenance chain breaks.
  2. **Centralized Cloud SIEM / Log Shipping (Splunk, CloudWatch):** Shipping gigabytes of raw sensor logs to the cloud causes network bandwidth saturation (90%+ waste), high detection latency, and severe privacy violations (GDPR/HIPAA).
  3. **Heterogeneous Event Disconnect:** Linux auditd syscalls, Fog container events, and Cloud REST API logs have disjoint schemas, making automated correlation historically impossible.
- **Speaker Notes:**
  > *"If an attacker compromises a smart sensor on the factory floor and pivots to our cloud database, existing tools leave analysts with isolated, fragmented logs. Centralized log shipping tries to solve this by dumping all raw data to the cloud, but that exhausts edge uplinks and exposes sensitive data. CLOUD-M7 solves this with intelligent tier-adaptive processing and unified graph fusion."*

---

### SLIDE 3: Literature Survey & Comparative Analysis
| Forensic Feature / Capability | Host Logs (`auditd`) | Centralized SIEM | SPADE / CamQuery | Prov-IoT | **CLOUD-M7 (Our Project)** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Cross-Tier Multi-Hop Tracking** | ❌ No | ⚠️ Partial (Manual) | ❌ No | ⚠️ Partial | **✅ Full Cross-Tier** |
| **Tier-Adaptive Task Placement** | ❌ No | ❌ No | ❌ No | ❌ No | **✅ Dynamic Cost Optimizer** |
| **Edge Bandwidth & Privacy Preservation** | ❌ No | ❌ No | ❌ No | ⚠️ Partial | **✅ 90% Bandwidth Reduction** |
| **Unified Cross-Tier Event Schema** | ❌ Disjoint | ⚠️ Proprietary | ⚠️ OS-only | ⚠️ IoT-only | **✅ Unified ($\mathcal{E}_i$) + SHA-256** |
| **Iterative Multi-Root Discovery** | ❌ Single-Pass | ❌ Rule-Based | ❌ Single-Pass | ❌ Single-Pass | **✅ Hyperparameter ($\Delta I_k$)** |
| **Multi-Sensor Choke-Point Detection** | ❌ No | ❌ No | ❌ No | ❌ No | **✅ Graph Articulation Cut** |
- **Speaker Notes:**
  > *"As summarized in Table 1, existing research addresses only individual slices of this problem. SPADE and CamQuery focus strictly on OS syscalls, while Prov-IoT targets smart homes. CLOUD-M7 is the first framework combining tier-adaptive placement optimization with multi-sensor convergent choke-point forensics."*

---

### SLIDE 4: Unified System Architecture & Forensic Event Schema
- **Mathematical Schema Definition:**
  $$\mathcal{E}_i = \langle \text{UUID}_i, \tau_i, \text{Tier}_i, \text{HostID}_i, \text{Type}_i, \mathcal{P}_i, \pi_i \rangle$$
  - $\text{UUID}_i$: Universally unique cryptographically secure event identifier.
  - $\tau_i$: High-precision ISO-8601 UTC timestamp.
  - $\text{Tier}_i \in \{\text{Edge}, \text{Fog}, \text{Cloud}\}$: Execution environment.
  - $\text{HostID}_i$: Physical machine, container, or VM identifier.
  - $\text{Type}_i \in \{\text{Process}, \text{File}, \text{Socket}, \text{API}\}$: Forensic event category.
  - $\mathcal{P}_i$: Action payload with network 5-tuple, process lineage, and resource paths.
  - $\pi_i = \text{SHA256}(\dots)$: Tamper-evident cryptographic hash ensuring non-repudiation.
- **Cross-Tier Socket Correlation:**
  - Network flows are linked using the bi-directional 5-tuple:
    $$\langle \text{src\_ip}, \text{src\_port}, \text{dst\_ip}, \text{dst\_port}, \text{proto} \rangle \quad \text{with temporal constraint } \tau_{send} \le \tau_{recv}$$
- **Speaker Notes:**
  > *"To stitch events across heterogeneous layers, we designed a unified mathematical schema. Each event captures the exact tier, host, type, and payload, accompanied by a SHA-256 tamper-evident hash to guarantee forensic integrity in court or audit reviews."*

---

### SLIDE 5: Dataset & Experimental Setup
- **Where the Dataset Comes From:**
  - **Realistic Multi-Tier Telemetry Generator:** Developed a dedicated distributed simulation engine (`cloud_m7.simulator`) modeling realistic operating system telemetry across 3 Edge nodes (`edge-sensor-01`, `edge-sensor-02`, `edge-actuator-03`), 1 Fog Gateway (`fog-gateway-01`), and 2 Cloud nodes (`cloud-api-prod`, `cloud-db-cluster`).
  - **Event Composition (70 Total Provenance Events):**
    - **40 Benign Noise Events:** Background IoT sensor readings, periodic gateway health checks, routine administrative cloud database queries.
    - **14 Primary Attack Events (Vector 1):** Memory-corruption exploit on IoT sensor $\rightarrow$ privilege escalation $\rightarrow$ credential exfiltration $\rightarrow$ lateral socket pivot to Fog $\rightarrow$ cloud service token theft $\rightarrow$ crown jewel database exfiltration.
    - **8 Secondary Attack Events (Vector 2):** Concurrent firmware command-injection exploit on `edge-sensor-02`.
    - **8 Actuator Control Events (Vector 3):** Unauthorized control-bus injection on `edge-actuator-03`.
- **Why Synthetic Telemetry for Review 1?**
  - Controlled ground truth is essential to mathematically verify that the causal reconstruction algorithm achieves 100% path recall and 0% false stitching before scaling.
  - **Future Roadmap Integration:** In Phase 2 (Semester 6), this pipeline will ingest public benchmarks (**DARPA OpTC**, **DARPA TC**, and **TON_IoT**).
- **Speaker Notes:**
  > *"For Review 1, rigorous evaluation requires known ground-truth causal links. We developed a multi-tier telemetry engine generating 70 realistic events: 40 benign background events mixed with a 3-vector Advanced Persistent Threat. This proves our algorithm isolates the true attack path without false positives."*

---

### SLIDE 6: Novelty Factor 1 — Tier-Adaptive Placement Optimization
- **Problem Formulation:**
  $$\min_x J(x) = \alpha \cdot \text{Lat}(x) + \beta \cdot \text{BW}(x) + \gamma \cdot \text{Priv}(x) + \delta \cdot \text{Cost}(x) \quad \text{s.t. } C_{edge} \le C_{max}$$
- **Optimal Task Partitioning:**
  - **Edge Tier:** Event Capture, Privacy Masking, Local Graph Reduction.
  - **Fog Tier:** Cross-Tier Subgraph Fusion & Socket Alignment.
  - **Cloud Tier:** Global Causal Analytics & Tamper-Evident Immutable Storage.
- **Quantitative Benchmark vs Centralized Baseline:**
  - **Bandwidth Consumption:** Reduced from **500.0 KB/s down to 50.0 KB/s (90.0% reduction)**.
  - **Processing Latency:** Reduced from **160.0 ms down to 20.0 ms (87.5% reduction)**.
  - **Edge Capacity Feasibility:** Uses 620.0 mcores CPU (well within the 800.0 mcores cap).
- **Speaker Notes:**
  > *"Instead of naively shipping everything to the cloud, our placement optimizer mathematically solves where each forensic task should execute. By performing privacy masking and reduction at the edge, we save 90% bandwidth and slash latency by 87.5%."*

---

### SLIDE 7: Novelty Factor 2 — Iterative Multi-Root Causal Discovery
- **The Core Forensic Limitation:** Traditional graph backward-traversal stops once a single root cause is found, missing stealthy secondary attack vectors and compromised supply chains.
- **Our Hyperparameter-Tuned Iterative Engine:**
  - **Hyperparameters:**
    - $K_{max}$: Maximum iteration ceiling (prevents infinite graph searching).
    - $\epsilon$: Diminishing return threshold (stops when new paths provide negligible marginal impact).
    - $\lambda$: Attenuation decay rate for historical discovery dampening.
  - **Marginal Impact Comparison Formulation:**
    $$\Delta I_k = \text{Impact}(R_k) \cdot e^{-\lambda \cdot k} \ge \epsilon$$
- **Empirical Discovery Results:**
  - **Iteration 1 ($\Delta I_1 = 102.30$):** Discovered Vector 1 (IoT sensor memory exploit on `edge-sensor-01`).
  - **Iteration 2 ($\Delta I_2 = 10.24$):** Discovered Vector 2 (Firmware command injection on `edge-sensor-02`).
  - **Iteration 3 ($\Delta I_3 = 3.77$):** Discovered Vector 3 (Stolen cloud token credential access on `fog-gateway-01`).
  - **Convergence:** Terminates cleanly when marginal impact drops below $\epsilon$.
- **Speaker Notes:**
  > *"Real-world attackers exploit multiple entry points simultaneously. Our iterative discovery algorithm uses hyperparameter tuning to find not just the primary entry point, but all concurrent attack roots, stopping dynamically when diminishing returns are reached."*

---

### SLIDE 8: Novelty Factor 3 — Interconnected Multi-Sensor Graph & Choke-Point Analysis
- **Multi-Sensor Convergent Trajectories:**
  - Trajectories originating from separate edge nodes (`edge-sensor-01`, `edge-sensor-02`, `edge-actuator-03`) converge across intermediate tiers toward the Cloud target.
- **Articulation Choke-Point (Cut-Vertex) Discovery:**
  $$\text{Containment Efficiency } E_{cut}(v) = \frac{|\{p \in \mathcal{P}_{multi} \mid v \in p\}|}{|\mathcal{P}_{multi}|}$$
- **Key Empirical Finding:**
  - Event `fog-gateway-01:socket_connect` achieves **$E_{cut} = 1.0$ (100.0% containment efficiency)** as an articulation bottleneck.
- **High-Impact Takeaway for Incident Responders:**
  - Instead of rushing to patch dozens of remote edge sensors during an active breach, incident responders can quarantine **a single choke-point on the Fog gateway**, instantly neutralizing all 3 attack trajectories.
- **Speaker Notes:**
  > *"When an enterprise is under attack from multiple sensor vectors, incident responders cannot patch 50 devices at once. Our engine computes graph articulation cut-vertices and identified that isolating just one socket on the Fog gateway cuts 100% of attack paths to the cloud database."*

---

### SLIDE 9: Visual Forensic Artifacts (Outputs)
- **Figure 1: Reconstructed Cross-Tier Forensic Graph (`reports/attack_path_reconstruction.png`)**
  - Visualizes Edge (Green), Fog (Orange), and Cloud (Purple) tiers.
  - Highlights the 14-hop causal attack path in bold red while pruning 80% background noise.
- **Figure 2: Interconnected Multi-Sensor Attack Graph (`reports/interconnected_attack_paths.png`)**
  - Shows converging attack paths originating from disparate edge devices.
  - Highlights critical containment choke points in **bright gold**, pinpointing the optimal isolation points.
- **Speaker Notes:**
  > *"Here are our generated high-resolution visualizations. Figure 1 shows the end-to-end 14-hop cross-tier path. Figure 2 shows the multi-sensor graph, where gold nodes indicate the minimal choke-points for immediate attack containment."*

---

### SLIDE 10: Quantitative Results & Test Verification Summary
- **Evaluation Metrics Summary:**
  | Metric | Centralized / Traditional | CLOUD-M7 Result | Improvement |
  | :--- | :---: | :---: | :---: |
  | **Network Bandwidth** | 500.0 KB/s | **50.0 KB/s** | **90.0% Reduction** |
  | **Ingestion Latency** | 160.0 ms | **20.0 ms** | **87.5% Reduction** |
  | **Noise Pruning** | 0.0% | **80.0%** | **4x Signal-to-Noise Ratio** |
  | **Choke-Point Containment** | N/A (Manual) | **100.0% (1 Node)** | **Optimal Isolation** |
  | **Attack Vectors Discovered** | 1 (Single) | **3 (Iterative)** | **Comprehensive Coverage** |
- **Automated Verification:** **13/13 passing automated unit & integration tests** (`pytest`).
- **Speaker Notes:**
  > *"Every claim in this presentation is backed by running code and 13 passing unit tests. We achieved a 90% reduction in bandwidth, 87.5% reduction in latency, and 80% noise filtering, proving both theoretical novelty and practical efficiency."*

---

### SLIDE 11: 2-Year Capstone Project Roadmap
- **Phase 1 (Completed — Review 1):**
  - Unified Schema $\mathcal{E}_i$, placement cost optimizer, NetworkX causal DAG fusion, iterative discovery loop, multi-sensor choke-point engine, 13 automated tests, and GitHub repository.
- **Phase 2 (Semester 6 — Review 2):**
  - Ingest public DARPA OpTC & TON_IoT datasets; build Docker-based multi-tier testbed with live Linux eBPF telemetry hooks.
- **Phase 3 (Semester 7 — Review 3):**
  - Deep Reinforcement Learning (Q-learning / PPO) for real-time dynamic placement adaptation under fluctuating network loads.
- **Phase 4 (Semester 8 — Final Review & Conference Submission):**
  - Hardware deployment on physical Raspberry Pi / Jetson nodes + AWS Cloud, interactive web SOC dashboard, manuscript submission to IEEE/ACM security conference.
- **Speaker Notes:**
  > *"This concludes Phase 1 of our 2-year capstone. Next semester, we will connect this pipeline to live eBPF kernel hooks and public DARPA datasets, culminating in a reinforcement learning placement engine and an IEEE publication."*

---

## 3. Defense Script & Anticipated Panel Questions

### Q1: "Where did your dataset come from? Why not use real malware logs?"
**Answer:**  
*"For Review 1, our primary objective was establishing mathematical correctness for cross-tier fusion, iterative discovery, and choke-point detection. Public datasets like DARPA OpTC or TON_IoT contain audit logs from single servers or IoT networks, but none provide correlated multi-tier telemetry spanning Edge, Fog, and Cloud simultaneously. Therefore, we developed a high-fidelity simulator generating 70 provenance events with verified ground truth. In Phase 2, we will ingest DARPA OpTC and map it to our unified schema $\mathcal{E}_i$."*

### Q2: "What is the exact novelty in your iterative discovery loop?"
**Answer:**  
*"Standard forensic algorithms (like SPADE or CamQuery) perform a single-pass backward BFS from a compromised sink. This inherently misses concurrent attack vectors—such as an attacker probing a secondary sensor or maintaining a dormant supply-chain foothold. Our algorithm introduces an iterative loop governed by hyperparameters ($K_{max}, \epsilon, \lambda$). It subtracts known causal paths, computes marginal impact gain $\Delta I_k$, and uncovers secondary attack roots until diminishing returns are mathematically reached."*

### Q3: "What is a 'choke point' and how does it help?"
**Answer:**  
*"In graph theory, a choke point is an articulation cut-vertex. When multiple IoT sensors are compromised simultaneously, incident responders cannot manually isolate dozens of devices in the field. Our algorithm discovered that the socket connect event on the Fog gateway has 100% containment efficiency ($E_{cut} = 1.0$), meaning severing this single gateway link isolates all 3 attack paths from reaching the cloud crown jewel."*

### Q4: "How do you ensure logs are not tampered with at the edge?"
**Answer:**  
*"Every event $\mathcal{E}_i$ contains a SHA-256 cryptographic digest $\pi_i$ computed over the tuple: `UUID || timestamp || host || action || payload`. In Phase 2, these hashes will be chained in a Merkle tree and anchored into tamper-evident cloud storage, guaranteeing that an attacker with root access cannot alter past forensic records undetected."*
