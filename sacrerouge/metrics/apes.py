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
                        references_list: List[List[ReferenceType]]) -> Dict[str, List[str]]:
        instance_id_to_reference_ids = {}
        output_data = {}

        logger.info(f'Writing summaries to {output_file}')
        for i, (summaries, references) in enumerate(zip(summaries_list, references_list)):
            instance_id = str(i)
            output_data[instance_id] = {'man': {}, 'machine': {}}

            for j, summary in enumerate(summaries):
                summarizer_id = f'{instance_id}_{j}'
                if isinstance(summary, list):
                    text = ' '.join(summary)
                else:
                    text = summary
                output_data[instance_id]['machine'][summarizer_id] = text

            # We identify references with a letter
            assert len(references) <= 26
            reference_ids = []
            for j, reference in enumerate(references):
                reference_id = f'{instance_id}_{string.ascii_uppercase[j]}'
                reference_ids.append(reference_id)
                if isinstance(reference, list):
                    text = ' '.join(reference)
                else:
                    text = reference
                output_data[instance_id]['man'][reference_id] = text
            instance_id_to_reference_ids[instance_id] = reference_ids

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as out:
            out.write(json.dumps(output_data))

        return instance_id_to_reference_ids

    def _run_preprocess(self, input_file: str, output_file: str, metadata_file: str) -> Dict:
        logger.info('Running preprocessing')
        commands = [f'cd {self.apes_root}/APES-on-TAC2011']
        commands.append(f'source {os.environ["CONDA_INIT"]}')
        commands.append(f'conda activate {self.environment_name}')
        commands.append(f'python2.7 apes_on_tac2011.py --input-file {input_file} --output-file {output_file} --metadata-file {metadata_file}')
        command = ' && '.join(commands)

        logger.info(f'Running command: "{command}"')
        redirect = None if self.verbose else PIPE
        process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
        process.communicate()

        metadata = json.load(open(metadata_file, 'r'))
        return metadata

    def _run_answer_questions(self, input_file: str, output_file: str) -> Dict[Tuple[str, str], Dict[str, float]]:
        logger.info('Running answering questions')
        commands = [f'cd {self.apes_root}/rc-cnn-dailymail']
        commands.append(f'source {os.environ["CONDA_INIT"]}')
        commands.append(f'conda activate {self.environment_name}')
        commands.append(f'python2.7 code/run_qa_model.py --input_file {input_file} --output_file {output_file} --train_path cnn_train.txt --dev_path cnn_dev.txt --glove_path glove.6B.100d.txt')
        command = ' && '.join(commands)

        logger.info(f'Running command: "{command}"')
        redirect = None if self.verbose else PIPE
        process = Popen(command, stdout=redirect, stderr=redirect, shell=True)
        process.communicate()

        ids_to_scores = {}
        with JsonlReader(output_file) as f:
            for data in f:
                summarizer_id = data['answering_doc']
                reference_id = data['questioning_doc']
                accuracy = data['acc']
                num_correct = data['num_correct']
                ids_to_scores[(summarizer_id, reference_id)] = {'accuracy': accuracy, 'num_correct': num_correct}
        return ids_to_scores

    def _get_metrics(self,
                     summaries_list: List[List[SummaryType]],
                     references_list: List[List[ReferenceType]],
                     instance_id_to_reference_ids: Dict[str, List[str]],
                     ids_to_scores: Dict[Tuple[str, str], Dict[str, float]],
                     metadata: Dict) -> List[List[MetricsDict]]:
        metrics_lists = []
        missing_entities = metadata['missing_entities']
        missing_questions = metadata['missing_questions']
        for i, (summaries, references) in enumerate(zip(summaries_list, references_list)):
            metrics_lists.append([])
            instance_id = str(i)
            reference_ids = instance_id_to_reference_ids[instance_id]

            num_missing_entities = len(missing_entities[instance_id]) if instance_id in missing_entities else 0
            if num_missing_entities > 0:
                logger.warning(f'{num_missing_entities} reference(s) for instance index {i} are missing entities. No questions were generated')

            num_missing_questions = len(missing_questions[instance_id]) if instance_id in missing_questions else 0
            if num_missing_questions > 0:
                logger.warning(f'{num_missing_questions} reference(s) for instance index {i} are missing questions')

            for j, summary in enumerate(summaries):
                summarizer_id = f'{i}_{j}'
                scores = []
                for reference_id in reference_ids:
                    if (summarizer_id, reference_id) in ids_to_scores:
                        scores.append(ids_to_scores[(summarizer_id, reference_id)])

                if len(scores) + num_missing_entities + num_missing_questions != len(reference_ids):
                    logger.warning(f'Summary {j} for instance {i} does not have a score for every reference. '
                                   f'#Score: {len(scores)}, #Missing Entities: {num_missing_entities}, #Missing Qs: {num_missing_questions} #Ref: {len(reference_ids)}')

                if len(scores) == 0:
                    # All references were missing entities
                    scores = [{'accuracy': 0.0, 'num_correct': 0}]

                final_accuracy = sum([s['accuracy'] for s in scores]) / len(scores)
                final_num_correct = sum([s['num_correct'] for s in scores])
                metrics_lists[-1].append(MetricsDict({'APES': {'accuracy': final_accuracy, 'num_correct': final_num_correct}}))
        return metrics_lists

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        with TemporaryDirectory() as temp_dir:
            temp_dir = os.path.abspath(temp_dir)

            summaries_file = f'{temp_dir}/summaries.json'
            questions_file = f'{temp_dir}/questions.jsonl'
            metadata_file = f'{temp_dir}/metadata.json'
            answers_file = f'{temp_dir}/answers.jsonl'

            instance_id_to_reference_ids = self._save_summaries(summaries_file, summaries_list, references_list)
            metadata = self._run_preprocess(summaries_file, questions_file, metadata_file)
            ids_to_scores = self._run_answer_questions(questions_file, answers_file)
            metrics_lists = self._get_metrics(summaries_list, references_list, instance_id_to_reference_ids, ids_to_scores, metadata)

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
            f'git clone https://github.com/theblackcat102/rc-cnn-dailymail',
            f'cd rc-cnn-dailymail',
            f'wget https://danieldeutsch.s3.amazonaws.com/sacrerouge/metrics/APES/cnn_train.txt.gz',
            f'wget https://danieldeutsch.s3.amazonaws.com/sacrerouge/metrics/APES/cnn_dev.txt.gz',
            f'zcat cnn_train.txt.gz > cnn_train.txt',
            f'zcat cnn_dev.txt.gz > cnn_dev.txt',
            f'rm cnn_train.txt.gz cnn_dev.txt.gz',
            f'wget http://nlp.stanford.edu/data/glove.6B.zip',
            f'unzip glove.6B.zip',
            f'rm glove.6B.50d.txt glove.6B.200d.txt glove.6B.300d.txt glove.6B.zip',
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()

        if process.returncode == 0:
            print('APES setup success')
        else:
            print('APES setup failure')
