#!/usr/bin/env python3

import subprocess

benchmarks = [
    ("run_pbbs_bfs2.py", "graph_3200"),
    ("run_pbbs_knn2.py", "knn_16k"),
    ("run_pbbs_nbody2.py", "nbody_1600"),
    ("run_pbbs_isort2.py", "random_64k_int"),
    ("run_pbbs_sa2.py", "words_32k")
]

gem5_bin = '/u/csc368h/winter/pub/bin/gem5.opt'


for script, input_data in benchmarks:
    outdir = f"{script[:-3]}_{input_data}_out"
    
    cmd = [
        gem5_bin,
        f'--outdir={outdir}',
        script,
        '--binary_args', input_data
    ]
    
    print(f"\nRunning gem5 for {script} with data={input_data}")
    print("Command: " + " ".join(cmd))
    
    subprocess.run(cmd, check=True)

print("\nAll benchmarks completed.")
