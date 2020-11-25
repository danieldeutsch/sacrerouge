# SacreROUGE
![Master](https://github.com/danieldeutsch/sacrerouge/workflows/Master/badge.svg?branch=master&event=push)

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

## Supported Metrics
The list of metrics which are currently supported by SacreROUGE can be found [here](doc/metrics/metrics.md).
Running many of the metrics require some dependencies, either data resources, models, or source code that needs to be compiled.
Therefore, before you are able to use some of the metrics, these dependencies must be taken care of.

Setting up a metric in SacreROUGE is straightforward.
Each metric has a command that can be run that will prepare its dependencies.
The commands look like the following:
```bash
sacrerouge setup-metric <metric-name>
```
where `<metric-name>` is the registered name of the metric you are setting up.
The metric names are included in their respective documentation.
The dependencies will be downloaded to `~/.sacrerouge` (or `$SACREROUGE_DATA_ROOT` if the environment variable exists).

For example, to setup the AutoSummENG metric, the following command will clone the official Java repository and compile the necessary jars with Maven:
```bash
sacrerouge setup-metric autosummeng
```

## Python Interface
All of the metrics supported by SacreROUGE extend the `Metric` base class, and therefore share a common Python-based interface.
They can be imported and run, like as follows:

```python
>>> summary = 'Dan walked to the bakery this morning.'
>>> reference = 'Dan went to buy scones earlier this morning.'
>>>
>>> from sacrerouge.metrics import Rouge
>>> rouge = Rouge(max_ngram=2)
>>> rouge.score(summary, [reference])
{'rouge-1': {'recall': 50.0, 'precision': 57.143, 'f1': 53.333}, 'rouge-2': {'recall': 14.285999999999998, 'precision': 16.667, 'f1': 15.384999999999998}}
>>>
>>> from sacrerouge.metrics import AutoSummENG
>>> autosummeng = AutoSummENG()
>>> autosummeng.score(summary, [reference])
{'AutoSummENG': 0.300813, 'MeMoG': 0.300813, 'NPowER': 0.308208}
```
Behind the scenes, the `score` method is running a subprocess to run the original Perl and Java code for ROUGE and AutoSummENG, respectively.

The methods supported by `Metric`s each have slightly different semantics.
Their signatures will be slightly different across `Metric`s depending on the required fields (e.g., some may require the input document, others reference summaries).
The methods are explained below, using an example `Metric` that requires a list of reference summaries and the input document to score a summary: 
- `score`: Scores a single summary using its references and input document:
```python
def score(summary: SummaryType,
          references: List[ReferenceType],
          document: DocumentType) -> MetricsDict
```
  
- `score_all`: Scores a list of summaries, each with their own set of references and input documents:
```python
def score_all(summaries: List[SummaryType],
              references_list: List[List[ReferenceType]],
              documents: List[DocumentType]) -> List[MetricsDict]
```

- `score_multi`: Scores a list of summaries which share common references and input document:
```python
def score_multi(summaries: List[SummaryType],
                references: List[ReferenceType],
                document: DocumentType) -> List[MetricsDict]
```

- `score_multi_all`: Scores a list of list summaries, where each inner list shares common references and input documents: 
```python
def score_multi_all(summaries_list: List[List[SummaryType]],
                    references_list: List[List[ReferenceType]],
                    documents: List[DocumentType]) -> List[List[MetricsDict]]
```
Here, the summaries in `summaries_list[i]` should all be scored against `references_list[i]` and `documents[i]`.
The output `MetricsDict`s will be parallel to the `summaries_list`.

- `evaluate`: Score a list of summaries, each with their own references and input document, and calculate system-level metrics:
```python
def evaluate(summaries: List[SummaryType],
             references_list: List[List[ReferenceType]],
             documents: List[DocumentType]) -> Tuple[MetricsDict, List[MetricsDict]]
```
The first returned value is the system-level metrics.
The second returned value contains the input-level metrics for each summary.
This method would be most commonly used to evaluate a summarization system over a set of output summaries.

## Command Line Interface 
In addition to the Python interface, SacreROUGE also contains a command line interface.
The primary commands are `evaluate`, `score`, and `correlate`, described next.

### Evaluating Systems
The `evaluate` command is most often used to evaluate a summarization model based on its output.
Each `Metric` has its own automatically generated `evaluate` command:
```bash
sacrerouge rouge evaluate \
    <macro-output-file> \
    <micro-output-file> \
    --dataset-reader reference-based \
    --input-files <input-file>+
    --max_ngram 2 \
    --use_porter_stemmer false
```
All of the evaluate commands require an output path for the system-level metrics (`<macro-output-file>`), an output path for the summary-level metrics (`<micro-output-file>`), the type of dataset reader (here, `reference-based`), and the input file(s) (`<input-file>`).
The input files will be passed to the dataset reader's `read` method (see `sacrerouge.data.datset_readers`).

The `ReferenceBasedDatasetReader` expects the input file to a `.jsonl` file (one serialized JSON object per line) where each JSON looks like the following:
```
{
    "instance_id": "2",        // the unique ID for the input document(s)
    "summarizer_id": "7",      // the unique ID for the system which produced this summary
    "summarizer_type": "peer"  // either "peer" or "reference,
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
Of course, you can write your own `DatasetReader` to load the data from whichever file format is most convenient.

Then, each command will also accept parameters that correspond to the parameters for the respective `Metric`'s constructor.
In the above example, `--max_ngram` and `--use_porter_stemmer` correspond to parameters for the `Rouge` constructor.

The system-level output file will contain a json-serialized `MetricsDict` object that represents the metric's value aggregated over all summaries.
The summary-level output file will contain one json-serialized `Metrics` that represents the metric's value for just that particular summary.
 
### Evaluating Metrics
The `score` and `correlate` commands are used to evaluate a metric by calculating its correlation to human judgments.

When evaluating metrics, it is often desirable to be able to compare how well the metric scores system-generated summaries and human-written summaries at the same time.
This procedure requires running jackknifing to ensure system and human summaries can be fairly compared.
The main differences between `evaluate` and `score` are that the `score` command will automatically run jackknifing if the metric requires and there is no system-level output (as many systems are typically being scored at the same time).

Like `evaluate`, the `score` command is automatically created for each `Metric`:
```bash
sacrerouge rouge score \
    <output-file>
    --dataset-reader reference-based \
    --input-files <input-file>+ \
    --max_ngram 2 \
    --use_porter_stemmer false
```
The `<output-file>` will contain one json-serialized `Metrics` object per line that represents the value of the metric for that input summary.
If jackknifing was performed, the metric name will have `_jk` appended to its name.
For instance, here is an example output for a single summary:
```json
{
  "instance_id": "242",
  "summarizer_id": "21",
  "summarizer_type": "peer",
  "metrics": {
    "rouge-1": {
      "precision": 0.3,
      "recall": 0.8,
      "f1": 0.44
    },
    "rouge-1_jk": {
      "precision": 0.5,
      "recall": 0.6,
      "f1": 0.55
    }
  }
}
``` 

After the scores have been calculated, the `correlate` command can be used to calculate several different correlation coefficients between two provided input metrics.
```bash
sacrerouge correlate \
    --metrics-jsonl-files <metrics-file>+ \
    --metrics <metric-name-1> <metric-name-2> \
    --summarizer-type {all, reference, peer} \
    --output-file <output-file>
``` 
The `<metrics-file>` parameters should all have one json-serialized `Metrics` object per line.
The `<output-file>` will have the correlation between the two input metrics calculated in three different ways:

- Summary-level: Calculates the average correlation across inputs
- System-level: Calculates the average metric value per system, then calculates the correlation of those values
- Global: Directly calculates the correlation between all values of the metrics

The `--summarizer-type` flag controls what types of summaries the correlation should be calculated over. 

## Developing a New Metric
SacreROUGE can be used to easily develop new evaluation metrics.
Once a metric is implemented within our framework, (1) it can immediately be evaluated using many different datasets without writing any boilerplate code and (2) it automatically gets `evaluate` and `score` commands generated for it.

All metrics in SacreROUGE must extend the `Metric` base class.
Additionally, these steps must be performed:
- Registering the metric
- Providing a list of required input fields
- Provide a jackknifing class (if necessary)
- Override the `score_multi_all` method.

Here is an example reference-based metric:
```python
# Register the metric so it can be referred to by this name. We extend `ReferenceBasedMetric` because it
# concretely defines the arguments for the different `score` methods, which can help some autocomplete libraries.
@Metric.register('my-metric')
class MyMetric(ReferenceBasedMetric):
    def __init__(self):
        # Provide a list of required input fields, specify which jackknifer should be used
        super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())

    # Override the `score_multi_all` method
    def score_multi_all(summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]
        output_metrics = []
        for summaries, references in zip(summaries_list, references_list):
            output_metrics.append([])
            for summary in summaries:
                value = some_scoring_function(summary, references)
                output_metrics[-1].append(MetricsDict({'my-metric': value}))
        return output_metrics
```
The required input fields, which are passed to the super constructor, will be passed to the scoring methods in the same order as they appear in the lists.
First, the `required_summary_fields` are fields specific to the summary, such as the summary itself or any extra data.
The second, `required_context_fields` are the fields which the summary is scored against, such as the reference documents.
The names in both lists correspond the keys in the `fields` data member of the `EvalInstance` class, which are populated via the dataset reader.

The jackknifer is responsible for taking the input fields and returning a new list of fields for evaluation.
The average metric's value across this new list will be equal to the jackknifed score (see `sacrerouge.data.jackknifers`)

Only the `score_multi_all` method is required to be overridden.
By default, the other methods (e.g., `score`, `score_all`) call `score_multi_all`.

After the above class has been defined, SacreROUGE will automatically generate commands
```bash
sacrerouge my-metric evaluate
sacrerouge my-metric score
```
and `MyMetric` is accessible via the Python interface.

## Setting up a Dataset
SacreROUGE also contains data to load some summarization datasets and save them in a common format.
Run the `sacrerouge setup-dataset` command to see the available datasets, or check [here](doc/datasets/datasets.md).

## Data Visualization
We have also written two data visualization tools.
The [first tool](https://danieldeutsch.github.io/pages/pyramid-visualization.html) visualizes a Pyramid and optional Pyramid annotations on peer summaries.
It accepts the `pyramid.jsonl` and `pyramid-annotations.jsonl` files which are saved by some of the dataset readers.

The [second tool](https://danieldeutsch.github.io/pages/rouge-visualization.html) visualizes the n-gram matches that are used to calculate the ROUGE score.
It accepts the `summaries.jsonl` files which are saved by some of the dataset readers.

## Citation
If you use SacreROUGE for your paper, please cite the following paper:
```
@inproceedings{deutsch-roth-2020-sacrerouge,
    title = "{S}acre{ROUGE}: An Open-Source Library for Using and Developing Summarization Evaluation Metrics",
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
