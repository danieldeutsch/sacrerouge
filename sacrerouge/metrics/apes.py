import argparse
import json
import logging
import os
import string
from overrides import overrides
from subprocess import Popen, PIPE
from typing import Dict, List, Tuple

from sacrerouge.commands import MetricSetupSubcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.data import MetricsDict
from sacrerouge.data.types import ReferenceType
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import SummaryType
from sacrerouge.io import JsonlReader
from sacrerouge.metrics import Metric, ReferenceBasedMetric

logger = logging.getLogger(__name__)


@Metric.register('apes')
class APES(ReferenceBasedMetric):
    def __init__(self,
                 environment_name: str = 'apes',
                 apes_root: str = f'{DATA_ROOT}/metrics/apes',
                 verbose: bool = False):
        super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())
        self.environment_name = environment_name
        if 'CONDA_INIT' not in os.environ:
            raise Exception('Environment variable "CONDA_INIT" must be set to the path to "conda.sh" since APES uses conda '
                            'to run the Python2.7 code.')

        self.apes_root = apes_root
        if not os.path.exists(self.apes_root):
            raise Exception(f'Path "{self.apes_root}" does not exist. Have you setup the metric?')

        self.verbose = verbose

    def _save_summaries(self,
                        output_file: str,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> Dict[Tuple[int, int], str]:
        # The code requires the summaries have filenames which match the TAC format, so we artificially create filenames
        # accordingly. Reference summaries are capital letters, and the code requires they can only be A-H. It should
        # not matter that we might have duplicate references (due to jackknifing) since they will be given different
        # instance ids here.
        indices_to_filename = {}
        output_data = {}

        logger.info(f'Writing summaries to {output_file}')
        for i, (summaries, references) in enumerate(zip(summaries_list, references_list)):
            # Must be "DXXXX-A"
            instance_id = f'D{i:04}-A'
            output_data[instance_id] = {'man': {}, 'machine': {}}

            for j, summary in enumerate(summaries):
                # Peers must end with a number
                filename = f'{instance_id}.M.100.A.{j}'
                indices_to_filename[(i, j)] = filename
                if isinstance(summary, list):
                    text = ' '.join(summary)
                else:
                    text = summary
                output_data[instance_id]['machine'][filename] = text

            # References must end with a letter
            assert len(references) <= 8
            for j, reference in enumerate(references):
                letter = string.ascii_uppercase[j]
                filename = f'{instance_id}.M.100.A.{letter}'
                if isinstance(reference, list):
                    text = ' '.join(reference)
                else:
                    text = reference
                output_data[instance_id]['man'][filename] = text

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as out:
            out.write(json.dumps(output_data))

        return indices_to_filename

    def _run_preprocess(self, input_file: str, output_file: str, metadata_file: str) -> Dict:
        logger.info('Running preprocessing')
        commands = [f'cd {self.apes_root}/APES-on-TAC2011']
        commands.append(f'source {os.environ["CONDA_INIT"]}')
        commands.append(f'conda activate {self.environment_name}')
        commands.append(f'python2.7 apes_on_tac2011.py --mode preprocess --input_file {input_file} --output_file {output_file} --metadata_file {metadata_file}')
        command = ' && '.join(commands)

        logger.info(f'Running command: "{command}"')
        redirect = None if self.verbose else PIPE
        process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
        process.communicate()

        metadata = json.load(open(metadata_file, 'r'))
        print(json.dumps(metadata, indent=2))
        return metadata

    def _run_answer_questions(self, input_file: str, output_file: str) -> Dict[str, List[float]]:
        logger.info('Running answering questions')
        commands = [f'cd {self.apes_root}/rc-cnn-dailymail']
        commands.append(f'source {os.environ["CONDA_INIT"]}')
        commands.append(f'conda activate {self.environment_name}')
        commands.append(f'python2.7 code/run_qa_model.py --input_file {input_file} --output_file {output_file} --train_path cnn_training.txt --dev_path cnn_test.txt --glove_path glove.6B.100d.txt')
        command = ' && '.join(commands)

        logger.info(f'Running command: "{command}"')
        redirect = None if self.verbose else PIPE
        process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
        process.communicate()

        filename_to_scores = {}
        with JsonlReader(output_file) as f:
            for data in f:
                answering_doc = data['answering_doc']
                score = data['reward']
                if answering_doc not in filename_to_scores:
                    filename_to_scores[answering_doc] = []
                filename_to_scores[answering_doc].append(score)
        return filename_to_scores

    def _get_metrics(self,
                     summaries_list: List[List[SummaryType]],
                     references_list: List[List[ReferenceType]],
                     indices_to_filename: Dict[Tuple[int, int], str],
                     filename_to_scores: Dict[str, List[float]],
                     metadata: Dict) -> List[List[MetricsDict]]:
        metrics_lists = []
        for i, (summaries, references) in enumerate(zip(summaries_list, references_list)):
            metrics_lists.append([])
            for j, summary in enumerate(summaries):
                filename = indices_to_filename[(i, j)]
                if filename not in filename_to_scores:
                    scores = [0]
                else:
                    scores = filename_to_scores[filename]
                # assert len(scores) == len(references)
                metrics_lists[-1].append(MetricsDict({'APES': sum(scores) / len(scores)}))
        return metrics_lists

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        # The APES code expects the input and output to be directories relative to the repo root, so we clear
        # those directories to be sure there is no contamination across runs
        with TemporaryDirectory() as temp_dir:
            temp_dir = os.path.abspath(temp_dir)

            summaries_file = f'{temp_dir}/summaries.json'
            questions_file = f'{temp_dir}/questions.jsonl'
            metadata_file = f'{temp_dir}/metadata.json'
            answers_file = f'{temp_dir}/answers.jsonl'

            indices_to_filename = self._save_summaries(summaries_file, summaries_list, references_list)
            metadata = self._run_preprocess(summaries_file, questions_file, metadata_file)
            filename_to_scores = self._run_answer_questions(questions_file, answers_file)
            metrics_lists = self._get_metrics(summaries_list, references_list, indices_to_filename, filename_to_scores, metadata)

            return metrics_lists


@MetricSetupSubcommand.register('apes')
class APESSetupSubcommand(MetricSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the APES metric'
        self.parser = parser.add_parser('apes', description=description, help=description)
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        commands = [
            f'mkdir -p {DATA_ROOT}/metrics/apes',
            f'cd {DATA_ROOT}/metrics/apes',
            f'git clone https://github.com/mataney/APES-on-TAC2011',
            f'git clone https://github.com/theblackcat102/rc-cnn-dailymail'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()

        if process.returncode == 0:
            print('APES setup success')
        else:
            print('APES setup failure')
