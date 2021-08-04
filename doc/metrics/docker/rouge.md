# ROUGE
This is a version of ROUGE which is implemented within a Docker image.
It is a light wrapper around the [Repro implementation](https://github.com/danieldeutsch/repro/tree/master/models/lin2004).

The name of the metric is `docker-rouge` and the class is `sacrerouge.metrics.docker.rouge.DockerRouge`.

## Setting Up
To run this metric, you must have the `lin2004` Repro docker image built:
```shell script
repro setup lin2004
```
Then, you can directly run the metric.

We used [this experiment](../../../experiments/docker/rouge/run.sh) to verify that the Dockerized and non-Dockerized versions of the metric are identical.