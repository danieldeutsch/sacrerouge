import argparse
import logging
import os
import shutil
import zipfile
from overrides import overrides
from packaging import version
from typing import List

from sacrerouge.commands import MetricSetupSubcommand
from sacrerouge.common import DATA_ROOT
from sacrerouge.common.util import download_file_from_google_drive
from sacrerouge.data import MetricsDict
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric

MIN_QAEVAL_VERSION = '0.1.0'
QAEVAL_INSTALLED = False

logger = logging.getLogger(__name__)

try:
    import qaeval
    installed_version = version.parse(qaeval.__version__)
    if installed_version < version.parse(MIN_QAEVAL_VERSION):
        raise ImportError(f'"qaeval" version out of date. Minimum required: {MIN_QAEVAL_VERSION}')

except ImportError:
    @Metric.register('qa-eval')
    class QAEval(ReferenceBasedMetric):
        def __init__(self) -> None:
            super().__init__()

        def score_multi_all(self,
                            summaries_list: List[List[SummaryType]],
                            references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
            raise Exception(
                f'Package "qaeval" could not be imported. Please install "qaeval" before running the metric. '
                f'The minimum required version is {MIN_QAEVAL_VERSION}')
else:
    from qaeval import QAEval as _QAEval
    from qaeval.answer_selection import NP_CHUNKS_STRATEGY

    QAEVAL_INSTALLED = True

    @Metric.register('qa-eval')
    class QAEval(ReferenceBasedMetric):
        def __init__(self,
                     answer_selection_strategy: str = NP_CHUNKS_STRATEGY,
                     generation_model_path: str = f'{DATA_ROOT}/metrics/qaeval/models/generation/model.tar.gz',
                     answering_model_dir: str = f'{DATA_ROOT}/metrics/qaeval/models/answering/model',
                     cuda_device: int = 0,
                     generation_batch_size: int = 8,
                     answering_batch_size: int = 8,
                     use_lerc: bool = False,
                     lerc_model_path: str = f'{DATA_ROOT}/metrics/qaeval/models/lerc/model.tar.gz',
                     lerc_pretrained_model_path: str = f'{DATA_ROOT}/metrics/qaeval/models/lerc/pretrained.tar.gz',
                     lerc_batch_size: int = 8,
                     verbose: bool = False) -> None:
            super().__init__()
            self.metric = _QAEval(
                generation_model_path=generation_model_path,
                answering_model_dir=answering_model_dir,
                answer_selection_strategy=answer_selection_strategy,
                cuda_device=cuda_device,
                generation_batch_size=generation_batch_size,
                answering_batch_size=answering_batch_size,
                use_lerc=use_lerc,
                lerc_model_path=lerc_model_path,
                lerc_pretrained_model_path=lerc_pretrained_model_path,
                lerc_batch_size=lerc_batch_size,
                verbose=verbose,
            )

        def score_multi_all(self,
                            summaries_list: List[List[SummaryType]],
                            references_list: List[List[ReferenceType]],
                            return_qa_pairs: bool = False) -> List[List[MetricsDict]]:
            # The QAEval library doesn't accept grouped summaries
            ungrouped_summaries = []
            ungrouped_references_list = []
            for summaries, references in zip(summaries_list, references_list):
                for summary in summaries:
                    ungrouped_summaries.append(summary)
                    ungrouped_references_list.append(references)

            ungrouped_metrics = self.metric.score_batch(ungrouped_summaries, ungrouped_references_list, return_qa_pairs=return_qa_pairs)

            # Re-group
            metrics_lists = []
            index = 0
            for summaries in summaries_list:
                metrics_lists.append([])
                for _ in summaries:
                    if return_qa_pairs:
                        metrics, qa_pairs = ungrouped_metrics[index]
                        metrics = MetricsDict(metrics)
                        metrics_lists[-1].append((metrics, qa_pairs))
                    else:
                        metrics = MetricsDict(ungrouped_metrics[index])
                        metrics_lists[-1].append(metrics)
                    index += 1

            return metrics_lists


@MetricSetupSubcommand.register('qa-eval')
class QAEvalSetupSubcommand(MetricSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the QAEval metric'
        self.parser = parser.add_parser('qa-eval', description=description, help=description)
        self.parser.add_argument('--force', action='store_true', help='Forces redownloading the models')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        print('This setup command will download the necessary model files. It will not install "qaeval". You must "pip install qaeval" on your own.')

        generation_model_id = '1vVhRgLtsQDAOmxYhY5PMPnxxHUyCOdQU'
        generation_model_path = f'{DATA_ROOT}/metrics/qaeval/models/generation/model.tar.gz'
        if args.force and os.path.exists(generation_model_path):
            os.remove(generation_model_path)
        if not os.path.exists(generation_model_path):
            download_file_from_google_drive(generation_model_id, generation_model_path)
        else:
            print('Skipping downloading generation model')

        answering_model_id = '1q2Z3FPP9AYNz0RJKHMlaweNhmLQoyPA8'
        answering_model_zip_path = f'{DATA_ROOT}/metrics/qaeval/models/answering/model.zip'
        answering_model_path = f'{DATA_ROOT}/metrics/qaeval/models/answering/model'
        if args.force:
            if os.path.exists(answering_model_zip_path):
                os.remove(answering_model_zip_path)
            if os.path.exists(answering_model_path):
                shutil.rmtree(answering_model_path)

        if not os.path.exists(answering_model_zip_path):
            download_file_from_google_drive(answering_model_id, answering_model_zip_path)
        else:
            print('Skipping downloading answering model')
        if not os.path.exists(answering_model_path):
            print('Unzipping answering model')
            with zipfile.ZipFile(answering_model_zip_path) as zip:
                zip.extractall(answering_model_path)
        if os.path.exists(answering_model_zip_path):
            os.remove(answering_model_zip_path)

        lerc_model_id = '193K7v6pjOtuXdlMenQW-RzF6ft-xY2qd'
        lerc_model_path = f'{DATA_ROOT}/metrics/qaeval/models/lerc/model.tar.gz'
        if args.force and os.path.exists(lerc_model_path):
            os.remove(lerc_model_path)
        if not os.path.exists(lerc_model_path):
            download_file_from_google_drive(lerc_model_id, lerc_model_path)
        else:
            print('Skipping downloading LERC model')

        lerc_pretrained_model_id = '1fWBahDT-O1mpsbND300cuZuF73mfObzH'
        lerc_pretrained_model_path = f'{DATA_ROOT}/metrics/qaeval/models/lerc/pretrained.tar.gz'
        if args.force and os.path.exists(lerc_pretrained_model_path):
            os.remove(lerc_pretrained_model_path)
        if not os.path.exists(lerc_pretrained_model_path):
            download_file_from_google_drive(lerc_pretrained_model_id, lerc_pretrained_model_path)
        else:
            print('Skipping downloading LERC pretrained model')

        print('Downloading models complete')
