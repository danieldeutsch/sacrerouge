import argparse
from overrides import overrides
from typing import List, Union

from sacrerouge.commands import MetricSetupSubcommand
from sacrerouge.data import MetricsDict
from sacrerouge.data.types import DocumentType, SummaryType
from sacrerouge.metrics import DocumentBasedMetric, Metric


try:
    from blanc import BlancHelp, BlancTune
except ImportError:
    BLANC_INSTALLED = False

    class Blanc(DocumentBasedMetric):
        def __init__(self, *args, **kwargs):
            pass

        def score_multi_all(self, *args, **kwargs):
            raise NotImplementedError('Please install the "blanc" python library library to use Blanc')
else:
    BLANC_INSTALLED = True

    import torch

    @Metric.register('blanc')
    class Blanc(DocumentBasedMetric):
        def __init__(self,
                     blanc_type: str = 'blanc_help',
                     device: str = 'cuda',
                     random_seed: int = 1,
                     **kwargs) -> None:
            super().__init__()
            self.name = blanc_type

            if blanc_type == 'blanc_tune':
                self.blanc = BlancTune(device=device, random_seed=random_seed, **kwargs)
            elif blanc_type == 'blanc_help':
                self.blanc = BlancHelp(device=device, **kwargs)
            else:
                raise Exception(f'Unknown BLANC type: {blanc_type}')

        def _flatten(self, text: Union[DocumentType, SummaryType]) -> str:
            if isinstance(text, list):
                return ' '.join(text)
            return text

        def score_multi_all(self,
                            summaries_list: List[List[SummaryType]],
                            documents_list: List[List[DocumentType]]) -> List[List[MetricsDict]]:
            # For now, the implementation of the BLANC library looks like it only allows for single-document summaries
            documents = []
            for docs in documents_list:
                assert len(docs) == 1, 'BLANC only supports evaluating single-document summaries'
                documents.append(self._flatten(docs[0]))

            summaries_list = [[self._flatten(summary) for summary in summaries] for summaries in summaries_list]

            scores_list = self.blanc.eval_summaries_for_docs(documents, summaries_list)
            metrics_lists = []
            for scores in scores_list:
                metrics_lists.append([])
                for score in scores:
                    metrics_lists[-1].append(MetricsDict({self.name: score}))
            return metrics_lists


@MetricSetupSubcommand.register('blanc')
class BlancSetupSubcommand(MetricSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the BLANC metric'
        self.parser = parser.add_parser('blanc', description=description, help=description)
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        try:
            import blanc
            print('BLANC setup success')
        except ImportError:
            print('Please pip install "blanc" to complete setup')
