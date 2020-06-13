# MoverScore
MoverScore [1] is a reference-based evaluation metric using an Earth Mover's Distance between a summary and its reference that uses contextual word representations.
Our implementation uses the `moverscore` [pip package](https://github.com/AIPHES/emnlp19-moverscore).

## Setting Up
To set up MoverScore, pip install the package:
```bash
pip3 install moverscore
```
There are currently several libraries which also should be installed and won't be installed with the pip command, so please try to import `moverscore_v2` in a Python terminal to verify it is installed.

Then, some data dependencies can be downloaded via:
```bash
sacrerouge setup-metric moverscore
```

To verify your installation, run:
```bash
pytest sacrerouge/tests/metrics/moverscore_test.py
```

## References
[1] Wei Zhao, Maxime Peyrard, Fei Liu, Yang Gao, Christian M. Meyer, and Steffen Eger. [MoverScore: Text Generation Evaluating with Contextualized Embeddings and Earth Mover Distance](https://www.aclweb.org/anthology/D19-1053/). EMNLP 2019.