# Vasilyev 2020
This dataset includes human annotations collected for CNN/DailyMail summaries and summaries for news articles provided by the BLANC paper [1].
For the CNN/DailyMail dataset, there are 555 judged summaries with a `generic_quality` score.
For the DailyNews dataset, there are 300 with `generic_quality`, `fluent`, `understandable`, `informative`, `compact`, and `overall` scores.

The original dataset does not mark the instance or summarizer IDs, so we had to try and infer them.
The instance ID is inferred based on the document text.
That is, identical input documents will have identical instance IDs.
Since it is not possible to identify which model produced each summary, all of the instances are given a unique summarizer ID.

For the DailyNews dataset, there are two files of annotations.
The first contains a generic quality score and the second contains more fine-grained judgments.
The two files should be for the same set of summaries, but we were unable to match them.
Instead, we treated the files independently.
That is, instance or summarizer IDs across the files should not be compared.

## Setup
```
sacrerouge setup-dataset vasilyev2020 <output-dir>
```

## References
[1] Oleg Vasilyev, Vedant Dharnidharka, John Bohannon. [Fill in the BLANC: Human-free quality estimation of document summaries](https://www.aclweb.org/anthology/2020.eval4nlp-1.2/). Eval4NLP, 2020.