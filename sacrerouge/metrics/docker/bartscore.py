from repro.models.yuan2021 import BARTScore, DEFAULT_IMAGE

from sacrerouge.metrics import Metric
from sacrerouge.metrics.docker import ReferenceBasedDockerMetric


@Metric.register('docker-bartscore')
class DockerBARTScore(ReferenceBasedDockerMetric):
    def __init__(
        self,
        image: str = DEFAULT_IMAGE,
        model: str = "default",
        device: int = 0,
    ):
        metric = BARTScore(
            image=image,
            model=model,
            device=device,
        )
        super().__init__(metric)
