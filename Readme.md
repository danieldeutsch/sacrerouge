# SacreROUGE
SacreROUGE is a library dedicated to summarization evaluation metrics.
Its two main uses are to evaluate summarization systems and to evaluation the evaluation metrics themselves by calculating their correlations to human judgments.

The development of SacreROUGE was motivated by three problems: 

- Datasets for evaluating summarization metrics formatted differently and can be hard to parse (e.g., DUC and TAC).
SacreROUGE addresses this problem by providing dataset readers to load and reformat the data into a common schema.

- The official implementations for various evaluation metrics do not use a common interface, so running many of them on a dataset is frustrating and time consuming.
SacreROUGE wraps many popular evaluation metrics in a common interface so it is straightforward and fast to setup and run a new metric.

- Evaluating metrics can be tricky.
There are there are several different correlation coefficients commonly used, there are different levels at which the correlation can be calculated, and comparing system summaries to human summaries requires implementing jackknifing.
The evaluation code in SacreROUGE is shared among all of the metrics, so once a new metric implements the common interface, all of the details of the evaluation are taken care of for free.

## Installing
`pip install sacrerouge`

## Evaluating Summarization Systems
TODO: explain the `sacrerouge evaluate` command

### Setting up Evaluation Metrics
TODO: explain the `sacrerouge setup-metric` command

## Evaluating Metrics
TODO: explain the `sacrerouge score` and `sacrerouge correlate` commands

## Developing a New Metric
TODO: explain the `Metric` interface

## Setting up a Dataset
TODO: explain the `sacrerouge setup-dataset` command
