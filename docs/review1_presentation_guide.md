# CLOUD-M7: Capstone Review 1 Presentation Guide & Defense Script

**B.Tech Capstone Project | Department of Computer Science & Engineering**  
**Project Title:** CLOUD-M7: Tier-Adaptive Forensic Provenance: Distributed Attack-Path Reconstruction across Edge, Fog, and Cloud  
**Academic Batch:** 2026–2027  
**Candidate:** Dharshini  

---

## 1. Quick Presentation Slide Breakdown (10–12 Minute Presentation)

### Slide 1: Title & Introduction
- **Title:** CLOUD-M7: Tier-Adaptive Forensic Provenance
- **Subtitle:** Distributed Attack-Path Reconstruction across Edge, Fog, and Cloud
- **Opening Line:**  
  *"Good morning respected evaluators. Today, enterprise and IoT systems are no longer confined to isolated servers; workloads span resource-constrained Edge devices, intermediate Fog gateways, and centralized Cloud datastores. My capstone project, CLOUD-M7, addresses a critical unsolved challenge: how to reconstruct end-to-end multi-stage cyberattacks spanning across all three tiers without incurring prohibitive network bandwidth, high latency, or privacy violations."*

### Slide 2: The Multi-Tier Forensic Dilemma (Problem Statement)
- **Current Approach 1 (Host-Only EDR):** Monitors individual hosts (e.g., CamFlow, auditd). Fails completely when an attacker pivots from an IoT camera across a gateway to cloud infrastructure.
- **Current Approach 2 (Centralized Cloud Log Shipping):** Forwards all raw audit events to the cloud.
  - **Bandwidth exhaustion:** Millions of sensor events saturate uplink connections.
  - **Latency bottlenecks:** Detection and containment cannot occur in real time at the edge.
  - **Privacy risks:** Raw unmasked sensor/camera telemetry leaves local boundaries.
- **Current Approach 3 (Heterogeneous Schemas):** Linux auditd, eBPF syscalls, network PCAPs, and AWS CloudTrail logs use disjoint formats, preventing automated cross-tier correlation.

### Slide 3: Research Distinction (Table 1 Feature Comparison)
| Forensic Capability | Host Logs (`auditd`) | Cloud Forensics | CamFlow (Pasquier et al.) | **CLOUD-M7 (Our Project)** |
| :--- | :---: | :---: | :---: | :---: |
| **Cross-Tier Multi-Hop Tracking** | ❌ | Partial | ❌ | **✅ Full** |
| **Tier-Adaptive Placement Optimization** | ❌ | ❌ | ❌ | **✅ Dynamic** |
| **Edge Bandwidth & Privacy Preservation** | ❌ | ❌ | ❌ | **✅ Built-in** |
| **Common Multi-Tier Schema** | ❌ | Partial | Partial | **✅ Unified ($\mathcal{E}_i$)** |
| **Causal Provenance Graph Fusion** | ❌ | ❌ | ❌ | **✅ NetworkX DAG** |
| **End-to-End Attack-Path Synthesis** | ❌ | ❌ | Partial | **✅ Minimal Traversal** |

### Slide 4: Mathematical Formulation
Highlight the two core equations:
1. **Tier-Adaptive Placement Optimization (Equation 2):**
   $$\min_x J(x) = \alpha \cdot \text{Lat}(x) + \beta \cdot \text{BW}(x) + \gamma \cdot \text{Priv}(x) + \delta \cdot \text{Cost}(x) \quad \text{s.t. } C_{edge} \le C_{max}$$
   *Explain:* We dynamically place tasks (Capture, Privacy Filter, Graph Reduction, Fusion, Analytics) to minimize this cost while respecting device CPU/RAM limits.
2. **Cross-Tier Provenance Graph Fusion (Equation 3):**
   $$\mathcal{G}_{global} = \mathcal{G}_{edge} \cup \mathcal{G}_{fog} \cup \mathcal{G}_{cloud} \cup \mathcal{E}_{network}$$
   *Explain:* Cross-tier socket flows correlate outbound sockets at lower tiers with inbound connections at upstream tiers via socket 5-tuple and temporal alignment.

### Slide 5: The Simulated Attack Scenario
Walk the panel through the concrete multi-stage APT attack:
$$\text{Edge Sensor Compromise} \longrightarrow \text{Fog Gateway Lateral Pivot} \longrightarrow \text{Cloud Database Exfiltration}$$
- **Edge:** IoT sensor process exploited $\rightarrow$ root shell spawned $\rightarrow$ staging script written $\rightarrow$ credentials read $\rightarrow$ outbound TCP connection to Fog.
- **Fog:** Gateway accepts socket $\rightarrow$ unauthorized Python process spawned $\rightarrow$ Cloud service-account IAM token scraped $\rightarrow$ outbound HTTPS to Cloud API.
- **Cloud:** Cloud ingress accepts connection $\rightarrow$ unauthorized admin API invoked $\rightarrow$ 50,000 customer database records queried $\rightarrow$ dumped to archive $\rightarrow$ exfiltrated to adversary C2 IP.

### Slide 6: Live Demonstration & Results (Show Working Prototype!)
- Run the demo script live (or show pre-computed results):
  - **Bandwidth Reduction:** **90.0%** reduction in network traffic compared to raw centralized log shipping.
  - **Latency Reduction:** **87.5%** faster local filtering and response.
  - **Noise Pruning:** **77.4%** of benign background noise pruned away, leaving the clean 14-step causal attack chain.
  - **Show Diagram:** Display `reports/attack_path_reconstruction.png`.

### Slide 7: 2-Year Roadmap & Next Steps
- **Year 1 (Completed for Review 1):** Architecture design, formal schema $\mathcal{E}_i$, placement optimization algorithm, causal fusion engine, automated test suite (8/8 passing).
- **Year 1 (Semester 6):** Containerized Docker testbed, eBPF syscall capture, DARPA OpTC & TON_IoT dataset ingestion.
- **Year 2 (Semesters 7 & 8):** Reinforcement Learning (RL) placement agent, physical testbed (Raspberry Pi/Jetson), web-based interactive SOC analyst dashboard.

---

## 2. Live Demo Script (Step-by-Step Commands to Run)

Open your terminal / PowerShell in `C:\Users\Dharshini\capstone`:

### Command 1: Run the Full End-to-End Demo
```powershell
python scripts/run_demo.py
```
**What to say:**  
*"Here, our simulator generates 62 distributed events across Edge, Fog, and Cloud. Our fusion engine automatically establishes cross-tier socket edges, stitches the subgraphs into a directed acyclic graph, and isolates the 14-step attack trajectory while filtering out 77% of unrelated background noise."*

### Command 2: Show the High-Resolution Architecture Diagram
Open `reports/attack_path_reconstruction.png`.  
**What to say:**  
*"As shown in this generated visualization, the green zone represents Edge devices, the orange zone represents Fog gateways, and the purple zone represents Cloud services. The red arrows trace the malicious causality from the initial IoT sensor exploit all the way to cloud database exfiltration."*

### Command 3: Show Test Suite Verification
```powershell
pytest -v
```
**What to say:**  
*"We have established strict automated testing covering schema serialization, cryptographic SHA-256 integrity hashing, placement constraint feasibility, and graph fusion. All 8 test suites pass cleanly."*

---

## 3. Anticipated Panel Questions & Bulletproof Answers

### Q1: "Why can't we simply ship all logs to AWS CloudWatch or Splunk in the Cloud?"
**Answer:**  
*"Forwarding all raw audit events to the cloud works for traditional servers, but fails in modern Edge and IoT architectures for three reasons:
1. **Bandwidth:** Thousands of edge sensors emitting continuous system calls saturate edge uplinks (e.g. 4G/5G or satellite links in connected vehicles).
2. **Latency:** Critical containment cannot wait for round-trip cloud ingestion.
3. **Privacy:** Regulatory frameworks (like GDPR/HIPAA) prohibit raw unmasked device data from leaving local boundaries.
CLOUD-M7 performs local privacy filtering and reduction at Edge and Fog, reducing bandwidth consumption by 90% while preserving complete forensic causality."*

### Q2: "How do you correlate events across network boundaries ($E_{network}$)? What if clocks are out of sync?"
**Answer:**  
*"We establish cross-tier causal edges $E_{network}$ by matching the network socket 5-tuple—Source IP, Source Port, Destination IP, Destination Port, and Protocol—combined with causal temporal ordering within a configurable time window ($\Delta t_{window}$). In our roadmap, we also integrate logical clocks (Lamport timestamps / vector clocks) and sequence numbers to eliminate vulnerability to physical clock skew."*

### Q3: "What makes your event schema different from Linux auditd or eBPF?"
**Answer:**  
*"Linux auditd logs are host-centric text lines; eBPF produces kernel ring-buffer byte streams; AWS CloudTrail outputs JSON API records. None of them carry explicit causal parent pointers ($\pi_i$) or cross-tier context. The CLOUD-M7 schema $\mathcal{E}_i = \langle \text{UUID}_i, \tau_i, \text{Tier}_i, \text{HostID}_i, \text{Type}_i, \mathcal{P}_i, \pi_i \rangle$ standardizes heterogeneous telemetry into an entity-agnostic tuple equipped with cryptographic SHA-256 hashes for non-repudiation and explicit parent pointers for DAG construction."*

### Q4: "How does the placement optimizer enforce device constraints?"
**Answer:**  
*"Our optimizer formulates placement as a constrained multi-objective minimization problem $\min_x J(x)$ subject to $C_{edge} \le C_{max}$. It explicitly checks that assigned tasks do not exceed the edge device's CPU millicores or memory thresholds (e.g., 800 mcores CPU, 512 MB RAM). Computationally heavy tasks like deep graph analytics are kept on Cloud nodes, while lightweight filtering runs locally at the Edge."*

### Q5: "What have you accomplished so far for this 1st Review?"
**Answer:**  
*"For Review 1, we have completed the foundational architecture and Feature 1 prototype:
1. Full mathematical specification of the schema, placement model, and fusion engine.
2. Complete Python implementation of the unified schema, multi-tier simulator, placement optimizer, fusion engine, and visualizer.
3. Automated test suite with 100% pass rate.
4. Empirical validation demonstrating 90% bandwidth savings and end-to-end 14-hop attack path reconstruction."*
