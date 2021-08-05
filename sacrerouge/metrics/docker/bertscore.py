from repro.models.zhang2020 import BERTScore

from sacrerouge.metrics import Metric
from sacrerouge.metrics.docker import ReferenceBasedDockerMetric


@Metric.register('docker-bertscore')
class DockerBertScore(ReferenceBasedDockerMetric):
    def __init__(
        self,
        image: str = "zhang2020",
        model: str = None,
        device: int = 0,
        batch_size: int = 64,
        language: str = "en",
    ):
        metric = BERTScore(
            image=image,
            model=model,
            device=device,
            batch_size=batch_size,
            language=language,
        )
        super().__init__(metric)
