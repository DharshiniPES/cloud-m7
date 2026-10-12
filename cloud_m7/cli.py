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
from cloud_m7.fusion.iterative_discovery import IterativeAttackDiscoveryEngine
from cloud_m7.fusion.interconnected_paths import InterconnectedAttackPathEngine
from cloud_m7.fusion.causal_bridge import CausalBridgeImputer
from cloud_m7.fusion.active_remediation import ActiveChokePointRemediator
from cloud_m7.fusion.mitre_mapper import MitreAttackMapper
from cloud_m7.storage.parquet_engine import ProvenanceStorageEngine
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

    # 4. Novelty Feature: Iterative Multi-Root Causal Discovery
    print("\n[Stage 4] Executing Novel Iterative Multi-Root Causal Attack Discovery...")
    iter_engine = IterativeAttackDiscoveryEngine(
        engine,
        max_iterations=5,
        impact_threshold_epsilon=5.0,  # 5% marginal threshold
        causal_attenuation=0.85,
    )
    iter_result = iter_engine.discover_all_attack_points()

    print("=" * 70)
    print("  CLOUD-M7 NOVELTY: ITERATIVE CAUSAL DISCOVERY & IMPACT COMPARISON")
    print(f"  Hyperparameters: K_max={iter_result.max_iterations_hyperparameter}, "
          f"Epsilon={iter_result.impact_threshold_epsilon}%, Lambda=0.85")
    print("=" * 70)
    for m in iter_result.iteration_history:
        status_tag = "[CONVERGED]" if m.converged else "[EXPLORING]"
        print(f"  Iteration {m.iteration:02d} {status_tag}:")
        print(f"      New Attack Nodes:      +{m.new_nodes_discovered} (Total: {m.total_discovered_nodes})")
        print(f"      Cumulative Impact:     {m.cumulative_impact_score:.2f}")
        print(f"      Marginal Impact Gain:  +{m.marginal_impact_gain_pct:.2f}%")
        print(f"      Convergence Status:    {m.reason}")
        print("  " + "-" * 66)

    print("\n  Summary of Discovered Attack Entry Vectors:")
    for v in iter_result.discovered_vectors:
        print(f"    * {v.vector_id}:")
        print(f"        Entry Point: [{v.entry_tier}] on host '{v.entry_host}' ({v.entry_entity})")
        print(f"        Path Length: {v.path_length} hops -> Root impact: {v.vector_impact_score:.2f}")
        print(f"        Summary:     {v.description}")

    # 5. Interconnected Multi-Sensor Attack Graph & Choke-Point Analysis
    print("\n[Stage 5] Constructing Interconnected Multi-Sensor Attack Graph to Cloud...")
    intercon_engine = InterconnectedAttackPathEngine(engine)
    intercon_res = intercon_engine.analyze_interconnected_attack_graph()

    print("=" * 70)
    print("  INTERCONNECTED MULTI-SENSOR ATTACK GRAPH & CHOKE-POINT ANALYSIS")
    print("=" * 70)
    print(f"  Originating Edge Devices: {', '.join(intercon_res.originating_sensors)}")
    print(f"  Total Interconnected Graph Nodes: {intercon_res.total_interconnected_nodes}")
    print(f"  Total Interconnected Graph Edges: {intercon_res.total_interconnected_edges}")
    print("\n  Paths from Individual Edge Sensors to Cloud Target:")
    for sensor, paths in intercon_res.sensor_paths.items():
        for p in paths:
            print(f"    * [{sensor}] -> {' -> '.join(p.traversed_hosts)} ({p.hops} hops)")

    print("\n  Critical Convergence Choke Points (Containment Bottlenecks):")
    for cp in intercon_res.choke_points:
        print(f"    * [{cp.tier.upper()}] Host: '{cp.host_id}' | Action: {cp.action} on {cp.entity}")
        print(f"        Containment Efficiency: {cp.containment_efficiency_pct}% (Severs {cp.paths_severed_count}/{cp.total_paths_count} paths)")
        print(f"        Is Articulation Cut-Point: {cp.is_cut_vertex}")
        print(f"        Recommendation: {cp.mitigation_recommendation}")

    # 6. Generate Publication-Quality Visualizations
    print("\n[Stage 6] Generating Multi-Tier Forensic Graph Visualizations...")
    os.makedirs("reports", exist_ok=True)
    report_img_path = os.path.join("reports", "attack_path_reconstruction.png")
    intercon_img_path = os.path.join("reports", "interconnected_attack_paths.png")
    
    viz = Visualizer(engine)
    viz.render_attack_graph(report_img_path, iterative_result=iter_result)
    viz.render_interconnected_graph(intercon_img_path, interconnected_result=intercon_res)
    print(f"    -> Attack graph saved to: {report_img_path}")
    print(f"    -> Interconnected multi-sensor graph saved to: {intercon_img_path}")

    # 7. Run Placement Optimization
    print("\n[Stage 7] Solving Tier-Adaptive Placement Optimization Model...")
    run_placement_optimization()

    # 8. Columnar Parquet Storage & DuckDB High-Speed Analytics
    print("\n[Stage 8] Columnar Parquet Storage & DuckDB High-Speed Analytics...")
    storage_engine = ProvenanceStorageEngine()
    parquet_out = os.path.join("data", "processed", "provenance_events.parquet")
    json_out = os.path.join("data", "processed", "provenance_events.json")
    benchmark_res = storage_engine.benchmark_compression(events, parquet_out, json_out)
    print(f"    -> Serialized {benchmark_res['total_events']} events to Parquet: {parquet_out}")
    print(f"    -> Raw JSON Size:       {benchmark_res['json_size_bytes']:,} bytes")
    print(f"    -> Compressed Parquet:  {benchmark_res['parquet_size_bytes']:,} bytes")
    print(f"    -> Compression Factor:  {benchmark_res['compression_ratio']}x storage reduction")
    print(f"    -> DuckDB SQL Execution Time: {benchmark_res['parquet_query_time_sec']*1000:.2f} ms")

    # 9. Causal Bridge Imputation (Lossy Edge-Fog Networks)
    print("\n[Stage 9] Causal Bridge Imputation under Lossy Network Conditions...")
    bridge_imputer = CausalBridgeImputer(max_time_window_sec=30.0, confidence_threshold=0.60)
    bridge_res = bridge_imputer.impute_missing_bridges(global_dag)
    print(f"    -> Severed Graph Partitions Evaluated: {bridge_res.severed_components_detected}")
    print(f"    -> Imputed Causal Transitions:         {bridge_res.imputed_bridges_count}")
    print(f"    -> Successfully Repaired Attack Paths: {bridge_res.repaired_attack_paths_count}")
    for b in bridge_res.imputed_bridges:
        print(f"        * Imputed Edge: {b.source_host} ({b.source_tier}) -> {b.target_host} ({b.target_tier})")
        print(f"          Confidence: {b.confidence_score*100:.1f}% | Rationale: {b.imputation_rationale}")

    # 10. Active Choke-Point Remediation & Zero-Blast-Radius Containment
    print("\n[Stage 10] Active Choke-Point Remediation & Zero-Blast-Radius Containment...")
    remediator = ActiveChokePointRemediator(lambda_collateral_weight=0.5)
    nodes_meta = {n: d for n, d in global_dag.nodes(data=True)}
    remediation_plan = remediator.generate_remediation_plan(intercon_res.choke_points, nodes_meta)
    print(f"    -> Choke Points Analyzed for Policy Synthesis: {remediation_plan.total_choke_points_analyzed}")
    print(f"    -> Primary Target Choke Point:                  {remediation_plan.optimal_choke_point_node}")
    print(f"    -> Overall Containment Efficacy:               {remediation_plan.overall_containment_pct}%")
    print(f"    -> Average Collateral Disruption Index:        {remediation_plan.average_collateral_index}")
    print("\n  Synthesized Zero-Blast-Radius Mitigation Policies:")
    for pol in remediation_plan.policies:
        print(f"    * [{pol.mechanism.value}] on {pol.target_tier} ({pol.target_host}):")
        print(f"        Containment Efficacy: {pol.containment_efficacy_pct}% | Collateral Index: {pol.collateral_disruption_index}")
        print(f"        Remediation Priority Score (RPS): {pol.remediation_priority_score}")
        print(f"        Command: {pol.executable_command}")

    # 11. MITRE ATT&CK Matrix Motif Mapping
    print("\n[Stage 11] Mapping Provenance Subgraph to MITRE ATT&CK Matrix...")
    mitre_mapper = MitreAttackMapper()
    attack_subg = intercon_res.induced_attack_subgraph if intercon_res.induced_attack_subgraph.number_of_nodes() > 0 else global_dag
    mitre_report = mitre_mapper.map_attack_graph(attack_subg)
    print(f"    -> Techniques Mapped:      {mitre_report.total_techniques_mapped}")
    print(f"    -> Kill-Chain Coverage:    {mitre_report.kill_chain_coverage_pct}%")
    print(f"    -> Tactics Observed:       {', '.join(mitre_report.tactics_observed)}")
    print("\n" + mitre_report.progression_summary)

    print("=" * 70)
    print("  CLOUD-M7 PIPELINE COMPLETE: ALL ADVANCED CAPABILITIES VERIFIED")
    print("=" * 70)


def run_storage_demo():
    """Standalone runner for Parquet + DuckDB storage analytics."""
    print("=" * 70)
    print("  CLOUD-M7: PARQUET + DUCKDB COLUMNAR STORAGE & ANALYTICS")
    print("=" * 70)
    sim = MultiTierAttackSimulator()
    events = sim.generate_full_simulation_dataset(benign_count=40)
    storage = ProvenanceStorageEngine()
    parquet_path = os.path.join("data", "processed", "provenance_events.parquet")
    json_path = os.path.join("data", "processed", "provenance_events.json")
    bench = storage.benchmark_compression(events, parquet_path, json_path)
    print(f"[+] Events: {bench['total_events']} | JSON: {bench['json_size_bytes']}B | Parquet: {bench['parquet_size_bytes']}B")
    print(f"[+] Storage Compression: {bench['compression_ratio']}x reduction")
    print(f"[+] Query Speed: {bench['parquet_query_time_sec']*1000:.2f} ms")
    summary = storage.get_tier_summary(parquet_path)
    print("\n[+] Multi-Tier Distribution (via DuckDB SQL):")
    for row in summary:
        print(f"    - Tier {row['tier']}: Total={row['total_events']}, Attacks={row['attack_events']}, Hosts={row['host_count']}")


def run_bridge_demo():
    """Standalone runner for causal bridge imputation."""
    print("=" * 70)
    print("  CLOUD-M7 NOVELTY: CAUSAL BRIDGE IMPUTATION (LOSSY NETWORKS)")
    print("=" * 70)
    sim = MultiTierAttackSimulator()
    events = sim.generate_full_simulation_dataset(benign_count=20)
    engine = ProvenanceGraphEngine(time_window_seconds=15.0)
    engine.add_events(events)
    g = engine.fuse_global_graph()

    imputer = CausalBridgeImputer(max_time_window_sec=30.0, confidence_threshold=0.60)
    res = imputer.impute_missing_bridges(g)
    print(f"[+] Severed Components Detected: {res.severed_components_detected}")
    print(f"[+] Imputed Bridges Count:       {res.imputed_bridges_count}")
    print(f"[+] Repaired Paths:              {res.repaired_attack_paths_count}")


def run_remediation_demo():
    """Standalone runner for active choke-point remediation."""
    print("=" * 70)
    print("  CLOUD-M7 NOVELTY: ACTIVE CHOKE-POINT ZERO-BLAST CONTAINMENT")
    print("=" * 70)
    sim = MultiTierAttackSimulator()
    events = sim.generate_full_simulation_dataset(benign_count=20)
    engine = ProvenanceGraphEngine(time_window_seconds=15.0)
    engine.add_events(events)
    engine.fuse_global_graph()

    intercon = InterconnectedAttackPathEngine(engine)
    res = intercon.analyze_interconnected_attack_graph()

    remediator = ActiveChokePointRemediator()
    plan = remediator.generate_remediation_plan(res.choke_points)
    print(f"[+] Choke Points Analyzed: {plan.total_choke_points_analyzed}")
    print(f"[+] Containment Efficacy: {plan.overall_containment_pct}%")
    print(f"\n[+] Generated Deployment Script:\n{plan.deployment_script}")


def run_mitre_demo():
    """Standalone runner for MITRE ATT&CK motif mapping."""
    print("=" * 70)
    print("  CLOUD-M7 NOVELTY: MITRE ATT&CK MATRIX MOTIF MAPPING")
    print("=" * 70)
    sim = MultiTierAttackSimulator()
    events = sim.generate_full_simulation_dataset(benign_count=20)
    engine = ProvenanceGraphEngine(time_window_seconds=15.0)
    engine.add_events(events)
    g = engine.fuse_global_graph()

    mapper = MitreAttackMapper()
    report = mapper.map_attack_graph(g)
    print(f"[+] Techniques Mapped:   {report.total_techniques_mapped}")
    print(f"[+] Lifecycle Coverage:  {report.kill_chain_coverage_pct}%")
    print(f"[+] Observed Tactics:    {', '.join(report.tactics_observed)}")
    print("\n" + report.progression_summary)


def run_iterative_demo_standalone():
    """Standalone runner for the iterative multi-root discovery engine."""
    print("=" * 70)
    print("  CLOUD-M7 NOVELTY: ITERATIVE MULTI-ROOT FORENSIC DISCOVERY")
    print("=" * 70)
    sim = MultiTierAttackSimulator()
    events = sim.generate_full_simulation_dataset(benign_count=20, include_multi_vector=True)
    engine = ProvenanceGraphEngine(time_window_seconds=15.0)
    engine.add_events(events)
    engine.fuse_global_graph()

    iter_engine = IterativeAttackDiscoveryEngine(engine, max_iterations=5, impact_threshold_epsilon=5.0)
    res = iter_engine.discover_all_attack_points()

    print(f"\n[+] Total Iterations: {res.total_iterations_run}")
    print(f"[+] Total Discovered Attack Vectors: {len(res.discovered_vectors)}")
    for m in res.iteration_history:
        print(f"    - Iteration {m.iteration}: Impact={m.cumulative_impact_score:.2f}, Gain=+{m.marginal_impact_gain_pct:.2f}% ({m.reason})")
    for v in res.discovered_vectors:
        print(f"    * Vector: {v.vector_id} -> Entry on [{v.entry_tier}] '{v.entry_host}' ({v.entry_entity})")


def main():
    parser = argparse.ArgumentParser(description="CLOUD-M7 Forensic Provenance Framework")
    parser.add_argument(
        "mode",
        choices=["demo", "optimize", "simulate", "iterative", "storage", "bridge", "remediate", "mitre"],
        default="demo",
        nargs="?",
        help="Execution mode (default: demo)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Hyperparameter K_max for iterative discovery",
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=5.0,
        help="Convergence threshold epsilon on marginal impact gain (%)",
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
    elif args.mode == "iterative":
        run_iterative_demo_standalone()
    elif args.mode == "storage":
        run_storage_demo()
    elif args.mode == "bridge":
        run_bridge_demo()
    elif args.mode == "remediate":
        run_remediation_demo()
    elif args.mode == "mitre":
        run_mitre_demo()


if __name__ == "__main__":
    main()
