# SIMetrix
SIMetrix [1, 2, 3] is a reference-free evaluation metric that compares a summary to the input documents.
Our implementation wraps [this fork](https://github.com/igorbrigadir/simetrix) of the original code.

## Setting Up
Running SIMetrix requires Java 1.7 and Maven to be installed.
Then run:
```bash
sacrerouge setup-metric simetrix
```

To verify your installation, run:
```bash
pytest sacrerouge/tests/metrics/simetrix_test.py
```

## References
[1] Annie Louis and Ani Nenkova. [Automatically Evaluating Content Selection in Summarization without Human Models](https://www.aclweb.org/anthology/D09-1032/). EMNLP 2009.

[2] Annie Louis and Ani Nenkova. [Predicting Summary Quality using Limited Human Input](https://tac.nist.gov/publications/2009/participant.papers/UPenn.proceedings.pdf). TAC 2009.

[3] Annie Louis and Ani Nenkova. [Summary Evaluation without Human Models](https://www.researchgate.net/profile/Annie_Louis/publication/228863482_Automatic_summary_evaluation_without_human_models/links/02bfe51085c035d6eb000000/Automatic-summary-evaluation-without-human-models.pdf). TAC 2008.