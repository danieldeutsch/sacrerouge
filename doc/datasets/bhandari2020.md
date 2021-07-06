# Bhandari 2020
This dataset contains the Lightweight Pyramid annotations for the CNN/DailyMail dataset collected in [1].
It contains judgments for 100 summaries across 25 systems.
However, there is an error with the BART system in the [official repository](https://github.com/neulab/REALSumm).
BART is included in both the extractive and abstractive system.
The files for both of them have different summaries.
The key "bart_out" is included in both of the corresponding extractive and abstractive judgment files, however, both have the extractive summaries judged, but they have different scores.
Our setup script includes the "bart_out" summaries in the extractive models and their corresponding scores only, making the total number of systems 24 instead of 25. 
See [this issue](https://github.com/neulab/REALSumm/issues/3).

```bash
sacrerouge setup-dataset bhandari2020 <output-dir>
```

The output files are the following:
    - `summaries-{abs, ext, mix}.jsonl`: The judged summaries with their references and input documents.
    The references and inputs are specific to the individual system since there may have been differences in tokenization, etc.
    `abs` contains the abstractive systems, `ext` the extractive, and `mix` both.
    - `metrics-{abs, ext, mix}.jsonl`: The metrics for the corresponding summaries in the `summaries-*.jsonl` files.
    - `all-summaries-{abs, ext, mix}.jsonl.gz`: All of the model outputs with their corresponding input documents and references.
    The instance IDs do *not* match with those in `summaries-*.jsonl`.
    Some summaries are missing because the summaries could not be aligned (see the original Github repo for more details).
    We found 11,314 out of 11,490 summaries had outputs from all 24 models.
    This file groups all of the model outputs by their line numbers, which appears to be correct based on examining a few examples. 
    
## References
[1] Manik Bhandari, Pranav Narayan Gour, Atabak Ashfaq, Pengfei Liu, and Graham Neubig. Re-evaluating Evaluation in Text Summarization. EMNLP, 2020.