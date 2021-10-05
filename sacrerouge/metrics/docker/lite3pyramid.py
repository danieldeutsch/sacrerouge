from repro.models.zhang2021 import Lite3Pyramid, DEFAULT_IMAGE

from sacrerouge.metrics import Metric
from sacrerouge.metrics.docker import ReferenceBasedDockerMetric


@Metric.register('docker-lite3pyramid')
class DockerLite3Pyramid(ReferenceBasedDockerMetric):
    def __init__(
        self,
        image: str = DEFAULT_IMAGE,
        model: str = None,
        device: int = 0,
    ):
        metric = Lite3Pyramid(
            image=image,
            model=model,
            device=device,
        )
        super().__init__(metric)
