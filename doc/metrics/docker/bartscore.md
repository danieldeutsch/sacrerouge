# BARTScore
This is a version of BARTScore which is implemented within a Docker image.
It is a light wrapper around the [Repro implementation](https://github.com/danieldeutsch/repro/tree/master/models/yuan2021).

The name of the metric is `docker-bartscore` and the class is `sacrerouge.metrics.docker.bartscore.DockerBARTScore`.

## Setting Up
To run this metric, you must have the `yuan2021` Repro docker image built:
```shell script
repro setup yuan2021
```
Then, you can directly run the metric.