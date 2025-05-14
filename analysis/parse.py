#!/usr/bin/env python3
import sys
import re

"""
Usage:
  python parse_pbbs_stats.py <stats.txt>

Parses the 3 gem5 stats dumps from the file stats.txt and prints
the key metrics for each region (Setup, Execution, Tear Down).
"""

# The key metrics we want to extract.
# For "committedInstType::*", we'll do partial matching.
KEY_METRICS = [
    "simInsts",
    "simOps",
    "system.cpu.numCycles",
    "simSeconds",
    "hostSeconds",
    "system.cpu.ipc",
    "system.cpu.cpi",
    "readReqs",
    "writeReqs",
    "avgRdBWSys",
    "avgWrBWSys"
    # We'll handle "committedInstType::" separately
]

REGION_NAMES = ["Setup Time", "Execution Time", "Tear Down Time"]

def parse_stats_file(filename):
    """
    Reads 'filename' (stats.txt) and splits out each region's lines.
    Returns a list of length 3, where each element is the lines belonging
    to that region (setup, execution, teardown).
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    # We'll accumulate lines for each region.
    # We'll store them as a list of lists of lines:
    #   all_regions[0] = lines for setup
    #   all_regions[1] = lines for execution
    #   all_regions[2] = lines for tear-down
    # (Assumes exactly three stats dumps.)
    all_regions = []
    current_region_lines = []
    region_count = 0

    capturing = False

    for line in lines:
        if "Begin Simulation Statistics" in line:
            # Start capturing lines for a new region
            capturing = True
            current_region_lines = []
        elif "End Simulation Statistics" in line:
            # Stop capturing, save the region
            capturing = False
            all_regions.append(current_region_lines)
            region_count += 1
        elif capturing:
            current_region_lines.append(line)

    # all_regions should have 3 sub-lists (setup, execution, teardown)
    if len(all_regions) != 3:
        print(f"[ERROR] Expected exactly 3 stats dumps, found {len(all_regions)}.")
    return all_regions


def extract_key_metrics(region_lines):
    """
    Given the lines for a single stats dump, return a dict of key_metric -> value
    plus a list of lines for all committedInstType.
    """
    metrics_dict = {}

    # A regex to parse lines of the form:
    # keyName        1234567    # Some comment
    # capturing "keyName" and "1234567"
    line_pattern = re.compile(r'^(\S+)\s+([\d.eE\-+NaN]+)\s+.*')

    for line in region_lines:
        match = line_pattern.match(line.strip())
        if not match:
            continue

        key = match.group(1)
        val_str = match.group(2)


        # If key is one of our KEY_METRICS, store it
        if key in KEY_METRICS:
            metrics_dict[key] = val_str

    return metrics_dict


def print_region_metrics(region_name, metrics_dict):
    """
    Pretty-print the metrics for a given region (Setup, Execution, Tear Down).
    """
    print(f"{region_name}:")
    for m in KEY_METRICS:
        if m in metrics_dict:
            print(f"  {m}: {metrics_dict[m]}")
        else:
            print(f"  {m}: -- (not found)")

    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_pbbs_stats.py <stats.txt>")
        sys.exit(1)

    stats_file = sys.argv[1]
    all_regions = parse_stats_file(stats_file)

    for i, region_lines in enumerate(all_regions):
        region_name = REGION_NAMES[i] if i < len(REGION_NAMES) else f"Region {i+1}"
        metrics_dict = extract_key_metrics(region_lines)
        print_region_metrics(region_name, metrics_dict)


if __name__ == "__main__":
    main()
