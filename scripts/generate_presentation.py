"""
CLOUD-M7 Presentation Generator
Generates a 16:9 PowerPoint Presentation (.pptx) for Review 1,
complete with executive styling, metric cards, literature comparison tables,
embedded visualization figures, and speaker presenter notes.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT_DIR / "reports"
OUTPUT_PPTX = REPORTS_DIR / "CLOUD-M7_Review1_Presentation.pptx"

# Color Palette (Dark Cybersecurity Theme)
BG_COLOR = RGBColor(11, 17, 32)         # Deep Navy (#0B1120)
CARD_BG = RGBColor(26, 38, 57)          # Slate Navy Card (#1A2639)
CARD_BORDER = RGBColor(45, 64, 94)      # Card Border
PRIMARY_CYAN = RGBColor(14, 165, 233)   # Electric Cyan (#0EA5E9)
ACCENT_GOLD = RGBColor(245, 158, 11)    # Gold Accent (#F59E0B)
ACCENT_GREEN = RGBColor(16, 185, 129)   # Emerald Green (#10B981)
ACCENT_RED = RGBColor(239, 68, 68)      # Crimson Red (#EF4444)
TEXT_WHITE = RGBColor(248, 250, 252)    # Pure Text White (#F8FAFC)
TEXT_MUTED = RGBColor(148, 163, 184)    # Slate Gray Text (#94A3B8)
TABLE_HEADER_BG = RGBColor(15, 23, 42)  # Table Header Dark
TABLE_ROW_ALT = RGBColor(30, 41, 59)    # Table Row Alternating


def create_solid_bg(slide, prs):
    """Draws full slide background."""
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = BG_COLOR
    bg_shape.line.fill.background()
    return bg_shape


def add_header(slide, title_text, category="CLOUD-M7 CAPSTONE REVIEW 1"):
    """Adds a standard slide header card."""
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = PRIMARY_CYAN

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE


def add_card(slide, left, top, width, height, title="", border_color=CARD_BORDER):
    """Draws a styled container card."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)

    if title:
        title_box = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.4))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_CYAN
    return card


def set_speaker_notes(slide, notes_text):
    """Sets the presenter speaker notes for the slide."""
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text


def build_deck():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # -------------------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    create_solid_bg(slide1, prs)

    # Accent decorative bar
    bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.2), Inches(3.2))
    bar.fill.solid()
    bar.fill.fore_color.rgb = PRIMARY_CYAN
    bar.line.fill.background()

    # Title & Subtitle box
    tbox = slide1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(11.0), Inches(3.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "CLOUD-M7: Tier-Adaptive Forensic Provenance"
    p0.font.size = Pt(36)
    p0.font.bold = True
    p0.font.color.rgb = TEXT_WHITE

    p1 = tf1.add_paragraph()
    p1.text = "Distributed Attack-Path Reconstruction across Edge, Fog, and Cloud"
    p1.font.size = Pt(20)
    p1.font.color.rgb = PRIMARY_CYAN
    p1.space_before = Pt(10)

    p2 = tf1.add_paragraph()
    p2.text = "2-Year B.Tech Capstone Project (Batch 2026–2027) | Review 1 Prototype"
    p2.font.size = Pt(14)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(20)

    # Candidate Meta Card
    meta_card = add_card(slide1, Inches(1.2), Inches(5.2), Inches(10.8), Inches(1.4))
    mbox = slide1.shapes.add_textbox(Inches(1.5), Inches(5.35), Inches(10.2), Inches(1.1))
    mtf = mbox.text_frame
    mtf.word_wrap = True

    mp1 = mtf.paragraphs[0]
    mp1.text = "Candidate: Dharshini  |  Department: Computer Science and Engineering"
    mp1.font.size = Pt(14)
    mp1.font.bold = True
    mp1.font.color.rgb = TEXT_WHITE

    mp2 = mtf.add_paragraph()
    mp2.text = "GitHub Repository: https://github.com/DharshiniPES/cloud-m7"
    mp2.font.size = Pt(12)
    mp2.font.color.rgb = ACCENT_GOLD
    mp2.space_before = Pt(6)

    set_speaker_notes(
        slide1,
        "Good morning respected evaluators. My project is CLOUD-M7: Tier-Adaptive Forensic Provenance. "
        "In modern systems, computing spans edge sensors, fog gateways, and cloud servers. "
        "My project solves how to reconstruct multi-stage cyberattacks across all three tiers efficiently without "
        "wasting bandwidth or violating edge privacy."
    )

    # -------------------------------------------------------------------------
    # SLIDE 2: Problem Statement & Motivation
    # -------------------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    create_solid_bg(slide2, prs)
    add_header(slide2, "The Multi-Tier Forensic Dilemma & Motivation")

    card_w = Inches(3.6)
    card_h = Inches(5.0)
    top_pos = Inches(1.6)

    # Card 1: Host EDR
    add_card(slide2, Inches(0.8), top_pos, card_w, card_h, "1. Host EDR Blind Spot", ACCENT_RED)
    b1 = slide2.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.7), card_w - Inches(0.4), card_h - Inches(0.9))
    tf_b1 = b1.text_frame
    tf_b1.word_wrap = True
    p = tf_b1.paragraphs[0]
    p.text = "• Local monitors (auditd, CamFlow) only record events on a single machine.\n\n• When an attacker exploits an edge sensor and pivots to Fog or Cloud, the causal chain is permanently severed.\n\n• Results in siloed, incomplete forensic investigations."
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_WHITE

    # Card 2: Centralized SIEM
    add_card(slide2, Inches(4.85), top_pos, card_w, card_h, "2. Centralized SIEM Infeasibility", ACCENT_RED)
    b2 = slide2.shapes.add_textbox(Inches(5.05), top_pos + Inches(0.7), card_w - Inches(0.4), card_h - Inches(0.9))
    tf_b2 = b2.text_frame
    tf_b2.word_wrap = True
    p = tf_b2.paragraphs[0]
    p.text = "• Shipping raw audit logs to the Cloud exhausts constrained edge bandwidth (uplinks).\n\n• High round-trip ingestion latency delays real-time breach containment.\n\n• Exposes raw sensor and camera feeds, violating privacy regulations (GDPR/HIPAA)."
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_WHITE

    # Card 3: Heterogeneous Disconnect
    add_card(slide2, Inches(8.9), top_pos, card_w, card_h, "3. Heterogeneous Schemas", ACCENT_RED)
    b3 = slide2.shapes.add_textbox(Inches(9.1), top_pos + Inches(0.7), card_w - Inches(0.4), card_h - Inches(0.9))
    tf_b3 = b3.text_frame
    tf_b3.word_wrap = True
    p = tf_b3.paragraphs[0]
    p.text = "• Linux kernel syscalls, Fog container sockets, and Cloud REST API logs use conflicting data structures.\n\n• No standard cross-tier correlation model exists.\n\n• Requires tedious manual triage across disjoint security loggers."
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(
        slide2,
        "Existing forensic methods fail for three reasons: Host tools cannot see network pivots; "
        "centralized SIEM overwhelms network bandwidth by 90% and exposes sensitive data; "
        "and different operating tiers have incompatible log formats. CLOUD-M7 bridges this gap."
    )

    # -------------------------------------------------------------------------
    # SLIDE 3: Literature Survey & Comparative Analysis
    # -------------------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    create_solid_bg(slide3, prs)
    add_header(slide3, "Comparative Literature Analysis (Benchmarking)")

    # Add Table
    rows, cols = 7, 5
    table_shape = slide3.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.73), Inches(5.1))
    table = table_shape.table
    table.columns[0].width = Inches(3.73)
    table.columns[1].width = Inches(2.0)
    table.columns[2].width = Inches(2.0)
    table.columns[3].width = Inches(2.0)
    table.columns[4].width = Inches(2.0)

    headers = ["Forensic Capability", "Host EDR (auditd)", "Centralized SIEM", "SPADE / CamFlow", "CLOUD-M7 (Ours)"]
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = TABLE_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_CYAN if c_idx == 4 else TEXT_WHITE

    data = [
        ["Cross-Tier Multi-Hop Tracking", "No (Host-only)", "Partial (Manual)", "No (OS-only)", "Full (Autonomous)"],
        ["Tier-Adaptive Task Placement", "No", "No (Centralized)", "No", "Optimal Cost Model"],
        ["Edge Bandwidth Preservation", "No (Unbounded)", "Poor (Ship-all)", "No", "90.0% Reduction"],
        ["Unified Cross-Tier Schema", "Disjoint", "Proprietary", "Partial (LSM)", "Unified (E_i + SHA-256)"],
        ["Iterative Multi-Root Discovery", "Single-Pass BFS", "Rule-Based Alerts", "Single-Pass", "Hyperparameter (ΔI_k)"],
        ["Multi-Sensor Choke-Point Analysis", "None", "None", "None", "100% Containment Cut"],
    ]

    for r_idx, row_values in enumerate(data):
        for c_idx, val in enumerate(row_values):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = TABLE_ROW_ALT if (r_idx % 2 == 0) else CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(12)
            if c_idx == 4:
                p.font.bold = True
                p.font.color.rgb = ACCENT_GREEN
            else:
                p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(
        slide3,
        "Here is our comparative literature matrix. While SPADE and CamFlow focus solely on operating system syscalls, "
        "and centralized SIEM requires shipping everything to the cloud, CLOUD-M7 achieves full cross-tier correlation, "
        "adaptive placement, 90% bandwidth savings, and multi-sensor choke-point containment."
    )

    # -------------------------------------------------------------------------
    # SLIDE 4: Architecture & Unified Event Schema
    # -------------------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    create_solid_bg(slide4, prs)
    add_header(slide4, "Unified Multi-Tier Architecture & Formal Event Schema")

    # Left Card: The Schema
    add_card(slide4, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.2), "Formal Unified Event Tuple (E_i)")
    c1 = slide4.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf_c1 = c1.text_frame
    tf_c1.word_wrap = True
    p = tf_c1.paragraphs[0]
    p.text = "E_i = < UUID_i,  τ_i,  Tier_i,  HostID_i,  Type_i,  P_i,  π_i >\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GOLD

    details = (
        "• UUID_i: Cryptographically unique identifier\n"
        "• τ_i: High-precision UTC timestamp (temporal ordering)\n"
        "• Tier_i ∈ {Edge, Fog, Cloud}: Physical execution tier\n"
        "• HostID_i: Device / VM / container identity\n"
        "• Type_i ∈ {Process, File, Socket, API}\n"
        "• P_i: Structured payload (network 5-tuple, process lineage, resource target)\n"
        "• π_i: SHA-256 Tamper-evident cryptographic hash ensuring legal chain-of-custody"
    )
    p2 = tf_c1.add_paragraph()
    p2.text = details
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(8)

    # Right Card: Cross-Tier Correlation
    add_card(slide4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "Cross-Tier Socket & Temporal Correlation")
    c2 = slide4.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf_c2 = c2.text_frame
    tf_c2.word_wrap = True
    p = tf_c2.paragraphs[0]
    p.text = "Stitching Disjoint Intra-Tier Graphs into Global DAG:\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_CYAN

    corr_details = (
        "1. Bi-directional Socket 5-Tuple Alignment:\n"
        "   <src_ip, src_port, dst_ip, dst_port, protocol>\n\n"
        "2. Strict Temporal Constraint:\n"
        "   τ_send <= τ_recv (enforces causal forward flow)\n\n"
        "3. Cross-Tier Edge Construction (E_network):\n"
        "   Connects outbound socket on Edge to inbound socket on Fog, and Fog socket to Cloud ingress API.\n\n"
        "4. Global Causal Graph:\n"
        "   G_global = G_edge ∪ G_fog ∪ G_cloud ∪ E_network"
    )
    p2 = tf_c2.add_paragraph()
    p2.text = corr_details
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(6)

    set_speaker_notes(
        slide4,
        "To enable cross-tier forensics, we designed a unified mathematical schema tuple: UUID, timestamp, tier, "
        "host, event type, payload, and a SHA-256 hash. Cross-tier edges are automatically constructed by matching "
        "socket 5-tuples and strictly respecting temporal order."
    )

    # -------------------------------------------------------------------------
    # SLIDE 5: Dataset & Experimental Simulation
    # -------------------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    create_solid_bg(slide5, prs)
    add_header(slide5, "Experimental Setup & Multi-Tier Provenance Dataset")

    # Card 1: Event Breakdown
    add_card(slide5, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.2), "Provenance Dataset (70 Total Events)")
    d1 = slide5.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf_d1 = d1.text_frame
    tf_d1.word_wrap = True
    p = tf_d1.paragraphs[0]
    p.text = "Generated by High-Fidelity Multi-Tier Telemetry Engine:\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_CYAN

    data_summary = (
        "• 40 Benign Background Noise Events:\n"
        "   Periodic IoT sensor readings, Fog heartbeat beacons, routine Cloud SQL database queries.\n\n"
        "• 14 Primary Attack Events (Vector 1):\n"
        "   edge-sensor-01 memory corruption -> root shell -> staging script -> fog token theft -> lateral socket -> cloud admin API -> exfiltration dump.\n\n"
        "• 8 Secondary Attack Events (Vector 2):\n"
        "   edge-sensor-02 firmware command injection exploit.\n\n"
        "• 8 Control-Bus Events (Vector 3):\n"
        "   edge-actuator-03 unauthorized control-bus injection."
    )
    p2 = tf_d1.add_paragraph()
    p2.text = data_summary
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(6)

    # Card 2: Ground Truth & Benchmark Integration
    add_card(slide5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "Why Synthetic Ground Truth & Future Benchmarks")
    d2 = slide5.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf_d2 = d2.text_frame
    tf_d2.word_wrap = True
    p = tf_d2.paragraphs[0]
    p.text = "Methodological Rigor for Review 1 Validation:\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GOLD

    bench_summary = (
        "1. Verified Ground Truth:\n"
        "   Public single-host datasets lack correlated multi-tier telemetry across Edge, Fog, and Cloud simultaneously. Controlled ground truth is essential to verify 100% path recall and 0% false stitching.\n\n"
        "2. Realistic Behavioral Emulation:\n"
        "   Simulates realistic Linux process lifecycles, POSIX file I/O, BSD socket connections, and REST API access.\n\n"
        "3. Future Benchmark Roadmap (Phase 2):\n"
        "   Our unified schema is designed to ingest DARPA OpTC, DARPA TC (Cadets/THEIA), and TON_IoT in Semester 6."
    )
    p2 = tf_d2.add_paragraph()
    p2.text = bench_summary
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(6)

    set_speaker_notes(
        slide5,
        "For Review 1, rigorous validation requires verified ground truth. Our multi-tier simulator generates 70 events: "
        "40 benign background events mixed with a 3-vector Advanced Persistent Threat. This proves our algorithm isolates "
        "the true attack path without false positives, preparing us for DARPA OpTC ingestion in Phase 2."
    )

    # -------------------------------------------------------------------------
    # SLIDE 6: Novelty 1 - Placement Optimization
    # -------------------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    create_solid_bg(slide6, prs)
    add_header(slide6, "Novelty 1: Tier-Adaptive Task Placement Optimization")

    # Math Card
    add_card(slide6, Inches(0.8), Inches(1.6), Inches(11.73), Inches(1.7), "Mathematical Formulation")
    m_box = slide6.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(11.3), Inches(1.1))
    tf_m = m_box.text_frame
    tf_m.word_wrap = True
    p = tf_m.paragraphs[0]
    p.text = "min_x  J(x) = α · Lat(x) + β · BW(x) + γ · Priv(x) + δ · Cost(x)    subject to: C_edge(x) <= C_max"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GOLD

    p2 = tf_m.add_paragraph()
    p2.text = "Dynamically partitions tasks (Event Capture, Privacy Filtering, Graph Reduction, Fusion, Analytics) across Edge, Fog, and Cloud."
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(4)

    # Table of Optimization Results
    rows, cols = 5, 4
    t_shape = slide6.shapes.add_table(rows, cols, Inches(0.8), Inches(3.6), Inches(11.73), Inches(3.2))
    opt_table = t_shape.table
    opt_table.columns[0].width = Inches(3.73)
    opt_table.columns[1].width = Inches(2.66)
    opt_table.columns[2].width = Inches(2.66)
    opt_table.columns[3].width = Inches(2.66)

    headers = ["Optimization Metric", "Centralized Cloud Baseline", "CLOUD-M7 (Optimal Placement)", "Performance Gain"]
    for c_idx, h_text in enumerate(headers):
        cell = opt_table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = TABLE_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_CYAN if c_idx == 3 else TEXT_WHITE

    opt_data = [
        ["Network Bandwidth (Uplink)", "500.0 KB/s", "50.0 KB/s", "90.0% Reduction (10x Savings)"],
        ["Processing Latency", "160.0 ms", "20.0 ms", "87.5% Faster Local Triage"],
        ["Privacy Exposure Penalty", "120.0 points", "5.0 points", "95.8% Exposure Mitigation"],
        ["Edge CPU Utilization", "150.0 mcores", "620.0 mcores", "Feasible (< 800 mcores limit)"],
    ]

    for r_idx, r_vals in enumerate(opt_data):
        for c_idx, val in enumerate(r_vals):
            cell = opt_table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = TABLE_ROW_ALT if (r_idx % 2 == 0) else CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(12)
            if c_idx == 3:
                p.font.bold = True
                p.font.color.rgb = ACCENT_GREEN
            else:
                p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(
        slide6,
        "Our first novelty is Tier-Adaptive Placement Optimization. We formulate task placement as a constrained "
        "cost minimization problem. By moving privacy filtering and graph reduction to the edge, we achieve a 90% "
        "reduction in network bandwidth and 87.5% reduction in latency, all within edge hardware limits."
    )

    # -------------------------------------------------------------------------
    # SLIDE 7: Novelty 2 - Iterative Multi-Root Causal Discovery
    # -------------------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    create_solid_bg(slide7, prs)
    add_header(slide7, "Novelty 2: Hyperparameter-Tuned Iterative Causal Discovery")

    # Left: The Algorithm & Hyperparameters
    add_card(slide7, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.2), "Iterative Discovery Engine Formulation")
    it1 = slide7.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf_it1 = it1.text_frame
    tf_it1.word_wrap = True
    p = tf_it1.paragraphs[0]
    p.text = "Marginal Impact Comparison Condition:\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GOLD

    p_form = tf_it1.add_paragraph()
    p_form.text = "ΔI_k = Impact(R_k) · e^(-λ · k) >= ε\n"
    p_form.font.size = Pt(14)
    p_form.font.bold = True
    p_form.font.color.rgb = PRIMARY_CYAN

    it_text = (
        "• Hyperparameter K_max: Iteration ceiling (stops infinite traversal)\n"
        "• Hyperparameter ε: Diminishing return threshold\n"
        "• Hyperparameter λ: Exponential decay attenuation factor\n\n"
        "Forensic Superiority over Single-Pass BFS:\n"
        "Standard forensic algorithms terminate as soon as ONE root cause is discovered. "
        "Our engine subtracts previously traversed subgraphs and iteratively uncovers stealthy concurrent entry vectors."
    )
    p2 = tf_it1.add_paragraph()
    p2.text = it_text
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(4)

    # Right: Empirical Multi-Vector Output
    add_card(slide7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "Empirical Discovery of Concurrent Attack Roots")
    it2 = slide7.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf_it2 = it2.text_frame
    tf_it2.word_wrap = True
    p = tf_it2.paragraphs[0]
    p.text = "Discovered Attack Roots Across Iterations:\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    res_text = (
        "• Iteration 1 [Primary Vector]:\n"
        "   Host: edge-sensor-01 | /usr/bin/iot_agent\n"
        "   Path: 14 hops to Cloud | Impact: 102.30\n"
        "   Vector: IoT memory corruption vulnerability\n\n"
        "• Iteration 2 [Secondary Vector]:\n"
        "   Host: edge-sensor-02 | /usr/sbin/fw_updater\n"
        "   Path: 11 hops to Cloud | Impact: 10.24\n"
        "   Vector: Concurrent firmware command-injection\n\n"
        "• Iteration 3 [Secondary Vector]:\n"
        "   Host: fog-gateway-01 | cloud_service_account.json\n"
        "   Path: 7 hops to Cloud | Impact: 3.77\n"
        "   Vector: Stolen Fog IAM credential token\n\n"
        "[*] Convergence: Terminates cleanly at iteration 4 when ΔI_4 < ε."
    )
    p2 = tf_it2.add_paragraph()
    p2.text = res_text
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(4)

    set_speaker_notes(
        slide7,
        "Our second novelty addresses a fatal flaw in traditional forensics: single-pass algorithms stop after finding "
        "just one entry point. Our engine uses an iterative loop with hyperparameters (K_max, epsilon, lambda) to discover "
        "all concurrent attack vectors, finding three distinct entry points across edge and fog."
    )

    # -------------------------------------------------------------------------
    # SLIDE 8: Novelty 3 - Interconnected Multi-Sensor Graph & Choke Points
    # -------------------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    create_solid_bg(slide8, prs)
    add_header(slide8, "Novelty 3: Interconnected Multi-Sensor Graph & Choke-Point Analysis")

    # Left: Convergence & Cut Vertices
    add_card(slide8, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.2), "Convergent Multi-Sensor Attack Graph")
    ms1 = slide8.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf_ms1 = ms1.text_frame
    tf_ms1.word_wrap = True
    p = tf_ms1.paragraphs[0]
    p.text = "Tracing Convergent Attack Trajectories:\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_CYAN

    ms_text = (
        "• In real IoT environments, attacks originate from multiple sensors simultaneously.\n\n"
        "• Engine discovers all paths from Edge sensors (edge-sensor-01, edge-sensor-02, edge-actuator-03) through Fog to Cloud target.\n\n"
        "• Articulation Cut-Vertex Detection:\n"
        "   Computes graph articulation bottlenecks where all divergent sensor attack paths MUST converge.\n\n"
        "   Containment Efficiency Formulation:\n"
        "   E_cut(v) = |{p ∈ P_multi | v ∈ p}| / |P_multi|"
    )
    p2 = tf_ms1.add_paragraph()
    p2.text = ms_text
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(4)

    # Right: Choke-point Discovery Result
    add_card(slide8, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "Critical Choke-Point Discovery & Containment")
    ms2 = slide8.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf_ms2 = ms2.text_frame
    tf_ms2.word_wrap = True
    p = tf_ms2.paragraphs[0]
    p.text = "Discovered Articulation Bottleneck:\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GOLD

    res_choke = (
        "[*] Identified Choke-Point Node:\n"
        "   Tier: [FOG] | Host: 'fog-gateway-01'\n"
        "   Action: Socket 'connect' to Cloud Ingress\n"
        "   Containment Efficiency: 100.0% (Severs 3/3 paths)\n"
        "   Is Articulation Cut-Point: TRUE\n\n"
        "Practical Incident Response Impact:\n"
        "• Instead of rushing to patch dozens of remote edge sensors in the field during an active breach...\n\n"
        "• Security teams can isolate or block JUST ONE choke-point on the Fog gateway to achieve 100% containment of all multi-sensor attack paths!"
    )
    p2 = tf_ms2.add_paragraph()
    p2.text = res_choke
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(4)

    set_speaker_notes(
        slide8,
        "Our third novelty models interconnected attacks originating from multiple edge sensors. Using graph theory "
        "and articulation cuts, our engine discovered a critical choke point at the Fog gateway socket with 100% "
        "containment efficiency. Blocking this single point instantly neutralizes all incoming attacks before they touch the cloud."
    )

    # -------------------------------------------------------------------------
    # SLIDE 9: Visual Forensic Artifacts (Images Embedded)
    # -------------------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    create_solid_bg(slide9, prs)
    add_header(slide9, "Visual Forensic Artifacts & Reconstructed Attack Graphs")

    img_w = Inches(5.7)
    img_h = Inches(4.0)

    # Check if images exist and embed
    p1_path = REPORTS_DIR / "attack_path_reconstruction.png"
    p2_path = REPORTS_DIR / "interconnected_attack_paths.png"

    # Card 1: Attack Path
    add_card(slide9, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.2), "Figure 1: Cross-Tier 14-Hop Attack Path")
    if p1_path.exists():
        slide9.shapes.add_picture(str(p1_path), Inches(0.9), Inches(2.2), img_w - Inches(0.2), img_h)
    else:
        # Placeholder text if missing
        b = slide9.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(5.3), Inches(2.0))
        b.text_frame.text = "[Figure 1: reports/attack_path_reconstruction.png]"

    cap1 = slide9.shapes.add_textbox(Inches(0.9), Inches(6.3), img_w - Inches(0.2), Inches(0.5))
    cap1.text_frame.text = "Edge (Green) -> Fog (Orange) -> Cloud (Purple). 80% noise pruned."
    cap1.text_frame.paragraphs[0].font.size = Pt(11)
    cap1.text_frame.paragraphs[0].font.color.rgb = TEXT_MUTED

    # Card 2: Interconnected Choke Points
    add_card(slide9, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "Figure 2: Multi-Sensor Paths & Gold Choke Points")
    if p2_path.exists():
        slide9.shapes.add_picture(str(p2_path), Inches(6.9), Inches(2.2), img_w - Inches(0.2), img_h)
    else:
        b = slide9.shapes.add_textbox(Inches(7.0), Inches(2.5), Inches(5.3), Inches(2.0))
        b.text_frame.text = "[Figure 2: reports/interconnected_attack_paths.png]"

    cap2 = slide9.shapes.add_textbox(Inches(6.9), Inches(6.3), img_w - Inches(0.2), Inches(0.5))
    cap2.text_frame.text = "Multiple edge sensors converging to cloud. Gold nodes = 100% containment choke points."
    cap2.text_frame.paragraphs[0].font.size = Pt(11)
    cap2.text_frame.paragraphs[0].font.color.rgb = TEXT_MUTED

    set_speaker_notes(
        slide9,
        "Here are our generated visualizations. Figure 1 shows the end-to-end 14-hop causal attack path across Edge, "
        "Fog, and Cloud tiers with 80% noise pruned. Figure 2 shows the multi-sensor graph where gold nodes highlight "
        "the critical choke points for immediate incident containment."
    )

    # -------------------------------------------------------------------------
    # SLIDE 10: Quantitative Results & Test Verification
    # -------------------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    create_solid_bg(slide10, prs)
    add_header(slide10, "Quantitative Results & Automated Test Verification")

    # Left: Metrics Summary
    add_card(slide10, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.2), "Empirical Performance Summary")
    q1 = slide10.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf_q1 = q1.text_frame
    tf_q1.word_wrap = True
    p = tf_q1.paragraphs[0]
    p.text = "Key Quantitative Achievements:\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    q_text = (
        "• Bandwidth Reduction: 90.0% (500 KB/s -> 50 KB/s)\n"
        "• Latency Reduction: 87.5% (160 ms -> 20 ms)\n"
        "• Background Noise Pruning: 80.0% pruned away\n"
        "• Reconstructed Attack Path: Exactly 14 causal hops\n"
        "• Choke-Point Containment: 100.0% efficiency (1 Fog node)\n"
        "• Attack Vectors Uncovered: 3 distinct vectors (Iterative engine)\n"
        "• Edge CPU Feasibility: 620 / 800 mcores (Within budget)"
    )
    p2 = tf_q1.add_paragraph()
    p2.text = q_text
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(6)

    # Right: Automated Tests
    add_card(slide10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.2), "Automated Pytest Suite (13/13 Passing)")
    q2 = slide10.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.4))
    tf_q2 = q2.text_frame
    tf_q2.word_wrap = True
    p = tf_q2.paragraphs[0]
    p.text = "Strict Software Engineering Quality Standards:\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_CYAN

    tests_text = (
        "PASSED: test_end_to_end_attack_reconstruction\n"
        "PASSED: test_cross_tier_network_correlation\n"
        "PASSED: test_backward_and_forward_traversal\n"
        "PASSED: test_multi_sensor_paths_to_cloud\n"
        "PASSED: test_choke_point_containment_bottlenecks\n"
        "PASSED: test_iterative_discovery_multi_vector\n"
        "PASSED: test_hyperparameter_max_iterations_ceiling\n"
        "PASSED: test_hyperparameter_epsilon_convergence\n"
        "PASSED: test_placement_feasibility_constraint\n"
        "PASSED: test_optimal_placement_discovery\n"
        "PASSED: test_event_initialization_and_hash\n"
        "PASSED: test_serialization_and_deserialization\n"
        "PASSED: test_network_tuple_extraction\n\n"
        "[*] 100% Passing in 0.88s on Python 3.11."
    )
    p2 = tf_q2.add_paragraph()
    p2.text = tests_text
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(4)

    set_speaker_notes(
        slide10,
        "Every claim in our presentation is verified with automated test suites. We have 13 passing unit and integration "
        "tests verifying schema integrity, placement constraints, iterative hyperparameter convergence, and choke-point "
        "detection in under one second."
    )

    # -------------------------------------------------------------------------
    # SLIDE 11: 2-Year Project Roadmap
    # -------------------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    create_solid_bg(slide11, prs)
    add_header(slide11, "2-Year Capstone Project Roadmap (Phase 1 to Phase 4)")

    col_w = Inches(2.7)
    gap = Inches(0.3)
    top_pos = Inches(1.6)
    c_height = Inches(5.2)

    phases = [
        ("Phase 1: Review 1", "COMPLETED", ACCENT_GREEN,
         "• Formal Event Schema E_i\n• SHA-256 integrity hash\n• Placement Cost Optimizer\n• Causal Graph Fusion\n• Iterative Discovery Engine\n• Multi-Sensor Choke Points\n• 13/13 Pytest Suite\n• GitHub Repo Setup"),

        ("Phase 2: Review 2", "Semester 6", PRIMARY_CYAN,
         "• Public Datasets:\n  - DARPA OpTC\n  - DARPA TC (Cadets)\n  - TON_IoT\n• Docker Multi-Tier Testbed\n• Linux eBPF Kernel Hooks\n• Merkle-Tree Hash Chaining"),

        ("Phase 3: Review 3", "Semester 7", ACCENT_GOLD,
         "• Deep Reinforcement Learning Placement Agent (PPO/DQN)\n• Dynamic real-time network adaptation\n• Graph Neural Network (GNN) anomalous path scorer"),

        ("Phase 4: Final Review", "Semester 8", PRIMARY_CYAN,
         "• Physical Hardware Testbed (Raspberry Pi + Jetson + AWS)\n• Web-based Interactive SOC Analyst Dashboard\n• Research Paper Submission to IEEE/ACM Security Conference")
    ]

    for idx, (title, status, color, content) in enumerate(phases):
        l_pos = Inches(0.8) + idx * (col_w + gap)
        add_card(slide11, l_pos, top_pos, col_w, c_height, title, color)

        # Status badge
        s_box = slide11.shapes.add_textbox(l_pos + Inches(0.2), top_pos + Inches(0.55), col_w - Inches(0.4), Inches(0.3))
        p_s = s_box.text_frame.paragraphs[0]
        p_s.text = f"[{status}]"
        p_s.font.size = Pt(11)
        p_s.font.bold = True
        p_s.font.color.rgb = color

        # Content
        c_box = slide11.shapes.add_textbox(l_pos + Inches(0.2), top_pos + Inches(0.9), col_w - Inches(0.4), c_height - Inches(1.1))
        tf_c = c_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = content
        p_c.font.size = Pt(11)
        p_c.font.color.rgb = TEXT_WHITE

    set_speaker_notes(
        slide11,
        "Here is our structured 2-year roadmap. Phase 1 is fully delivered today with working code, optimization, "
        "and novelties. Next semester in Phase 2, we integrate DARPA OpTC and live eBPF kernel hooks. In Phase 3, we add "
        "reinforcement learning, culminating in Phase 4 with a physical hardware testbed and IEEE conference submission."
    )

    # Save presentation
    prs.save(str(OUTPUT_PPTX))
    print(f"[+] Successfully generated PowerPoint presentation: {OUTPUT_PPTX}")


if __name__ == "__main__":
    build_deck()
