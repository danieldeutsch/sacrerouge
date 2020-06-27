# Chaganty 2018
This dataset contains quality judgments for several different summarization systems on the CNN/DailyMail dataset.
The data was published in [The price of debiasing automatic metrics in natural language evaluation](https://www.aclweb.org/anthology/P18-1060.pdf).

```bash
sacrerouge setup-dataset chaganty2018 \
    <output-dir>
```

The output files are the following:
- `documents.jsonl`: The CNN/DailyMail documents
- `summaries.jsonl`: The system summaries
- `metrics.jsonl`: The corresponding manual evaluation metrics for the system summaries

## Notes
006588 appears twice for ml+rl.