#!/usr/bin/env python3

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

KEY_METRICS = [
    "simInsts",
    "simOps",
    "system.cpu.numCycles",
    "simSeconds",
    "hostSeconds",
    "system.cpu.ipc",
    "system.cpu.cpi",
    "system.mem_ctrl.readReqs",
    "system.mem_ctrl.writeReqs",
    "system.mem_ctrl.avgRdBWSys",
    "system.mem_ctrl.avgWrBWSys"
]

OUTDIRS = [
    "words_1k_out",
    "words_2k_out",
    "words_4k_out",
    "words_8k_out",
    "words_16k_out",
    "words_32k_out",
    "words_64k_out",
]

INPUT_LABELS = ["1000", "2000", "4000", "8000", "16000", "32000", "64000"]

PHASES = ["Setup", "Execution", "Teardown"]


def parse_three_stats_dumps(stats_file):
    """
    read 'stats.txt' file which has three dumps
    returns list [setup_lines, execution_lines, teardown_lines],
    where each element is a list of lines for that region.
    """
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

def extract_key_metrics(lines):
    """
    parse key metrics, returns a dict { metric_name: float_value }.
    """
    results = {}
    pattern = re.compile(r'^(\S+)\s+([\d.eE+\-NaN]+)\s+.*')
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
    return results

def main():
    # data[outdir][phase][metric] = value
    data = {}

    for outdir in OUTDIRS:
        stats_path = os.path.join(outdir, "stats.txt")
        if not os.path.isfile(stats_path):
            print(f"[ERROR] {stats_path} not found, skipping.")
            continue

        regions = parse_three_stats_dumps(stats_path)
        if len(regions) != 3:
            print(f"[ERROR] {stats_path} has {len(regions)} dumps")
            continue

        data[outdir] = {}
        for i, phase_name in enumerate(PHASES):
            lines = regions[i]
            metrics_dict = extract_key_metrics(lines)
            data[outdir][phase_name] = metrics_dict

    # one bar chart per metric
    # create a color map for the bars of each input size
    cmap = plt.cm.get_cmap("tab10")
    num_inputs = len(OUTDIRS)
    colors = [cmap(i % 10) for i in range(num_inputs)]

    for metric in KEY_METRICS:
        # phase_percentages[phase][idx_outdir] = percentage for that outdir & phase
        phase_percentages = {ph: [] for ph in PHASES}

        for idx, outdir in enumerate(OUTDIRS):
            if outdir not in data:
                for ph in PHASES:
                    phase_percentages[ph].append(0.0)
                continue

            val_setup = data[outdir]["Setup"].get(metric, 0.0)
            val_exec  = data[outdir]["Execution"].get(metric, 0.0)
            val_teard = data[outdir]["Teardown"].get(metric, 0.0)

            total = val_setup + val_exec + val_teard
            if total == 0:
                pct_setup, pct_exec, pct_teard = 0.0, 0.0, 0.0
            else:
                pct_setup = 100.0 * (val_setup / total)
                pct_exec  = 100.0 * (val_exec  / total)
                pct_teard = 100.0 * (val_teard / total)

            phase_percentages["Setup"].append(pct_setup)
            phase_percentages["Execution"].append(pct_exec)
            phase_percentages["Teardown"].append(pct_teard)

        fig, ax = plt.subplots(figsize=(8, 5))
        x_phase = np.arange(len(PHASES))  # [0,1,2]
        bar_width = 1.0 / (num_inputs + 1)

        # shift horizontally
        offset_base = - (num_inputs - 1) * bar_width / 2.0

        for i, outdir in enumerate(OUTDIRS):

            y_vals = [
                phase_percentages["Setup"][i],
                phase_percentages["Execution"][i],
                phase_percentages["Teardown"][i]
            ]
            x_positions = x_phase + (offset_base + i*bar_width)

            ax.bar(
                x_positions,
                y_vals,
                width=bar_width,
                color=colors[i],
                alpha=0.85
            )

        ax.set_xticks(x_phase)
        ax.set_xticklabels(PHASES)
        ax.set_ylabel("Percentage (%)")
        ax.set_title(f"Distribution of {metric} across Setup/Execution/Teardown")

        legend_patches = []
        for i in range(num_inputs):
            patch = Patch(color=colors[i], label=INPUT_LABELS[i])
            legend_patches.append(patch)

        ax.legend(handles=legend_patches, title="Input Sizes", loc="best")

        plt.tight_layout()
        outname = f"{metric}_phase_distribution.png"
        plt.savefig(outname)
        plt.close()

        print(f"saved: {outname}")

    print("done")

if __name__ == "__main__":
    main()
