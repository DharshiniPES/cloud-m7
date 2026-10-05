"""
Evaluation and Benchmark Analysis Script for CLOUD-M7.

Generates comparative evaluation metrics matching Table 1 of the specification:
    - Cross-Tier Multi-Hop Tracking
    - Tier-Adaptive Placement Optimization
    - Edge Bandwidth & Privacy Preservation
    - Common Multi-Tier Schema
    - Causal Provenance Graph Fusion
    - End-to-End Attack-Path Synthesis
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cloud_m7.placement.cost_model import ForensicTask, MultiObjectiveWeights, TaskType
from cloud_m7.placement.optimizer import PlacementOptimizer
from cloud_m7.schema.types import TierType


def generate_comparative_table():
    print("=" * 78)
    print("  TABLE 1: FEATURE COMPARISON WITH EXISTING FORENSIC & PROVENANCE SYSTEMS")
    print("=" * 78)

    features = [
        "Cross-Tier Multi-Hop Tracking",
        "Tier-Adaptive Placement Optimization",
        "Edge Bandwidth & Privacy Preservation",
        "Common Multi-Tier Schema",
        "Causal Provenance Graph Fusion",
        "End-to-End Attack-Path Synthesis",
    ]

    data = {
        "Forensic Capability": features,
        "Host Logs (auditd)": ["No", "No", "No", "No", "No", "No"],
        "Cloud Forensics (Zawoad et al.)": ["Partial", "No", "No", "Partial", "No", "No"],
        "CamFlow (Pasquier et al.)": ["No", "No", "No", "Partial", "No", "Partial"],
        "CLOUD-M7 (Ours)": ["YES", "YES", "YES", "YES", "YES", "YES"],
    }

    df = pd.DataFrame(data)
    print(df.to_string(index=False))
    print("=" * 78)


def evaluate_scalability():
    print("\n" + "=" * 78)
    print("  EMPIRICAL EVALUATION: BANDWIDTH & LATENCY TRADEOFF ANALYSIS")
    print("=" * 78)

    event_rates = [100, 500, 1000, 5000, 10000]
    results = []

    for rate in event_rates:
        tasks = [
            ForensicTask(TaskType.EVENT_CAPTURE, required_cpu_mcore=150, required_memory_mb=64, raw_event_rate_per_sec=rate),
            ForensicTask(TaskType.PRIVACY_FILTER, required_cpu_mcore=120, required_memory_mb=48, raw_event_rate_per_sec=rate),
            ForensicTask(TaskType.GRAPH_REDUCTION, required_cpu_mcore=350, required_memory_mb=180, raw_event_rate_per_sec=rate // 2),
            ForensicTask(TaskType.CROSS_TIER_FUSION, required_cpu_mcore=600, required_memory_mb=512, raw_event_rate_per_sec=rate // 5),
            ForensicTask(TaskType.CAUSAL_ANALYTICS, required_cpu_mcore=1200, required_memory_mb=1024, raw_event_rate_per_sec=rate // 10),
            ForensicTask(TaskType.LONG_TERM_STORAGE, required_cpu_mcore=200, required_memory_mb=2048, raw_event_rate_per_sec=rate // 10),
        ]

        optimizer = PlacementOptimizer()
        opt_assignment, opt_metrics = optimizer.find_optimal_placement(tasks)

        # Baseline
        base_assignment = {t.name: TierType.CLOUD for t in tasks}
        base_assignment[TaskType.EVENT_CAPTURE] = TierType.EDGE
        base_metrics = optimizer.evaluate_placement(tasks, base_assignment)

        bw_saving = (1.0 - (opt_metrics.bandwidth_kbps / base_metrics.bandwidth_kbps)) * 100
        lat_saving = (1.0 - (opt_metrics.latency_ms / base_metrics.latency_ms)) * 100

        results.append({
            "Events/sec": rate,
            "Centralized BW (KB/s)": base_metrics.bandwidth_kbps,
            "CLOUD-M7 BW (KB/s)": opt_metrics.bandwidth_kbps,
            "BW Reduction (%)": f"{bw_saving:.1f}%",
            "Centralized Latency (ms)": base_metrics.latency_ms,
            "CLOUD-M7 Latency (ms)": opt_metrics.latency_ms,
            "Lat Reduction (%)": f"{lat_saving:.1f}%",
        })

    eval_df = pd.DataFrame(results)
    print(eval_df.to_string(index=False))
    print("=" * 78)


if __name__ == "__main__":
    generate_comparative_table()
    evaluate_scalability()
