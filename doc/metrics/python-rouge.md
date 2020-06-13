# Python ROUGE
Python ROUGE is a Python-based implementation of ROUGE [1].
The original ROUGE is written in Perl and requires writing all of the summaries to disk and does a lot of intermediate I/O which makes it quite slow.
The Python version is significantly faster.

The Python version currently supports ROUGE-N and ROUGE-L.
Although, it is near-identical to the Perl version, it should only be used for development and not official evaluation, for which you should use the original [ROUGE](rouge.md).

## Setting Up
This metric only requires that ROUGE has been set up (see [here](rouge.md)).

To verify your installation, run:
```bash
pytest sacrerouge/tests/metrics/python_rouge_test.py
```

## References
[1] Chin-Yew Lin. [ROUGE: A Package for Automatic Evaluation of Summaries](https://www.aclweb.org/anthology/W04-1013/). 2004.