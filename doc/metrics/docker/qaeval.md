# QAEval
This is a version of QAEval which is implemented within a Docker image.
It is a light wrapper around the [Repro implementation](https://github.com/danieldeutsch/repro/tree/master/models/deutsch2021).

The name of the metric is `docker-qa-eval` and the class is `sacrerouge.metrics.docker.qaeval.DockerQAEval`.

## Setting Up
To run this metric, you must have the `deutsch2021` Repro docker image built:
```shell script
repro setup deutsch2021
```
Then, you can directly run the metric.

We used [this experiment](../../../experiments/docker/qaeval/run.sh) to verify that the Dockerized and non-Dockerized versions of the metric are identical. 