from repro.models.lin2004 import ROUGE

from sacrerouge.metrics import Metric
from sacrerouge.metrics.docker import ReferenceBasedDockerMetric


@Metric.register('docker-rouge')
class DockerRouge(ReferenceBasedDockerMetric):
    def __init__(
        self,
        image: str = "lin2004",
        ngram_order: int = 4,
        porter_stemmer: bool = True,
        remove_stopwords: bool = False,
        sentence_split: bool = True,
        calculate_su4: bool = True,
    ):
        metric = ROUGE(
            image=image,
            ngram_order=ngram_order,
            porter_stemmer=porter_stemmer,
            remove_stopwords=remove_stopwords,
            sentence_split=sentence_split,
            calculate_su4=calculate_su4,
        )
        super().__init__(metric)
