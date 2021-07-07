# FEQA
FEQA [1] is a question-answering based metric for evaluating the faithfulness of summaries.
Our implementation uses our [fork](https://github.com/danieldeutsch/feqa) of the [original repository](https://github.com/esdurmus/feqa) which adds a `run.py` file to easily run FEQA using an input and output file.

## Setting Up
First, create an environment for FEQA to run (see [here](../../environments/feqa.yml)).
We had to manually install the Cython and numpy packages before installing the other requirements because benepar requires Cython and numpy to be installed first.

After the environment is created, install the spacy model and other resources:
```
python -m spacy download en_core_web_sm
python
>>> import benepar
>>> import nltk
>>> benepar.download('benepar_en2')
>>> nltk.download('stopwords')
```

Then, setup the metric by cloning the repository and downloading the necessary pre-trained models:
```
sacrerouge setup-metric feqa
```

## Correlations
This implementation achieves near 0.0 Pearson correlations to the data collected by [2] on the CNN/DailyMail and XSUM splits, respectively.
I am not sure why yet.
The data from [1] has not been released yet to reproduce the results from the paper.

## References
[1] Esin Durmus, He He and Mona Diab. [FEQA: A Question Answering Evaluation Framework for Faithfulness Assessment in Abstractive Summarization](https://www.aclweb.org/anthology/2020.acl-main.454/). ACL 2020.
[2] Alex Wang, Kyunghyun Cho, and Mike Lewis. [Asking and Answering Questions to Evaluate the Factual Consistency of Summaries](https://www.aclweb.org/anthology/2020.acl-main.450.pdf). ACL 2020.