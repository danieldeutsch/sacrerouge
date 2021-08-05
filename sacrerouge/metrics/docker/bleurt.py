from repro.models.sellam2020 import BLEURT

from sacrerouge.metrics import Metric
from sacrerouge.metrics.docker import ReferenceBasedDockerMetric


@Metric.register('docker-bleurt')
class DockerBluert(ReferenceBasedDockerMetric):
    def __init__(
        self,
        image: str = "sellam2020",
        model: str = "bleurt-base-128",
        device: int = 0,
        batch_size: int = 16,
    ):
        metric = BLEURT(
            image=image,
            model=model,
            device=device,
            batch_size=batch_size,
        )
        super().__init__(metric)
