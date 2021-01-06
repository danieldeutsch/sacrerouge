# QAGS
QAGS [1] is a question-based automatic metric for evaluating the factual consistency of summaries.
Our implementation of QAGS uses [our fork](https://github.com/danieldeutsch/qags) of [the original code](https://github.com/W4ngatang/qags) which fixes some errors and makes the pipeline easier to run.

For some reason, the output scores appear to be non-deterministic (you may get different outputs on multiple runs for the same inputs).

## Setting Up
First, run the SacreROUGE setup command:
```
sacrerouge setup-metric qags
```
This will clone the Github repository and download the necessary pre-trained models.

The Python environment file we have successfully used to run the code is located [here](../../environments/qags.yml).
After you have installed those packages, you must do the following:
- Run `python -m spacy download en_core_web_lg`
- cd into the fairseq directory in the QAGS code (`~/.sacrerouge/metrics/QAGS/qags/fairseq`) and run `pip install --editable .`

## Correlations
The QAGS score implemented here achieves 0.35 and 0.08 correlation to the human judgments collected by [1] on the CNN/DailyMail and XSUM datasets respectively.
We currently do not know why these do not match the expected 0.55 and 0.17 as reported in the paper.

## References
[1] Alex Wang, Kyunghyun Cho, and Mike Lewis. [Asking and Answering Questions to Evaluate the Factual Consistency of Summaries](https://www.aclweb.org/anthology/2020.acl-main.450.pdf). ACL 2020.