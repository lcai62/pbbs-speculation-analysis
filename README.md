# pbbs-characterization-gem5

Experiments and analysis for evaluating the impact of memory speculation techniques, like prefetching and branch prediction, 
workloads from PBBS, using the gem5 simulator.

## Built With

[![Python][python-shield]][python-url]  
[![gem5][gem5-shield]][gem5-url]  
[![Matplotlib][matplotlib-shield]][matplotlib-url]  
[![NumPy][numpy-shield]][numpy-url]

## Contents

- `analysis/`: data parsing and plotting code
- `benchmarks/`: benchmarking binary files
- `data/`: simulation outputs
- `inputs/`: generated simulation inputs
- `scripts/`: python simulation scripts

> The gem5 binaries used in these experiments can be found at [gem5.org](https://www.gem5.org).


## Experiments

### Exploration 1: Prefetching Effects
Evaluates how attaching prefetchers to the L1 instruction and data caches impacts performance. Prefetcher types and parameters are varied to analyze access latency and bandwidth effects across benchmarks.

### Exploration 2: Branch Predictor Accuracy
Analyzes how different branch predictors perform across PBBS benchmarks. Investigates how the configuration (e.g., size) of a Tournament predictor influences prediction accuracy and control flow performance.

<!-- MARKDOWN LINKS & IMAGES -->
[python-shield]: https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white
[python-url]: https://www.python.org/

[gem5-shield]: https://img.shields.io/badge/gem5-orange?style=for-the-badge&logo=gnu&logoColor=white
[gem5-url]: https://www.gem5.org/

[matplotlib-shield]: https://img.shields.io/badge/Matplotlib-ff69b4.svg?style=for-the-badge&logo=plotly&logoColor=white
[matplotlib-url]: https://matplotlib.org/

[numpy-shield]: https://img.shields.io/badge/NumPy-013243.svg?style=for-the-badge&logo=numpy&logoColor=white
[numpy-url]: https://numpy.org/
