# SacreROUGE
![Master](https://github.com/danieldeutsch/sacrerouge/workflows/Master/badge.svg?branch=master&event=push)

**New (2021-08-04):**
We now have Docker versions of several evaluation metrics included in the library, which makes it even easier to run them as long as you have Docker installed.
Our implementations are wrappers around the metrics included in the [Repro library](https://github.com/danieldeutsch/repro).
See [here](docs/docker/Readme.md) for more information about the Dockerized metrics.

SacreROUGE is a library dedicated to the development and use of summarization evaluation metrics.
It can be viewed as an [AllenNLP](https://github.com/allenai/allennlp) for evaluation metrics (with an emphasis on summarization).
The inspiration for the library came from [SacreBLEU](https://github.com/mjpost/sacreBLEU), a library with a standardized implementation of BLEU and dataset readers for common machine translation datasets.
See our [paper](https://arxiv.org/abs/2007.05374) for more details or [this Jupyter Notebook](https://colab.research.google.com/drive/1RikOFUEx299c8qxd6IfCLe3KeuLX31I4?usp=sharing) that was presented at the [NLP-OSS 2020](https://nlposs.github.io/2020/) and [Eval4NLP 2020](https://nlpevaluation2020.github.io/) workshops for a demo of the library.

The development of SacreROUGE was motivated by three problems: 

- The official implementations for various evaluation metrics do not use a common interface, so running many of them on a dataset is frustrating and time consuming.
SacreROUGE wraps many popular evaluation metrics in a common interface so it is straightforward and fast to setup and run a new metric.

- Evaluating metrics can be tricky.
There are there are several different correlation coefficients commonly used, there are different levels at which the correlation can be calculated, and comparing system summaries to human summaries requires implementing jackknifing.
The evaluation code in SacreROUGE is shared among all of the metrics, so once a new metric implements the common interface, all of the details of the evaluation are taken care of for free.

- Datasets for evaluating summarization metrics formatted differently and can be hard to parse (e.g., DUC and TAC).
SacreROUGE addresses this problem by providing dataset readers to load and reformat the data into a common schema.

The two main uses of SacreROUGE are to evaluate summarization systems and to evaluation the evaluation metrics themselves by calculating their correlations to human judgments.

## Installing
The easiest method of using SacreROUGE is to install the [pypi library](https://pypi.org/project/sacrerouge/) via:
```
pip install sacrerouge
```
This will add a new `sacrerouge` bash command to your path, which serves as the primary interface for the library.

## Tutorials
We provide several different tutorials for how to use SacreROUGE based on your use case:
- [Using SacreROUGE to evaluate a model](doc/tutorials/evaluating-models.md)
- [Using SacreROUGE to develop and evaluate a new metric](doc/tutorials/developing-metrics.md)

### Setting up a Dataset
SacreROUGE  contains data to load some summarization datasets and save them in a common format.
Run the `sacrerouge setup-dataset` command to see the available datasets, or check [here](doc/datasets/datasets.md).

### Data Visualization
We have also written two data visualization tools.
The [first tool](https://danieldeutsch.github.io/pages/pyramid-visualization.html) visualizes a Pyramid and optional Pyramid annotations on peer summaries.
It accepts the `pyramid.jsonl` and `pyramid-annotations.jsonl` files which are saved by some of the dataset readers.

The [second tool](https://danieldeutsch.github.io/pages/rouge-visualization.html) visualizes the n-gram matches that are used to calculate the ROUGE score.
It accepts the `summaries.jsonl` files which are saved by some of the dataset readers.

## Papers
Relevant publications which are implemented in the SacreROUGE framework include:
- [Understanding the Extent to which Summarization Evaluation Metrics Measure the Information Quality of Summaries](https://arxiv.org/abs/2010.12495)
- [Towards Question-Answering as an Automatic Metric for Evaluating the Content Quality of a Summary](https://arxiv.org/abs/2010.00490)
- [A Statistical Analysis of Summarization Evaluation Metrics using Resampling Methods](https://arxiv.org/abs/2104.00054)

## Help
If you have any questions or suggestions, please open an issue or contact me (Dan Deutsch).

## Citation
If you use SacreROUGE for your paper, please cite the following paper:
```
@inproceedings{deutsch-roth-2020-sacrerouge,
    title = {{SacreROUGE: An Open-Source Library for Using and Developing Summarization Evaluation Metrics},
    author = "Deutsch, Daniel  and
      Roth, Dan",
    booktitle = "Proceedings of Second Workshop for NLP Open Source Software (NLP-OSS)",
    month = nov,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.nlposs-1.17",
    pages = "120--125"
}
```
