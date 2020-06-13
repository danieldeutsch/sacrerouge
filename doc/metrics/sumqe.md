# Sum-QE
Sum-QE [1] is a BERT-based model to estimate the linguistic quality of a summary.
Our implementation wraps [our fork](https://github.com/danieldeutsch/SumQE) of the [original code](https://github.com/nlpaueb/SumQE) which creates a more compatible command-line interface.
We additionally followed the steps in the repository to retrain their multi-task 5 models which we have saved on AWS:

- [Model trained on DUC 2005 and 2006](https://danieldeutsch.s3.amazonaws.com/sacrerouge/metrics/SumQE/models/multitask_5-duc2005_duc2006.npy)
- [Model trained on DUC 2005 and 2007](https://danieldeutsch.s3.amazonaws.com/sacrerouge/metrics/SumQE/models/multitask_5-duc2005_duc2007.npy)
- [Model trained on DUC 2006 and 2007](https://danieldeutsch.s3.amazonaws.com/sacrerouge/metrics/SumQE/models/multitask_5-duc2006_duc2007.npy)

## Setting Up
Sum-QE has many Python dependencies.
We recommend referencing the repository's instructions for creating the conda environment.
The path to the Python binary can be passed to the `SumQE` class.

The models can be set up with the following command:
```bash
sacrerouge setup-metric sumqe \
    --download-2005-2006-model \
    --download-2005-2007-model \
    --download-2006-2007-model
```
Each of the `--download` arguments is optional.

To verify your installation, run:
```bash
pytest sacrerouge/tests/metrics/sumqe_test.py
```
This requires setting the environment variable `SUMQE_PYTHON_BINARY` to the Python binary with the Sum-QE dependencies installed.

## References
[1] Stratos Xenouleas, Prodromos Malakasiotis, Marianna Apidianaki and Ion Androutsopoulos. [Sum-QE: a BERT-based Summary Quality Estimation Model](https://arxiv.org/abs/1909.00578). EMNLP 2019.