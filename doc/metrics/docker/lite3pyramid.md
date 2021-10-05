# Lite3Pyramid
This is a version of Lite3Pyramid which is implemented within a Docker image.
It is a light wrapper around the [Repro implementation](https://github.com/danieldeutsch/repro/tree/master/models/zhang2021).

The name of the metric is `docker-lite3pyramid` and the class is `sacrerouge.metrics.docker.lite3pyramid.DockerLite3Pyramid`.

## Setting Up
To run this metric, you must have the `zhang2021` Repro docker image built:
```shell script
repro setup zhang2021
```
Then, you can directly run the metric.