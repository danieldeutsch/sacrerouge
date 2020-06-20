# SacreROUGE
![Master](https://github.com/danieldeutsch/sacrerouge/workflows/Master/badge.svg?branch=master&event=push)

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
The `sacrerouge evaluate` command is typically used when you want to evaluate a summarization model on a particular dataset using one or more evaluation metrics.
It will calculate the value of each metric specified in the config file for each input summary.
The command outputs two files:
The "macro" file contains the metric values averaged over all of the inputs, and the "micro" file has the metric values for each input.

### Setting up Evaluation Metrics
Many of the evaluation metrics implemented in SacreROUGE require extra resources, often in the form of external libraries, data, or models.
Therefore, before you are able to evaluate with a metric, it may be necessary to download its dependencies.
The `sacrerouge setup-metric` command is the interface to do so.
Running that command will provide a list of metric names that can be setup.

You can view a list of the metrics implemented in this library [here](doc/metrics/metrics.md).

## Evaluating Metrics
The two main steps for evaluating a metric itself are to score a set of summaries across systems and inputs (using jackknifing where necessary) and then calculate the correlation of the metric's values to human judgments.
These are done in SacreROUGE with the `sacrerouge score` and `sacrerouge correlate` commands.

The `sacrerouge score` command will evaluate the input summaries with the metrics specified in the config file both normally and with jackknifing (if jackknifing can and needs to be done).
The output file will have the corresponding metrics' values for each input.
If the jackknifing was done, there will be an entry for that metric with a `_jk` suffix on the top-level entry.
For instance, one entry in the output could look like the following:
```json
{
  "my_metric": {
    "precision": 0.4,
    "recall": 0.8
  },
  "my_metric_jk": {
    "precision": 0.35,
    "recall": 0.7
  }
}
```
The `my_metric` entry is the standard score and `my_metric_jk` is the jackknifed version.

The `sacrerouge correlate` command will calculate several different correlation coefficients between the two provided input metrics.
The output will have the correlation metrics that are calculated in three different ways:

- Summary-level: Calculates the average correlation across inputs
- System-level: Calculates the average metric value per system, then calculates the correlation of those values
- Global: Directly calculates the correlation between all values of the metrics 

## Developing a New Metric
Every metric in SacreROUGE implements the `Metric` interface.
The constructor of `Metric` requires two arguments: the names of the `Field`s required to calculate the metric and the `Jackknifer` which implements jackknifing for the input fields.

Then, the `score_multi_all` method needs to be implemented.
The method accepts two arguments: `summaries_list` and `*args`.
Argument `summaries_list` is 2d list of summaries that should be evaluated.
Each inner list is a group that should be evaluated using the same context in `*args`, for example, using the same set of reference summaries.
Each element in `*args` has the same length as `summaries_list` and represents some context field.
The order of the fields in `*args` will be the same as the order provided to the constructor's `required_fields` argument. 

For instance, if your metric requires reference summaries and the input documents, the `score_multi_all` signature could look like this:
```python
def score_multi_all(self,
                    summaries_list: List[List[SummaryField]],
                    references_list: List[ReferencesField],
                    documents_list: List[DocumentsField]) -> List[List[MetricsDict]]:
    pass
```
where `references_list[i]` and `documents_list[i]` should be used to evaluate all of the summaries in `summaries_list[i]`.

The output of the `score_multi_all` should be a nested list of `MetricDict`s that is the same shape as `summaries_list`.

## Setting up a Dataset
SacreROUGE also contains data to load some summarization datasets and save them in a common format.
Run the `sacrerouge setup-dataset` command to see the available datasets, or check [here](doc/datasets/datasets.md).
