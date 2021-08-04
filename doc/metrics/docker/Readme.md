# Dockerized Metrics
One of the original goals of SacreROUGE was to provide standard implementations around evaluation metrics that were easy to run.
Thus far, we have worked towards that by implementing Python wrappers around various libraries so that they all share the same interface and providing setup commands to download and install all of the necessary dependenices.
Now we are exploring taking that a step further and implementing metrics within [Docker containers](https://www.docker.com/).

Docker containers are a powerful tool for improving reproducibility because they enable developers to have complete control over the environment that the code runs on.
The metric code, pretrained models, and specific Python versions and dependencies can all be isolated to the container, so all you have to do is build the container.
Because Docker is able to handle all of these dependencies, as long as you have a working Docker installation, you should be able to run any Dockerized metric without any additional effort!

Our Dockerized metrics are wrappers around their implementations in [Repro](https://github.com/danieldeutsch/repro).
We recommend following [their guide for installing Docker](https://github.com/danieldeutsch/repro/blob/master/tutorials/docker.md).

Instead of running `sacrerouge setup-metric` for each metric you want to run, you now need to build the corresponding metric's Docker container with a `repro setup` command.
Once that is complete, you can directly run the Dockerized metric.

This directory contains the documentation for the Dockerized metrics, including the commands to build their Docker containers.