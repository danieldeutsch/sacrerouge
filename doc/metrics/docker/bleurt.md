# BLEURT
This is a version of BLEURT which is implemented within a Docker image.
It is a light wrapper around the [Repro implementation](https://github.com/danieldeutsch/repro/tree/master/models/sellam2020).

The name of the metric is `docker-bleurt` and the class is `sacrerouge.metrics.docker.bleurt.DockerBluert`.

## Setting Up
To run this metric, you must have the `sellam2020` Repro docker image built:
```shell script
repro setup sellam2020
```
Then, you can directly run the metric.

We used [this experiment](../../../experiments/docker/bleurt/run.sh) to verify that the Dockerized and non-Dockerized versions of the metric are identical. 