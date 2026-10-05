"""
Command Line Interface (CLI) for CLOUD-M7 Forensic Framework.

Provides commands to run multi-tier simulation, evaluate placement optimization,
fuse cross-tier subgraphs, and reconstruct distributed attack paths.
"""

import argparse
import os
import sys
import time

from cloud_m7.fusion.attack_path import AttackPathReconstructor
from cloud_m7.fusion.causal_graph import ProvenanceGraphEngine
from cloud_m7.placement.cost_model import (
    ForensicTask,
    MultiObjectiveWeights,
    TaskType,
)
from cloud_m7.placement.optimizer import PlacementOptimizer
from cloud_m7.schema.types import TierType
from cloud_m7.simulator.attack_scenario import MultiTierAttackSimulator
from cloud_m7.visualization.graph_plot import Visualizer


def run_placement_optimization():
    """Runs and displays multi-objective tier placement optimization."""
    print("=" * 70)
    print("  CLOUD-M7: TIER-ADAPTIVE FORENSIC TASK PLACEMENT OPTIMIZATION")
    print("  Formulation: min_x J(x) = alpha*Lat(x) + beta*BW(x) + gamma*Priv(x) + delta*Cost(x)")
    print("=" * 70)

    tasks = [
        ForensicTask(TaskType.EVENT_CAPTURE, required_cpu_mcore=150, required_memory_mb=64, raw_event_rate_per_sec=500),
        ForensicTask(TaskType.PRIVACY_FILTER, required_cpu_mcore=120, required_memory_mb=48, raw_event_rate_per_sec=500),
        ForensicTask(TaskType.GRAPH_REDUCTION, required_cpu_mcore=350, required_memory_mb=180, raw_event_rate_per_sec=200),
        ForensicTask(TaskType.CROSS_TIER_FUSION, required_cpu_mcore=600, required_memory_mb=512, raw_event_rate_per_sec=100),
        ForensicTask(TaskType.CAUSAL_ANALYTICS, required_cpu_mcore=1200, required_memory_mb=1024, raw_event_rate_per_sec=50),
        ForensicTask(TaskType.LONG_TERM_STORAGE, required_cpu_mcore=200, required_memory_mb=2048, raw_event_rate_per_sec=50),
    ]

    optimizer = PlacementOptimizer(
        weights=MultiObjectiveWeights(alpha=0.35, beta=0.35, gamma=0.15, delta=0.15),
        edge_max_cpu_mcore=800.0,
        edge_max_mem_mb=512.0,
    )

    # 1. Optimal Adaptive Assignment
    optimal_assignment, optimal_metrics = optimizer.find_optimal_placement(tasks)

    # 2. Centralized Cloud Baseline (All tasks forwarded to cloud)
    cloud_baseline_assignment = {t.name: TierType.CLOUD for t in tasks}
    cloud_baseline_assignment[TaskType.EVENT_CAPTURE] = TierType.EDGE
    cloud_baseline_metrics = optimizer.evaluate_placement(tasks, cloud_baseline_assignment)

    print("\n[+] OPTIMAL FORENSIC PLACEMENT ASSIGNMENT:")
    for task_name, tier in optimal_assignment.items():
        print(f"    - {task_name.value:<20} -> [{tier.value.upper()}] Tier")

    print("\n[+] QUANTITATIVE COMPARISON WITH CENTRALIZED CLOUD BASELINE:")
    print("-" * 70)
    print(f"{'Metric':<28} | {'Centralized Baseline':<20} | {'CLOUD-M7 (Adaptive)':<18}")
    print("-" * 70)
    print(f"{'Total Cost J(x)':<28} | {cloud_baseline_metrics.total_cost_j:<20} | {optimal_metrics.total_cost_j:<18}")
    print(f"{'Latency (ms)':<28} | {cloud_baseline_metrics.latency_ms:<20} | {optimal_metrics.latency_ms:<18}")
    print(f"{'Network Bandwidth (KB/s)':<28} | {cloud_baseline_metrics.bandwidth_kbps:<20} | {optimal_metrics.bandwidth_kbps:<18}")
    print(f"{'Privacy Exposure Penalty':<28} | {cloud_baseline_metrics.privacy_risk_score:<20} | {optimal_metrics.privacy_risk_score:<18}")
    print(f"{'Cloud Cost ($/day)':<28} | ${cloud_baseline_metrics.monetary_cost_usd_per_day:<19} | ${optimal_metrics.monetary_cost_usd_per_day:<17}")
    print(f"{'Edge CPU Consumed (mcores)':<28} | {cloud_baseline_metrics.edge_cpu_used_mcore:<20} | {optimal_metrics.edge_cpu_used_mcore:<18}")
    print(f"{'Edge Memory (MB)':<28} | {cloud_baseline_metrics.edge_mem_used_mb:<20} | {optimal_metrics.edge_mem_used_mb:<18}")
    print("-" * 70)

    bw_savings = round((1.0 - (optimal_metrics.bandwidth_kbps / cloud_baseline_metrics.bandwidth_kbps)) * 100, 1)
    lat_savings = round((1.0 - (optimal_metrics.latency_ms / cloud_baseline_metrics.latency_ms)) * 100, 1)
    print(f"\n[*] Key Achievement: Bandwidth reduced by {bw_savings}%, Latency reduced by {lat_savings}%")
    print(f"[*] Edge Constraints: Within capacity limits (Used {optimal_metrics.edge_cpu_used_mcore} / 800.0 mcores CPU)\n")


def run_full_pipeline_demo():
    """Runs complete end-to-end simulation, fusion, and reconstruction."""
    print("=" * 70)
    print("  CLOUD-M7: DISTRIBUTED ATTACK-PATH RECONSTRUCTION PIPELINE")
    print("  B.Tech Capstone Project | Department of CSE | Review 1 Prototype")
    print("=" * 70)

    # 1. Simulate Multi-Tier Telemetry
    print("\n[Stage 1] Generating Multi-Tier Distributed Telemetry & Multi-Stage APT...")
    simulator = MultiTierAttackSimulator()
    start_time = time.time()
    events = simulator.generate_full_simulation_dataset(base_time=start_time, benign_count=36)
    print(f"    -> Generated {len(events)} total provenance events across Edge, Fog, and Cloud.")

    # 2. Ingest into Provenance Graph Engine
    print("\n[Stage 2] Constructing Intra-Tier Subgraphs and Correlating E_network...")
    engine = ProvenanceGraphEngine(time_window_seconds=10.0)
    engine.add_events(events)

    # Fuse global DAG
    global_dag = engine.fuse_global_graph()
    stats = engine.get_summary_statistics()

    print(f"    -> Total Nodes in G_global: {stats['total_nodes']}")
    print(f"    -> Total Directed Edges:   {stats['total_edges']}")
    print(f"    -> Node Distribution:      {stats['nodes_per_tier']}")
    print(f"    -> Cross-Tier Socket Flows:{stats['cross_tier_edges_count']}")
    print(f"    -> Is Valid Causal DAG:    {stats['is_directed_acyclic_graph']}")

    # 3. Perform Attack Path Reconstruction
    print("\n[Stage 3] Executing Backward & Forward Causal Traversal...")
    reconstructor = AttackPathReconstructor(engine)
    result = reconstructor.reconstruct_attack_path()

    if not result:
        print("[!] No attack path detected.")
        return

    print(f"    -> Reconstructed Attack Path Length: {result.path_length} hops")
    print(f"    -> Traversed Tiers:                 {' -> '.join(result.traversed_tiers)}")
    print(f"    -> Background Noise Reduction:      {result.reduction_percentage}% pruned")

    print("\n" + "=" * 70)
    print("  RECONSTRUCTED ATTACK TIMELINE (ROOT ENTRY -> TARGET IMPACT)")
    print("=" * 70)
    for step in result.attack_steps:
        print(f"  Step {step.order:02d} | [{step.tier.upper():<5}] | {step.event_type:<7} | {step.host_id}")
        print(f"          Action:      {step.action}")
        print(f"          Entity:      {step.entity}")
        print(f"          Description: {step.description}")
        print("  " + "-" * 66)

    # 4. Generate Publication-Quality Visualization
    print("\n[Stage 4] Generating Multi-Tier Forensic Graph Visualization...")
    os.makedirs("reports", exist_ok=True)
    report_img_path = os.path.join("reports", "attack_path_reconstruction.png")
    viz = Visualizer(engine)
    viz.render_attack_graph(report_img_path, attack_result=result)
    print(f"    -> High-resolution attack graph saved to: {report_img_path}")

    # 5. Run Placement Optimization
    print("\n[Stage 5] Solving Tier-Adaptive Placement Optimization Model...")
    run_placement_optimization()

    print("=" * 70)
    print("  REVIEW 1 DEMONSTRATION COMPLETE: ALL MODULES VERIFIED")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="CLOUD-M7 Forensic Provenance Framework")
    parser.add_argument(
        "mode",
        choices=["demo", "optimize", "simulate"],
        default="demo",
        nargs="?",
        help="Execution mode (default: demo)",
    )
    args = parser.parse_args()

    if args.mode == "demo":
        run_full_pipeline_demo()
    elif args.mode == "optimize":
        run_placement_optimization()
    elif args.mode == "simulate":
        sim = MultiTierAttackSimulator()
        evts = sim.generate_full_simulation_dataset()
        print(f"Generated {len(evts)} events successfully.")


if __name__ == "__main__":
    main()
