import argparse
import logging
import os
import shutil
from glob import glob
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT
from sacrerouge.data import MetricsDict
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric

logger = logging.getLogger(__name__)


@Metric.register('pyreval')
class PyrEval(ReferenceBasedMetric):
    def __init__(self,
                 environment_name: str = None,
                 pyreval_root: str = f'{DATA_ROOT}/metrics/PyrEval',
                 verbose: bool = False):
        super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())
        self.environment_name = environment_name
        self.pyreval_root = pyreval_root
        self.verbose = verbose

    def _clean_directories(self):
        # The PyrEval code runs all of its processing in place, so we need to clean up all of its
        # directories in case there is something left over from an old run, which might cause a problem
        # for the next run.
        #
        # This code is based on the clean function in "pyreval.py". The original code will crash if one of
        # the directories it searches for does not exist, so we reimplemented it here.

        # Clean the raw data (not included in the original code)
        for file_path in glob(f'{self.pyreval_root}/Raw/peers/*'):
            if os.path.isfile(file_path):
                os.remove(file_path)
        for file_path in glob(f'{self.pyreval_root}/Raw/model/*'):
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Clean the sentence splits
        for file_path in glob(f'{self.pyreval_root}/Raw/peers/split/*'):
            os.remove(file_path)
        for file_path in glob(f'{self.pyreval_root}/Raw/model/split/*'):
            os.remove(file_path)

        # Clean the preprocessed folder, first the files, then the folders
        for file_path in glob(f'{self.pyreval_root}/Preprocess/peer_summaries/*.xml'):
            os.remove(file_path)
        for dir_path in glob(f'{self.pyreval_root}/Preprocess/peer_summaries/*'):
            shutil.rmtree(dir_path)

        for file_path in glob(f'{self.pyreval_root}/Preprocess/wise_crowd_summaries/*.xml'):
            os.remove(file_path)
        for dir_path in glob(f'{self.pyreval_root}/Preprocess/wise_crowd_summaries/*'):
            shutil.rmtree(dir_path)

        # Pyramid scores
        scores_file = f'{self.pyreval_root}/Pyramid/scores.txt'
        if os.path.exists(scores_file):
            os.remove(scores_file)

        # Pyramids
        for file_path in glob(f'{self.pyreval_root}/Scoring/pyrs/pyramids/*.pyr'):
            os.remove(file_path)

        # SCUs
        for file_path in glob(f'{self.pyreval_root}/Scoring/scu/*.pyr'):
            os.remove(file_path)

        # Sizes
        for file_path in glob(f'{self.pyreval_root}/Scoring/sizes/*.size'):
            os.remove(file_path)

        # Temp
        for file_path in glob(f'{self.pyreval_root}/Scoring/temp/*'):
            os.remove(file_path)

        # The results file
        results_file = f'{self.pyreval_root}/results.csv'
        if os.path.exists(results_file):
            os.remove(results_file)

    def _flatten_summaries(self, summaries: List[SummaryType]):
        flat = []
        for summary in summaries:
            if isinstance(summary, list):
                flat.append(' '.join(summary))
            else:
                flat.append(summary)
        return flat

    def _save_summary(self, summary: str, file_path: str) -> None:
        dirname = os.path.dirname(file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(file_path, 'w') as out:
            out.write(summary)

    def _parse_results(self) -> List[MetricsDict]:
        results_path = f'{self.pyreval_root}/results.csv'
        if not os.path.exists(results_path):
            raise Exception(f'PyrEval results file does not exist: "{results_path}"')

        # First line is the name of the pyramid
        # Second line is the header
        lines = open(results_path, 'r').read().splitlines()
        metrics_dict = {}
        for line in lines[2:]:
            index, raw, quality, coverage, comprehensive = line.split(',')
            metrics_dict[int(index)] = MetricsDict({
                'pyreval': {
                    'raw': int(raw),
                    'quality': float(quality),
                    'coverage': float(coverage),
                    'comprehensive': float(comprehensive),
                }
            })

        metrics_list = []
        for index in sorted(metrics_dict.keys()):
            metrics_list.append(metrics_dict[index])
        return metrics_list

    def score_multi(self, summaries: List[SummaryType], references: List[ReferenceType]) -> List[MetricsDict]:
        # Clean before starting, just in case it's dirty
        self._clean_directories()

        summaries = self._flatten_summaries(summaries)
        references = self._flatten_summaries(references)

        # Write the summaries to the Raw directory
        for i, summary in enumerate(summaries):
            self._save_summary(summary, f'{self.pyreval_root}/Raw/peers/{i}')
        for i, summary in enumerate(sorted(references)):
            self._save_summary(summary, f'{self.pyreval_root}/Raw/model/{i}')

        # Run the whole pipeline by piping '0 -t' to the pyreval script. '0' means run the pipeline end-to-end.
        # '-t' means to save the scores to a file
        commands = [f'cd {self.pyreval_root}']
        if self.environment_name is not None:
            commands.append(f'source activate {self.environment_name}')
        commands.append(f'echo "0 -t" | python2.7 pyreval.py')
        command = ' && '.join(commands)

        logger.info(f'Running PyrEval command: "{command}"')
        redirect = None if self.verbose else PIPE
        process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
        process.communicate()

        metrics_list = self._parse_results()

        # Clean for the next run
        self._clean_directories()

        return metrics_list

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        # The original code can only do one pyramid at a time, so we can't process all of the inputs at once
        metrics_dict_lists = []
        for summaries, references in zip(summaries_list, references_list):
            metrics_dict_lists.append(self.score_multi(summaries, references))
        return metrics_dict_lists


class PyrEvalSetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the PyrEval metric'
        self.parser = parser.add_parser('pyreval', description=description, help=description)
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        commands = [
            f'mkdir -p {DATA_ROOT}/metrics',
            f'cd {DATA_ROOT}/metrics',
            f'git clone https://github.com/serenayj/PyrEval',
            f'cd PyrEval',
            f'wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip',
            f'unzip stanford-corenlp-full-2018-10-05.zip',
            f'mv stanford-corenlp-full-2018-10-05/* Stanford/',
            f'rm stanford-corenlp-full-2018-10-05.zip'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()

        if process.returncode == 0:
            print('PyrEval setup success')
        else:
            print('PyrEval setup failure')
