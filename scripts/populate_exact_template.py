"""
CLOUD-M7: Populate Exact PES University PPT Template
Loads the user's exact official template 'C:\\Users\\Dharshini\\Downloads\\ppt.pptx',
preserves every single original shape, PES logo, position, and layout 100%,
and populates the exact placeholders with complete, high-quality technical content.
"""

from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = Path(r"C:\Users\Dharshini\Downloads\ppt.pptx")
OUTPUT_IN_CAPSTONE = ROOT_DIR / "reports" / "CLOUD-M7_PES_Exact_Template_Review1.pptx"
OUTPUT_IN_DOWNLOADS = Path(r"C:\Users\Dharshini\Downloads\CLOUD_M7_Review1_Exact_Template.pptx")

# Color constants for text formatting
NAVY = RGBColor(27, 43, 80)
BLUE = RGBColor(30, 64, 175)
DARK = RGBColor(30, 41, 59)


def populate_template():
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found at: {TEMPLATE_PATH}")

    prs = pptx.Presentation(str(TEMPLATE_PATH))
    print(f"[+] Loaded exact template: {TEMPLATE_PATH} (Total slides: {len(prs.slides)})")

    # Iterate over slides and populate exact shapes
    for idx, slide in enumerate(prs.slides, 1):
        # 1. Update common header & footer across all content slides
        for shape in slide.shapes:
            if shape.has_text_frame:
                txt = shape.text_frame.text.strip()
                # Update "Title of the Project" header
                if "Title of the Project" in txt:
                    shape.text_frame.text = "CLOUD-M7: Tier-Adaptive Forensic Provenance"
                    p = shape.text_frame.paragraphs[0]
                    p.font.name = "Segoe UI"
                    p.font.size = Pt(11)
                    p.font.bold = True
                    p.font.color.rgb = NAVY
                # Update "name1_name2_name3_name4" footer
                elif "name1_name2_name3_name4" in txt:
                    shape.text_frame.text = "Dharshini  [PES1UG24CS...]"
                    p = shape.text_frame.paragraphs[0]
                    p.font.name = "Segoe UI"
                    p.font.size = Pt(10)
                    p.font.color.rgb = DARK

        # 2. Slide-Specific Content Population
        if idx == 1:
            # SLIDE 1: Title Slide
            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text_frame.text
                    if "B.Tech. in CSE" in txt:
                        shape.text_frame.text = (
                            "B.Tech. in CSE (2024-2028)\n"
                            "Semester- V\n"
                            "UE24CS320A - Capstone Project Phase-1\n"
                            "Review-1"
                        )
                        for p in shape.text_frame.paragraphs:
                            p.font.name = "Segoe UI"
                            p.font.bold = True
                            p.font.color.rgb = NAVY
                    elif "Project Title" in txt:
                        shape.text_frame.text = (
                            "Project Title   : CLOUD-M7: Tier-Adaptive Forensic Provenance\n"
                            "Project ID      : UE24CS320A-CAP-CLOUD-M7\n"
                            "Project Guide   : [Internal Faculty Guide, Department of CSE]\n"
                            "Project Team    : Dharshini  [PES1UG24CS...]"
                        )
                        for p in shape.text_frame.paragraphs:
                            p.font.name = "Segoe UI"
                            p.font.size = Pt(12)
                            p.font.color.rgb = DARK
                            p.font.bold = "Project Title" in p.text or "Project Team" in p.text

        elif idx == 2:
            # SLIDE 2: Outline
            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text_frame.text
                    if "Problem Statement" in txt and "Scope" in txt:
                        shape.text_frame.text = (
                            "- Problem Statement\n"
                            "- Introduction\n"
                            "- Scope and Feasibility study\n"
                            "- Applications/Use cases\n"
                            "- Background Study (5 Key Research Papers)\n"
                            "- Implementation (Architecture, Novelties & Live Demo)\n"
                            "- Capstone (Phase-I & Phase-II) Project Timeline\n"
                            "- Any other information & Verification"
                        )
                        for p in shape.text_frame.paragraphs:
                            p.font.name = "Segoe UI"
                            p.font.size = Pt(13)
                            p.font.color.rgb = DARK

        elif idx == 3:
            # SLIDE 3: Problem Statement
            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text_frame.text
                    if "Well defined problem statement" in txt:
                        shape.text_frame.text = (
                            "1. The Distributed Forensic Dilemma:\n"
                            "Modern enterprise workloads span three heterogeneous tiers: Edge IoT sensors, intermediate Fog gateways, and centralized Cloud datastores. When Advanced Persistent Threats (APTs) strike, forensic evidence is fragmented across isolated silos.\n\n"
                            "2. Failure of Host EDR (Pillar 1):\n"
                            "Tools like Linux auditd and CamFlow monitor single OS kernels. When an attacker pivots across a network socket, the causal chain breaks permanently.\n\n"
                            "3. Failure of Centralized SIEM (Pillar 2):\n"
                            "Forwarding all raw audit events to the cloud exhausts constrained edge uplinks (>500 KB/s), incurs high detection latency (160ms+), and violates privacy laws (GDPR/HIPAA).\n\n"
                            "4. Heterogeneous Schemas (Pillar 3):\n"
                            "Incompatible log formats between Edge syscalls, Fog container streams, and Cloud REST APIs prevent automated end-to-end causal reconstruction."
                        )
                        for p in shape.text_frame.paragraphs:
                            p.font.name = "Segoe UI"
                            p.font.size = Pt(10.5)
                            p.font.color.rgb = DARK

        elif idx == 4:
            # SLIDE 4: Introduction
            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text_frame.text
                    if "Introduction to your project" in txt:
                        shape.text_frame.text = (
                            "1. Project Definition:\n"
                            "CLOUD-M7 is an end-to-end distributed forensic provenance framework tailored for heterogeneous Edge, Fog, and Cloud computing environments.\n\n"
                            "2. Three-Tier Architectural Hierarchy:\n"
                            "- Edge Tier: Low-latency syscall capture and in-memory privacy filtering.\n"
                            "- Fog Tier: Regional aggregation, reduction, and intermediate network socket correlation.\n"
                            "- Cloud Tier: Global causal graph analytics and tamper-evident long-term storage.\n\n"
                            "3. Core Innovations:\n"
                            "- Tier-Adaptive Task Placement Optimization: Formulates min J(x) to mathematically place forensic tasks across tiers.\n"
                            "- Automated Cross-Tier Graph Fusion: Correlates network socket flows across tiers to synthesize complete multi-hop attack paths.\n"
                            "- Unified Event Model: Cryptographically bound 7-element tuple E_i ensuring legal non-repudiation."
                        )
                        for p in shape.text_frame.paragraphs:
                            p.font.name = "Segoe UI"
                            p.font.size = Pt(10)
                            p.font.color.rgb = DARK

        elif idx == 5:
            # SLIDE 5: Scope and Feasibility study
            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text_frame.text
                    if "Provide an overview of scope" in txt:
                        shape.text_frame.text = (
                            "1. Project Scope & Technical Boundaries:\n"
                            "- Multi-Tier Coverage: Covers Edge microcontrollers (ARM Cortex/Raspberry Pi), Linux Fog gateways, and enterprise Cloud clusters.\n"
                            "- Normalized Event Scope: Normalizes 4 core abstractions: Process lifecycle, POSIX file I/O, BSD network sockets, and Cloud REST APIs.\n"
                            "- Threat Model: Multi-stage APTs involving remote buffer overflows, privilege escalation, lateral socket movement, and database exfiltration.\n\n"
                            "2. Possible Shortcomings & Feasibility Solutions:\n"
                            "- Challenge: Edge Resource Constraints (CPU/RAM caps)\n"
                            "  -> Feasibility: Lightweight local reduction uses 620/800 mcores CPU and 292 MB RAM.\n"
                            "- Challenge: Uplink Bandwidth Saturation on IoT Networks\n"
                            "  -> Feasibility: Tier-adaptive placement cuts network bandwidth by 90.0% (500 KB/s -> 50 KB/s).\n"
                            "- Challenge: Cross-Tier Timing Jitter & Latency\n"
                            "  -> Feasibility: Sliding temporal causal window (t_send <= t_recv <= t_send + Dt) enforces forward causality."
                        )
                        for p in shape.text_frame.paragraphs:
                            p.font.name = "Segoe UI"
                            p.font.size = Pt(10)
                            p.font.color.rgb = DARK

        elif idx == 6:
            # SLIDE 6: Applications/Use cases
            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text_frame.text
                    if "Describe the applications" in txt:
                        shape.text_frame.text = (
                            "1. Industrial IoT & SCADA Smart Facilities:\n"
                            "- Detects and reconstructs attacks where adversaries exploit sensors/PLCs and pivot to plant control servers (e.g. Stuxnet/Triton), severing exfiltration before reaching corporate networks.\n\n"
                            "2. Connected Autonomous Vehicles (V2X):\n"
                            "- Enables real-time forensic logging over constrained 4G/5G cellular uplinks without vehicle network lag, isolating telematics tampering.\n\n"
                            "3. Smart Healthcare & Medical Grids (IoMT):\n"
                            "- Guarantees HIPAA and GDPR compliance via local in-memory privacy filtering of sensitive patient vitals before transmission to central EHR databases.\n\n"
                            "4. Enterprise Hybrid Cloud Infrastructures:\n"
                            "- Protects corporate networks against supply chain attacks entering through branch IoT devices and traversing VPN tunnels to exfiltrate enterprise SQL databases."
                        )
                        for p in shape.text_frame.paragraphs:
                            p.font.name = "Segoe UI"
                            p.font.size = Pt(10)
                            p.font.color.rgb = DARK

        elif idx == 7:
            # SLIDE 7: Background Study (5 Key Research Papers)
            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text_frame.text
                    if "Background work of the project" in txt:
                        shape.text_frame.text = (
                            "1. CamFlow / CamQuery (Pasquier et al., USENIX ATC 2018):\n"
                            "- Focus: Whole-system OS provenance capture via Linux Security Modules (LSM) & graph query engine.\n"
                            "- Limitation: Confined to single OS kernel; completely blind to cross-network socket pivots.\n"
                            "- CLOUD-M7 Advance: Bridges tiers via unified tuple E_i and socket flow correlation (E_network).\n\n"
                            "2. SPADE (Bates et al., USENIX Security 2015):\n"
                            "- Focus: Distributed provenance collection and query engine for Linux auditd.\n"
                            "- Limitation: Ships all raw audit records to central storage, saturating edge uplinks.\n"
                            "- CLOUD-M7 Advance: Constrained task placement optimization (min J(x)) saving 90.0% bandwidth.\n\n"
                            "3. Prov-IoT (Wang et al., IEEE IoT Journal 2020):\n"
                            "- Focus: Provenance tracking framework designed for smart home IoT devices.\n"
                            "- Limitation: Restricted to simple smart-home app triggers; cannot scale to hybrid clouds.\n"
                            "- CLOUD-M7 Advance: Unified schema scaling from microcontrollers to enterprise cloud datastores.\n\n"
                            "4. HOLMES (Milajerdi et al., IEEE S&P 2019):\n"
                            "- Focus: Real-time APT detection by correlating information flows to MITRE ATT&CK.\n"
                            "- Limitation: Single-pass kill chain traversal terminates at first alert, missing secondary roots.\n"
                            "- CLOUD-M7 Advance: Hyperparameter-tuned iterative multi-root discovery (Delta_I_k >= epsilon).\n\n"
                            "5. BackTracker (King & Chen, ACM SOSP 2003):\n"
                            "- Focus: Foundational backward causal dependency graph analysis from detection to root.\n"
                            "- Limitation: Single host, prone to dependency explosion, and no choke-point containment.\n"
                            "- CLOUD-M7 Advance: Multi-sensor convergent graph analysis with articulation choke points (100% containment)."
                        )
                        for p in shape.text_frame.paragraphs:
                            p.font.name = "Segoe UI"
                            p.font.size = Pt(8.5)
                            p.font.color.rgb = DARK

        elif idx == 8:
            # SLIDE 8: Implementation
            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text_frame.text
                    if "A Demo to be presented" in txt:
                        shape.text_frame.text = (
                            "1. System Architecture & Mathematical Schema (Equation 1):\n"
                            "- E_i = < UUID_i, tau_i, Tier_i, HostID_i, Type_i, P_i, pi_i > with SHA-256 tamper-evident integrity.\n"
                            "- Cross-Tier Flow Correlation (E_network): Socket 5-tuple matching with temporal window constraints.\n\n"
                            "2. Core Novelty 1: Iterative Multi-Root Discovery Engine:\n"
                            "- Formula: Delta_I_k = Impact(R_k) * exp(-lambda * k) >= epsilon  (K_max=5, epsilon=1.0, lambda=0.1)\n"
                            "- Discovered all 3 concurrent entry vectors (IoT agent exploit, firmware injection, cloud token theft).\n\n"
                            "3. Core Novelty 2: Multi-Sensor Convergence & Choke-Point Analysis:\n"
                            "- Containment Efficiency: E_cut(v) = |{p in P_multi | v in p}| / |P_multi|\n"
                            "- Discovered choke point: 'fog-gateway-01:socket_connect' achieves 100.0% containment efficiency.\n\n"
                            "4. Live Working Demonstration (run_demo.bat):\n"
                            "- Reconstructed 14-hop causal attack path across Edge -> Fog -> Cloud with 80% noise pruned.\n"
                            "- Automated Pytest Suite: 13/13 passing tests verifying schema, placement, and novelty algorithms."
                        )
                        for p in shape.text_frame.paragraphs:
                            p.font.name = "Segoe UI"
                            p.font.size = Pt(9.5)
                            p.font.color.rgb = DARK

        elif idx == 9:
            # SLIDE 9: Timeline
            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text_frame.text
                    if "The timelines for execution" in txt or "Provide" in txt:
                        shape.text_frame.text = (
                            "1. Timelines for Execution (Gantt Chart Milestones):\n"
                            "- Phase-I (Sem 5 - Review 1): Event Schema E_i, SHA-256 Hashing, Placement Optimization, Iterative Loop, Choke Points, 13 Pytests -> [COMPLETED]\n"
                            "- Phase-I (Sem 6 - Review 2): Real datasets ingestion (DARPA OpTC, TON_IoT), Docker multi-tier testbed, live Linux kernel eBPF syscall capture -> [PLANNED]\n"
                            "- Phase-II (Sem 7 - Review 3): Deep Reinforcement Learning (PPO/DQN) placement agent for dynamic adaptation, GNN anomalous path scorer -> [PLANNED]\n"
                            "- Phase-II (Sem 8 - Final Review): Physical hardware testbed (Raspberry Pi 4 + NVIDIA Jetson + AWS Cloud), Web SOC dashboard, IEEE security conference submission -> [PLANNED]\n\n"
                            "2. Individual Effort Plan:\n"
                            "- Dharshini (100% Effort): System Architecture, Placement Optimization, Graph Fusion, Novelty Formulations, Experimental Verification & Defense."
                        )
                        for p in shape.text_frame.paragraphs:
                            p.font.name = "Segoe UI"
                            p.font.size = Pt(10)
                            p.font.color.rgb = DARK

        elif idx == 10:
            # SLIDE 10: Any other information
            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text_frame.text
                    if "Provide any other information" in txt:
                        shape.text_frame.text = (
                            "1. Quantitative Benchmark vs. Centralized Baseline:\n"
                            "- Bandwidth: 500 KB/s -> 50 KB/s (90.0% Reduction / 10x Bandwidth Savings)\n"
                            "- Latency: 160 ms -> 20 ms (87.5% Faster Incident Response)\n"
                            "- Privacy Exposure Penalty: 120 pts -> 5 pts (95.8% Exposure Mitigation)\n"
                            "- Background Noise Pruning: 80.0% pruned away (4x Signal-to-Noise Ratio)\n\n"
                            "2. Automated Software Engineering Verification:\n"
                            "- 13 passing unit and integration tests executing in 0.88s on Python 3.11.\n\n"
                            "3. Real-World Datasets Roadmap for Phase-I Review 2:\n"
                            "- Ingestion adapters designed for DARPA OpTC (500+ GB enterprise audit logs), DARPA TC (Cadets/THEIA provenance graphs), and TON_IoT (industrial sensors).\n\n"
                            "4. Open-Source GitHub Repository: https://github.com/DharshiniPES/cloud-m7"
                        )
                        for p in shape.text_frame.paragraphs:
                            p.font.name = "Segoe UI"
                            p.font.size = Pt(10)
                            p.font.color.rgb = DARK

        elif idx == 11:
            # SLIDE 11: Thank You
            for shape in slide.shapes:
                if shape.has_text_frame:
                    txt = shape.text_frame.text
                    if "Thank You" in txt:
                        shape.text_frame.text = (
                            "Thank You!\n\n"
                            "CLOUD-M7: Tier-Adaptive Forensic Provenance\n"
                            "Candidate: Dharshini  |  Department of Computer Science & Engineering\n"
                            "PES University, Bangalore\n\n"
                            "Open for Evaluator Questions & Live Demo (run_demo.bat)"
                        )
                        p0 = shape.text_frame.paragraphs[0]
                        p0.font.name = "Segoe UI"
                        p0.font.size = Pt(28)
                        p0.font.bold = True
                        p0.font.color.rgb = NAVY

                        for p in shape.text_frame.paragraphs[1:]:
                            p.font.name = "Segoe UI"
                            p.font.size = Pt(12)
                            p.font.color.rgb = DARK

    # Save to both capstone reports and Downloads folder
    prs.save(str(OUTPUT_IN_CAPSTONE))
    print(f"[+] Saved populated presentation to: {OUTPUT_IN_CAPSTONE}")

    try:
        prs.save(str(OUTPUT_IN_DOWNLOADS))
        print(f"[+] Also saved to: {OUTPUT_IN_DOWNLOADS}")
    except PermissionError:
        print(f"[*] Note: {OUTPUT_IN_DOWNLOADS} is locked; updated capstone reports copy.")


if __name__ == "__main__":
    populate_template()
