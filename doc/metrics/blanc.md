# BLANC
BLANC [1] is a document-based evaluation metric.
It currently only supports single-document summaries.
Our implementation is a wrapper around the [original library](https://github.com/PrimerAI/blanc).
The name for this metric is `blanc`.

## Setting Up
Install the `blanc` pip package:
```
pip install blanc
```
Then we manually installed `transformers==2.5.1` based on the instructions on the Github repo.
The default transformers version which was installed did not work.

Currently, the unit tests do not produce the scores reported in the official Github repository, but I think it might be related to the random seed which is not set in the constructor of the class but in their main function.

## Correlations
Here are the correlations of BLANC to the expert-based relevance judgments from [Fabbri (2020)](https://arxiv.org/abs/2007.12626).

## References
Oleg Vasilyev, Vedant Dharnidharka, John Bohannon. [Fill in the BLANC: Human-free quality estimation of document summaries](https://www.aclweb.org/anthology/2020.eval4nlp-1.2/). Eval4NLP, 2020.