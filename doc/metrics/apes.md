# APES
APES [1] is a reference-based metric which evaluates summaries using a reading comprehension model.
The entities within the reference summary are removed, then a reading comprehension model tries to predict the removed entity from the candidate summary.
A score is calculated based on the number of correctly predicted entities.

Our implementation is a wrapper around the original code, which does not assume entities are already tagged.
The [preprocessing code is a fork](https://github.com/danieldeutsch/APES-on-TAC2011) of the [original repo](https://github.com/mataney/APES-on-TAC2011).
The reading [comprehension component is also a fork](https://github.com/danieldeutsch/rc-cnn-dailymail) of [this fork](https://github.com/theblackcat102/rc-cnn-dailymail) of the [original repo](https://github.com/mataney/rc-cnn-dailymail).

The name of the Python2.7 environment is required to run this metric.
See "Environment" below.

## Setup
To download the code and model dependencies, run
```
sacrerouge setup-metric apes
```

## Environment
The environment we used to run the APES code was created by creating a Python2.7 environment, then running:
```
pip install --upgrade https://github.com/Theano/Theano/archive/master.zip
pip install --upgrade https://github.com/Lasagne/Lasagne/archive/master.zip
pip install tqdm
python -m spacy download en
```
These commands were taken from [here](https://github.com/theblackcat102/rc-cnn-dailymail/blob/master/setup.sh).
See [here](../../environments/apes.yml) for the output of our `conda env export` command.
The name of your conda environment with this setup should be passed as the `environment_name` parameter to the `APES` constructor.

## References
[1]: Matan Eyal, Tal Baumel, and Michael Elhadad. [Question Answering as an Automatic Evaluation Metric for News Article Summarization](https://www.aclweb.org/anthology/N19-1395/). NAACL, 2019