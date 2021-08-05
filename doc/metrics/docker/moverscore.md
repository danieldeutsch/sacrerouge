# MoverScore
This is a version of MoverScore which is implemented within a Docker image.
It is a light wrapper around the [Repro implementation](https://github.com/danieldeutsch/repro/tree/master/models/zhao2019) of `MoverScoreForSummarization`.

The name of the metric is `docker-moverscore` and the class is `sacrerouge.metrics.docker.zhao2019.DockerMoverScore`.

## Setting Up
To run this metric, you must have the `zhao2019` Repro docker image built:
```shell script
repro setup zhao2019
```
Then, you can directly run the metric.

We used [this experiment](../../../experiments/docker/moverscore/run.sh) to verify that the Dockerized and non-Dockerized versions of the metric have similar correlations to ground-truth judgments.
For some reason, the scores of the two versions are not the same, but their overall correlations are similar.
 