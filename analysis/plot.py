#!/usr/bin/env python3

import os
import re
import matplotlib.pyplot as plt

# Define key metrics to extract
KEY_METRICS = [
    "system.cpu.branchPred.condPredicted",
    "system.cpu.branchPred.condIncorrect"
]

# Output directories with different localCtrBits values
OUTDIRS = {
    # BFS
    "run_pbbs_bfs_graph_3200_out": 1,
    "run_pbbs_bfs2_graph_3200_out": 2,
    "run_pbbs_bfs3_graph_3200_out": 4,

    # KNN
    "run_pbbs_knn_knn_16k_out": 1,
    "run_pbbs_knn2_knn_16k_out": 2,
    "run_pbbs_knn3_knn_16k_out": 4,

    # NBody
    "run_pbbs_nbody_nbody_1600_out": 1,
    "run_pbbs_nbody2_nbody_1600_out": 2,
    "run_pbbs_nbody3_nbody_1600_out": 4,

    # Suffix Array
    "run_pbbs_sa_words_32k_out": 1,
    "run_pbbs_sa2_words_32k_out": 2,
    "run_pbbs_sa3_words_32k_out": 4,

    # iSort
    "run_pbbs_isort_random_64k_int_out": 1,
    "run_pbbs_isort2_random_64k_int_out": 2,
    "run_pbbs_isort3_random_64k_int_out": 4
}

# Pretty names for benchmarks (labeling localCtrBits)
BENCHMARK_NAMES = {
    "run_pbbs_bfs_graph_3200_out": "BFS (graph_3200)",
    "run_pbbs_bfs2_graph_3200_out": "BFS (graph_3200)",
    "run_pbbs_bfs3_graph_3200_out": "BFS (graph_3200)",

    "run_pbbs_knn_knn_16k_out": "KNN (knn_16k)",
    "run_pbbs_knn2_knn_16k_out": "KNN (knn_16k)",
    "run_pbbs_knn3_knn_16k_out": "KNN (knn_16k)",

    "run_pbbs_nbody_nbody_1600_out": "NBody (nbody_1600)",
    "run_pbbs_nbody2_nbody_1600_out": "NBody (nbody_1600)",
    "run_pbbs_nbody3_nbody_1600_out": "NBody (nbody_1600)",

    "run_pbbs_sa_words_32k_out": "Suffix Array (words_32k)",
    "run_pbbs_sa2_words_32k_out": "Suffix Array (words_32k)",
    "run_pbbs_sa3_words_32k_out": "Suffix Array (words_32k)",

    "run_pbbs_isort_random_64k_int_out": "iSort (random_64k_int)",
    "run_pbbs_isort2_random_64k_int_out": "iSort (random_64k_int)",
    "run_pbbs_isort3_random_64k_int_out": "iSort (random_64k_int)"
}


def parse_three_stats_dumps(stats_file):
    """ Reads 'stats.txt' file which has three dumps (setup, execution, teardown). """
    with open(stats_file, 'r') as f:
        lines = f.readlines()

    regions = []
    capturing = False
    current_block = []

    for line in lines:
        if "Begin Simulation Statistics" in line:
            capturing = True
            current_block = []
        elif "End Simulation Statistics" in line:
            capturing = False
            regions.append(current_block)
        elif capturing:
            current_block.append(line)

    return regions


def extract_key_metrics_from_lines(lines):
    """ Extracts key branch prediction metrics from the given lines of text. """
    pattern = re.compile(r'^(\S+)\s+([\d.eE+\-NaN]+)\s+.*')
    results = {}

    for line in lines:
        match = pattern.match(line.strip())
        if match:
            key = match.group(1)
            val_str = match.group(2)
            if key in KEY_METRICS:
                try:
                    results[key] = float(val_str)
                except ValueError:
                    results[key] = float('nan')

    if "system.cpu.branchPred.condPredicted" in results and "system.cpu.branchPred.condIncorrect" in results:
        cpred = results["system.cpu.branchPred.condPredicted"]
        cincorr = results["system.cpu.branchPred.condIncorrect"]
        results["bpAccuracy"] = 1.0 - (cincorr / cpred) if cpred > 0 else 0.0

    return results


def main():
    data = {}

    # Parse statistics for each benchmark
    for outdir, localCtrBits in OUTDIRS.items():
        stats_path = os.path.join(outdir, "stats.txt")
        if not os.path.isfile(stats_path):
            print(f"[ERROR] {stats_path} not found, skipping.")
            continue

        regions = parse_three_stats_dumps(stats_path)
        if len(regions) != 3:
            continue

        execution_lines = regions[1]
        metrics = extract_key_metrics_from_lines(execution_lines)
        data[outdir] = metrics
        data[outdir]["localCtrBits"] = localCtrBits  # Store localCtrBits

    # Sort results by benchmark name first, then localCtrBits
    sorted_data = sorted(data.items(), key=lambda x: (BENCHMARK_NAMES[x[0]], x[1]["localCtrBits"]))

    # Print table header
    print("\nBranch Prediction Accuracy Results for Different `localCtrBits` Values:\n")
    print(f"{'Benchmark':<35} {'localCtrBits':<15} {'Cond. Predicted':<20} {'Cond. Incorrect':<20} {'Accuracy (%)':<15}")
    print("=" * 120)

    last_benchmark = None  # Track last printed benchmark name

    # Print results in table format
    for outdir, metrics in sorted_data:
        name = BENCHMARK_NAMES.get(outdir, outdir)  # Get pretty name
        localCtrBits = metrics.get("localCtrBits", "Unknown")

        cond_pred = int(metrics.get("system.cpu.branchPred.condPredicted", 0))
        cond_incorr = int(metrics.get("system.cpu.branchPred.condIncorrect", 0))
        accuracy = metrics.get("bpAccuracy", 0) * 100  # Convert to percentage

        # Print separator only when the benchmark changes
        if last_benchmark and last_benchmark != name:
            print("-" * 120)  # ✅ ADDITION: Print separator between benchmarks only

        print(f"{name:<35} {localCtrBits:<15} {cond_pred:<20} {cond_incorr:<20} {accuracy:.2f}%")

        last_benchmark = name  # Update last benchmark name

    print("=" * 120)


if __name__ == "__main__":
    main()
