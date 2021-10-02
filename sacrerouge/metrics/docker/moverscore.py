from repro.models.zhao2019 import DEFAULT_IMAGE, MoverScoreForSummarization

from sacrerouge.metrics import Metric
from sacrerouge.metrics.docker import ReferenceBasedDockerMetric


@Metric.register('docker-moverscore')
class DockerMoverScore(ReferenceBasedDockerMetric):
    def __init__(
        self,
        image: str = DEFAULT_IMAGE,
        device: int = 0,
    ):
        metric = MoverScoreForSummarization(
            image=image,
            device=device,
        )
        super().__init__(metric)
