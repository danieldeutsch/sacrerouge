# Developing and Evaluating Metrics
This tutorial will cover:
- Implementing a reference-based evaluation metric
- Evaluating a metric via correlations
- Hypothesis testing two metrics' correlations

We recommend cloning the SacreROUGE repository and developing your metric within the SacreROUGE code base.
You can install SacreROUGE and implement a new metric in your own package, but you lose the benefit of SacreROUGE automatically creating a commandline interface for your metric (e.g., the `setup-metric`, `evaluate`, and `score` methods will not be automatically created).

## Implementing a Metric
Implementing a metric in SacreROUGE generally requires implementing two classes: one which contains the code to calculate the metric's score and one to download or setup any dependencies required by the metric.
We first explain the setup class followed by the implementation class.

### Setup Command
Many metrics require external resources to score summaries.
Users of the library can automatically download the required resources through the SacreROUGE `setup-metric` command.
For instance:
```bash
sacrerouge setup-metric <metric-name>
```
To create a similar command for your new metric, extend the `MetricSetupSubcommand` class as follows: 
```python
import argparse
from overrides import overrides

from sacrerouge.common import DATA_ROOT
from sacrerouge.commands import MetricSetupSubcommand


@MetricSetupSubcommand.register('tutorial')
class TutorialSetupCommand(MetricSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the Tutorial metric'
        self.parser = parser.add_parser('tutorial', description=description, help=description)
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        # Download dependencies to f'{DATA_ROOT}/metrics/tutorial'
        pass
```
The name given to the `MetricSetupSubcommand.register` function should be a name that is unique across different setup commands.
We recommend using the name of your metric.

The `add_subparser` method should add any commandline arguments that your setup function requires.
For example, you may require passing a file path to the setup method.
The file path argument can be added here, and it will be required by the corresponding `sacrerouge setup-metric <metric-name>` command.

The `run` method is what gets executed by SacreROUGE when the `setup-metric` command is run.
The `args` argument will be the commandline arguments as parsed by the `argparse` library.
Your metric's resources should be downloaded to a directory defined by `DATA_ROOT/metrics/<metric-name>`.
The `DATA_ROOT` contains the location where the user wants the SacreROUGE data to be saved on disk.
It is an environment variable that can be set by the user.

### Metric Implementation
Every metric within SacreROUGE extends the `Metric` class, which defines a set of methods that need to be implemented by every metric.
In this tutorial, we will be implementing a reference-based metric (i.e., one that scores a summary using a reference summary, such as ROUGE), so we will actually extend the `ReferenceBasedMetric` class.
`ReferenceBasedMetric` is just a subclass of `Metric` that provides some nicer syntactic sugar.
There is also a `ReferenceFreeMetric` (which does not require any other inputs) and a `DocumentBasedMetric` (which only uses the source documents).

There are 5 different methods in the `Metric` interface.
We recommend reading [this](evaluating-models.md) for a description of each of them.
However, you only need to implement `score_multi_all`.
(`evaluate` may be necessary if your metric calculates a score for a system from a set of input summaries using any other method than an average).

The `score_multi_all` method accepts two parameters, `summaries_list` and `references_list`, which contain the summaries that should be evaluated.
The summaries are grouped by common references.
This means the summaries in the list `summaries_list[i]` all need to be evaluated against the list of references in `references_list[i]`.
Here is an example metric implementation:
```python
from typing import List

from sacrerouge.data import MetricsDict
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric


@Metric.register('tutorial')
class TutorialMetric(ReferenceBasedMetric):
    def __init__(self, a: int, b: str, c: bool):
        super().__init__()
        # Do something with a, b, and c

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        metrics_lists = []
        for summaries, references in zip(summaries_list, references_list):
            metrics_list = []
            for summary in summaries:
                # Score this `summary` using `references`
                metrics_list.append(MetricsDict({
                    'my_score': 0.0
                }))
            metrics_lists.append(metrics_list)
        return metrics_lists
```

The metric scores are stored in a `MetricsDict`, which is just a dictionary with some additional methods.
The returned object should be a nested list that is parallel to the summaries in `summaries_list`.

Next, we discuss how to evaluate your metric by calculate the correlation between its scores and human judgments.
If you want to use your metric to score a system, see [here](evaluating-models.md).

## Evaluating a Metric
Evaluation metrics are themselves evaluated based on how similarly they score systems and summaries to humans.
Here, we describe how to do this in SacreROUGE.

### Scoring Summaries
In order to evaluate a metric, you first need to score a set of summaries with your metric.
If you already have these scores, you can skip to the next part.

The summaries should be stored in a `jsonl` file, where each line is a flattened JSON object with the following format:
```json
{
    "instance_id": "2",        // the unique ID for the input document(s)
    "summarizer_id": "7",      // the unique ID for the system which produced this summary
    "summarizer_type": "peer", // either "peer" or "reference". Use "peer" for model-generated summaries
                               // and "reference" for human-written summaries
    "summary": {
        "text": "..."          // the text of the summary, either a `str` or `List[str]`
    },
    "references": [            // a list of references
        {
            "text": "..."      // the text of the reference, either a `str` or `List[str]`
        },
        ...
    ]
}
```

Then, you can score all of the summaries in this file with a command like the following:
```bash
sacrerouge tutorial score \
    --input-files <path-to-file-with-summaries> \
    --dataset-reader reference-based \
    --output-jsonl <path-to-the-output-file> \
    --a 5 \
    --b testing \
    --c true
```
The parameters in the constructor (`a`, `b`, and `c`) will automatically have a corresponding commandline argument.
If your summaries are in a different format, you can define your own `DatasetReader`.
See `ReferenceBasedDatasetReader` for an example dataset reader implementation.
After, you can pass the name of the reader as the `--dataset-reader` argument.

The output file will have one JSON object per line which looks like the following:
```json
{
  "instance_id": "2",
  "summarizer_id": "7",
  "summarizer_type": "peer",
  "metrics": {
    "my_score": 0.0
  }
}
```
One object will exist for every input summary.
If your instances have multiple reference summaries or you are scoring reference summaries, there will also be a version of your metric with a `_jk` underscore, which is the jackknifed version of your metric.
The jackknifed metric can be used to compare scoring model-generated summaries' scores to human-written reference summaries' scores.
This can be disabled with the `--disable-peer-jackknifing` flag.

### Calculating Correlations
After you have calculated your metric's score for a set of summaries, you need to calculate the correlation to human scores for those summaries.
The human scores must be in the same score format as above.
They can be in the same or separate files to where your metric's scores are.

The correlation can be calculated using the following command:
```bash
sacrerouge correlate \
    --metrics-jsonl-files <path-to-the-files-with-the-scores> \
    --metrics <ground-truth-metric> <your-metric-name> \
    --summarizer-type peer \
    --output-file <path-to-output-json>
```
The `metrics-jsonl-files` can be a list of files with different metrics dictionaries, which will be merged if there are repeated (instance, summarizer) pairs.
The arguments to `--metrics` should be the name of the ground-truth metric and your metric (the order does not matter).
If the metric in the `MetricsDict` is nested (e.g., `{rouge-1: {"recall": 0.5, {"precision": 0.3}}`), the dictionary will be flattened and the keys will be joined with underscores (e.g., `rouge-1_recall`, `rouge-1_precision`).
Use the flattened name for the commandline parameter.

The `--summarizer-type` specifics what type of summaries you want to use to calculate the correlation.
If `reference` or `all`, you should use the jackknifed version of the metric (for reference-based metrics) and specify the `_jk` version to the `--metrics` argument.

The correlation will be calculated at three different levels with three different correlation coefficients.
We refer the reader to [1] for a description of the summary- and system-level correlation calculations.

The `correlate` command will also calculate a 95% confidence interval for the correlation values using the `BOOT-BOTH` method from [1].
This can be disabled or changed using the `--confidence-interval-method` parameter.

## Hypothesis Testing
If you have two metrics and you are testing whether one metric correlates better to some ground-truth score than the other does, you need to use a hypothesis test.
The hypothesis tests implemented in SacreROUGE are described in [1].
The a single-tailed test with alpha = 0.05 and the PERM-BOTH method is used by default.
It can be run by the following command:
```bash
sacrerouge stat-sig-test \
    --metrics-jsonl-files <path-to-files-with-metric-scores> \
    --dependent-metric <dependent-metric> \
    --metric-A <metric1> \
    --metric-B <metric2> \
    --summarizer-type peer \
    --output-file <path-to-output-file>
```
By default, the null hypothesis will be `rho(metric1, dependent-metric) - rho(metric2, dependent-metric) <= 0`.
If you are arguing your metric correlates better than another, yours should be `metric1`.

The output file will contain the test results for each of the correlation levels and coefficients.

## Bonferroni Correction
If you run a set of hypothesis tests (e.g., compare your metric to several other metrics), you should run the Bonferroni Correction.
See [2] for details.

This can be done via
```
sacrerouge partial-conjunction-test \
    --pvalue-json-files <path-to-stat-sig-test-result-jsons> \
    --names <name-of-the-other-metrics> \
    --output-file <path-to-output-file>
```
The `--names` argument should be a list of metric names that corresponds to the files in `--pvalue-json-files`.
For instance, you may compare your metric to ROUGE, BERTScore, and QAEval.
You should run the `stat-sig-test` command against those three metrics, then pass the result files to the `--pvalue-json-files` argument and `--names` should be the names of those 3 metrics.


## References
[1] Daniel Deutsch, Rotem Dror, and Dan Roth. [A Statistical Analysis of Summarization Evaluation Metrics using Resampling Methods](https://arxiv.org/abs/2104.00054)
[2] Rotem Dror, Gili Baumer, Marina Bogomolov, Roi Reichart. [Replicability Analysis for Natural Language Processing: Testing Significance with Multiple Datasets](https://www.aclweb.org/anthology/Q17-1033.pdf). TACL, 2017.