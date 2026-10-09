# CLOUD-M7 Architectural Specification

## 1. System Overview

CLOUD-M7 is a distributed forensic provenance framework tailored for heterogeneous computing architectures spanning **Edge**, **Fog**, and **Cloud** tiers. 

```
                                  +------------------------------+
                                  |         CLOUD TIER           |
                                  |  - Central Data Center       |
                                  |  - Global Datastores         |
                                  |  - Deep Causal Analytics     |
                                  +--------------^---------------+
                                                 |
                                         (E_network Fog->Cloud)
                                                 |
                                  +--------------v---------------+
                                  |          FOG TIER            |
                                  |  - Regional Gateways         |
                                  |  - Edge Cluster Nodes        |
                                  |  - Reduction & Aggregation   |
                                  |  - Choke-Point Containment   |
                                  +--------------^---------------+
                                                 |
                                         (E_network Edge->Fog)
                                                 |
                                  +--------------v---------------+
                                  |          EDGE TIER           |
                                  |  - Resource-Constrained IoT  |
                                  |  - Low-Latency Capture       |
                                  |  - In-Memory Privacy Filter  |
                                  +------------------------------+
```

---

## 2. Mathematical Formalization

### 2.1 Unified Multi-Tier Event Representation (Equation 1)
Every system observation across the infrastructure is normalized into a standardized tuple:
$$\mathcal{E}_i = \langle \text{UUID}_i, \tau_i, \text{Tier}_i, \text{HostID}_i, \text{Type}_i, \mathcal{P}_i, \pi_i \rangle$$

Where:
- $\text{UUID}_i$: Globally unique identifier for event $i$.
- $\tau_i$: Physical timestamp (UNIX epoch float).
- $\text{Tier}_i \in \{\text{Edge}, \text{Fog}, \text{Cloud}\}$: Architectural stratum where the event occurred.
- $\text{HostID}_i$: Unique identifier of the originating container, VM, or physical hardware.
- $\text{Type}_i \in \{\text{Process}, \text{File}, \text{Socket}, \text{API}\}$: Event classification.
- $\mathcal{P}_i$: Payload dictionary carrying granular attributes (e.g., process PID, file path, IP 5-tuple, API method).
- $\pi_i$: Set of causal parent event UUIDs establishing direct dependency edges.

In addition, each event computes a cryptographic SHA-256 integrity hash:
$$H_i = \text{SHA256}(\text{UUID}_i \parallel \tau_i \parallel \text{Tier}_i \parallel \text{HostID}_i \parallel \text{Type}_i \parallel \mathcal{P}_i \parallel \pi_i)$$
This ensures tamper-evidence and forensic non-repudiation across untrusted distributed tiers.

---

### 2.2 Tier-Adaptive Placement Optimization (Equation 2)
Forensic task placement $x = \{x_1, \dots, x_m\}$ (where each task $x_k \in \{\text{Edge}, \text{Fog}, \text{Cloud}\}$) is formulated as a multi-objective cost minimization problem:
$$\min_x J(x) = \alpha \cdot \text{Lat}(x) + \beta \cdot \text{BW}(x) + \gamma \cdot \text{Priv}(x) + \delta \cdot \text{Cost}(x)$$
$$\text{subject to } C_{edge} \le C_{max}$$

#### Component Definitions:
1. **Latency Cost $\text{Lat}(x)$:** Total execution and network propagation latency required to capture, process, and query forensic data. Filtering at Edge minimizes detection latency.
2. **Bandwidth Cost $\text{BW}(x)$:** Network egress volume consumed across tier boundaries. Moving filtering and reduction closer to the edge prevents raw event flooding.
3. **Privacy Risk Penalty $\text{Priv}(x)$:** Quantitative exposure penalty for transmitting unmasked raw telemetry outside the local device boundary.
4. **Infrastructure Cost $\text{Cost}(x)$:** Monetary expense incurred for cloud compute and storage resources.
5. **Edge Capacity Constraint $C_{edge} \le C_{max}$:** Ensures CPU and RAM footprint on edge devices do not exceed local operational thresholds ($<800$ millicores CPU and $<512$ MB RAM).

---

### 2.3 Cross-Tier Causal Provenance Fusion (Equation 3)
The global forensic causal graph $\mathcal{G}_{global} = (\mathcal{V}_{global}, \mathcal{E}_{global})$ is synthesized by unifying intra-tier subgraphs and cross-tier network flows:
$$\mathcal{G}_{global} = \mathcal{G}_{edge} \cup \mathcal{G}_{fog} \cup \mathcal{G}_{cloud} \cup \mathcal{E}_{network}$$

#### Cross-Tier Flow Correlation:
A directed edge $(u, v) \in \mathcal{E}_{network}$ is established between an outbound socket event $u$ at tier $T_1$ and an inbound socket event $v$ at tier $T_2$ ($T_1 \ne T_2$) if and only if:
1. **Network 5-Tuple Match:**
   $$\text{IP}_{src}(u) = \text{IP}_{src}(v) \quad \land \quad \text{IP}_{dst}(u) = \text{IP}_{dst}(v)$$
   $$\text{Port}_{dst}(u) = \text{Port}_{dst}(v) \quad \land \quad \text{Proto}(u) = \text{Proto}(v)$$
2. **Causal Temporal Ordering:**
   $$0 \le \tau(v) - \tau(u) \le \Delta t_{window}$$
   where $\Delta t_{window}$ accounts for maximum network transit latency.

---

### 2.4 Causal Attack Path Reconstruction
Given an alert or impact event $v_{target}$ (such as an unauthorized database exfiltration in the Cloud tier):
1. **Backward Causal Traversal:** Computes all ancestral predecessors:
   $$\text{Ancestors}(v_{target}) = \{ u \in \mathcal{V}_{global} \mid \text{Path}(u \leadsto v_{target}) \}$$
2. **Root Cause Identification:** Isolates the earliest entry point $v_{root} \in \text{Ancestors}(v_{target})$ such that $\text{in-degree}(v_{root}) = 0$ in the attack subgraph.
3. **Forward Blast Radius Traversal:** Computes all downstream impacted entities:
   $$\text{Descendants}(v_{root}) = \{ w \in \mathcal{V}_{global} \mid \text{Path}(v_{root} \leadsto w) \}$$
4. **Minimal Attack Chain Isolation:** Extracts the shortest causal path connecting $v_{root}$ to $v_{target}$, pruning away unrelated background operations.

---

### 2.5 [NOVELTY 1] Hyperparameter-Tuned Iterative Multi-Root Causal Discovery
Traditional single-pass backward traversal terminates immediately upon finding the first root event, leaving stealthy concurrent vectors undetected.

CLOUD-M7 introduces an iterative discovery loop parameterized by $(K_{max}, \epsilon, \lambda)$:
1. At iteration $k$, extract the active causal subgraph $\mathcal{G}_k \subseteq \mathcal{G}_{global} \setminus \bigcup_{j < k} \mathcal{P}_j$.
2. Identify root candidate $R_k$ and evaluate its marginal impact gain:
   $$\Delta I_k = \text{Impact}(R_k) \cdot e^{-\lambda \cdot k}$$
3. Check the convergence criterion:
   $$\text{If } \Delta I_k < \epsilon \quad \lor \quad k \ge K_{max} \implies \text{Terminate}$$
4. Append trajectory $\mathcal{P}_k$ and repeat.

This methodology guarantees discovery of secondary compromised hosts (e.g. `edge-sensor-02` firmware injection, `fog-gateway-01` token theft) while mathematically bounding computational complexity.

---

### 2.6 [NOVELTY 2] Multi-Sensor Convergent Graph & Articulation Choke-Point Analysis
In cyber-physical IoT deployments, concurrent attacks originate from disparate edge sensors and converge upon critical upstream assets.

1. **Multi-Sensor Convergence Engine:** Discovers all directed paths $\mathcal{P}_{multi} = \{p_1, \dots, p_m\}$ originating from edge sensors $S = \{s_1, \dots, s_n\}$ to the target Cloud asset $t$.
2. **Articulation Cut-Vertex Detection:** Identifies bottleneck vertices $v \in \mathcal{V}_{global}$ whose removal partitions $S$ from $t$.
3. **Containment Efficiency Metric:**
   $$E_{cut}(v) = \frac{|\{p \in \mathcal{P}_{multi} \mid v \in p\}|}{|\mathcal{P}_{multi}|}$$
4. **Empirical Choke Point:** The socket connection event on `fog-gateway-01` exhibits $E_{cut} = 1.0$ (100% containment), demonstrating that security operators can quarantine a single Fog gateway node to block all multi-sensor attack vectors simultaneously.
