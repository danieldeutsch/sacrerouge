# BERTScore
This is a version of BERTScore which is implemented within a Docker image.
It is a light wrapper around the [Repro implementation](https://github.com/danieldeutsch/repro/tree/master/models/zhang2020).

The name of the metric is `docker-bertscore` and the class is `sacrerouge.metrics.docker.bertscore.DockerBertScore`.

## Setting Up
To run this metric, you must have the `zhang2020` Repro docker image built:
```shell script
repro setup zhang2020
```
Then, you can directly run the metric.

We used [this experiment](../../../experiments/docker/bertscore/run.sh) to verify that the Dockerized and non-Dockerized versions of the metric are identical. 