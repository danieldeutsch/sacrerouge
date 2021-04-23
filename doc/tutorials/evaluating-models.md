# Evaluating Summarization Models
This tutorial will cover how to use a metric which is already implemented in SacreROUGE to score a summarization system.
If you want to implement a new metric, see [here](developing-metrics.md).
This tutorial will use ROUGE as the demo metric, but the list of metrics which are currently implemented in SacreROUGE can be found [here](../metrics/metrics.md).


## Installing Dependencies
Many metrics require runtime dependencies, and those dependencies can be downloaded via the metric's setup command.
For example, running ROUGE requires the original Perl code.
It can be downloaded with
```bash
sacrerouge setup-metric rouge
```
The dependencies will be downloaded to the `$SACREROUGE_DATA_ROOT` directory, which defaults to `~/.sacrerouge`, though you may override it as an environment variable.

Some of the metrics will require other Python packages that are not installed by SacreROUGE's `pip install`.
We did not include those packages by default because they could be large and bloat the package.
You should see the [documentation](../metrics) for each metric to understand what needs to be done to run the metric.

## Scoring a System with the Python Interface
Each metric in SacreROUGE implements a common interface so it is easy to score a summary with multiple metrics.
The exact semantics for reference-based, document-based, or reference-free metrics are slightly different, but below is an explanation for the reference-based methods:

- `score`: Scores a single summary using its references:
```python
def score(summary: SummaryType,
          references: List[ReferenceType]) -> MetricsDict
```
  
- `score_all`: Scores a list of summaries, each with their own set of references.
`summaries[i]` should be scored with the references at `references_list[i]`.
```python
def score_all(summaries: List[SummaryType],
              references_list: List[List[ReferenceType]]) -> List[MetricsDict]
```

- `score_multi`: Scores a list of summaries which share common references.
`summaries[i]` should be scored with `references` for all `i`.
```python
def score_multi(summaries: List[SummaryType],
                references: List[ReferenceType]) -> List[MetricsDict]
```

- `score_multi_all`: Scores a list of list summaries, where each inner list shares common references.
All the summaries in the list `summaries_list[i]` should be scored using the references at `references_list[i]`. 
```python
def score_multi_all(summaries_list: List[List[SummaryType]],
                    references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]
```

- `evaluate`: Score a list of summaries, each with their own references, and calculate system-level metrics:
```python
def evaluate(summaries: List[SummaryType],
             references_list: List[List[ReferenceType]]) -> Tuple[MetricsDict, List[MetricsDict]]
```

The output to each of the above methods will be an object that contains a `MetricsDict` that corresponds to each of the input summaries.

It is likely that if you are using the Python interface, you only care about `score` and `score_all`.
Here is an example for ROUGE:
 ```python
>>> summary = 'Dan walked to the bakery this morning.'
>>> reference = 'Dan went to buy scones earlier this morning.'
>>>
>>> from sacrerouge.metrics import Rouge
>>> rouge = Rouge(max_ngram=2)
>>> rouge.score(summary, [reference])
{'rouge-1': {'recall': 50.0, 'precision': 57.143, 'f1': 53.333}, 'rouge-2': {'recall': 14.285999999999998, 'precision': 16.667, 'f1': 15.384999999999998}}
```


## Scoring a System with the CommandLine
The summaries from a system must be in a file in which each line is a serialized JSON object.
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
Since ROUGE is a reference-based metric, the `"references"` field is required.
Otherwise, it isn't.
If your data is not in this format, you can write your own custom dataset reader.
See `ReferenceBasedDatasetReader` for an example dataset reader implementation.
The summaries should all correspond to one system (so the `summarizer_id` should be the same).

Then, the system score can be calculated using the following command:
```
sacrerouge rouge evaluate \
    --input-files <files-with-the-summaries> \
    --dataset-reader reference-based \
    --macro-output-json <system-level-results-json> \
    --micro-output-jsonl <summary-level-results-jsonl>
```
The `macro-output-json` will contain the system-level results (averaged over all of the input instances).
The `micro-output-jsonl` will have the metric's score for each individual summary.

Metric-specific parameters defined in their constructors can also be passed via the command line.
See `sacrerouge <metric-name> evaluate` for what parameters are available. 