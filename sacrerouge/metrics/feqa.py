import argparse
import logging
import os
import shutil
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List

from sacrerouge.commands import MetricSetupSubcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.common.util import download_file_from_google_drive
from sacrerouge.data import MetricsDict
from sacrerouge.data.types import DocumentType, SummaryType
from sacrerouge.io import JsonlReader, JsonlWriter
from sacrerouge.metrics import Metric, DocumentBasedMetric

logger = logging.getLogger(__name__)


@Metric.register('feqa')
class FEQA(DocumentBasedMetric):
    def __init__(self,
                 environment_name: str = None,
                 feqa_root: str = f'{DATA_ROOT}/metrics/feqa',
                 batch_size: int = 8) -> None:
        super().__init__(['summary'], ['documents'])
        self.environment_name = environment_name
        self.feqa_root = feqa_root
        self.batch_size = batch_size

        if self.environment_name is not None:
            if 'CONDA_INIT' not in os.environ:
                raise Exception('If `environment_name` is not none, environment variable "CONDA_INIT" must be set to the path to "conda.sh"')

    def _ensure_single_document(self, documents_list: List[List[DocumentType]]):
        # For now, the code only works if there's 1 input document. The QA model only evalutes against one document,
        # so I think it may have to fundamentally change for multi-documents
        for documents in documents_list:
            assert len(documents) == 1

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        documents_list: List[List[DocumentType]]) -> List[List[MetricsDict]]:
        self._ensure_single_document(documents_list)

        with TemporaryDirectory() as temp_dir:
            input_file = f'{temp_dir}/input.jsonl'
            output_file = f'{temp_dir}/output.jsonl'
            with JsonlWriter(input_file) as out:
                for summaries, documents in zip(summaries_list, documents_list):
                    assert len(documents) == 1
                    document = documents[0]
                    if isinstance(document, list):
                        document = ' '.join(document)
                    for summary in summaries:
                        if isinstance(summary, list):
                            summary = ' '.join(summary)
                        out.write({'document': document, 'summary': summary})

            commands = []
            if self.environment_name is not None:
                commands.append(f'source {os.environ["CONDA_INIT"]}')
                commands.append(f'conda activate {self.environment_name}')
            commands.append(f'cd {self.feqa_root}')
            commands.append(f'python run.py {input_file} {output_file} {self.batch_size}')
            command = ' && '.join(commands)
            logger.info(f'Running FEQA command: "{command}"')
            process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
            stdout, stderr = process.communicate()
            logger.info(stdout.decode())
            logger.error(stderr.decode())

            scores = JsonlReader(output_file).read()
            metrics_list = []
            index = 0
            for summaries in summaries_list:
                metrics_list.append([])
                for _ in summaries:
                    metrics_list[-1].append(MetricsDict({'FEQA': scores[index]['score']}))
                    index += 1
            return metrics_list


@MetricSetupSubcommand.register('feqa')
class FEQASetupSubcommand(MetricSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the FEQA metric'
        self.parser = parser.add_parser('feqa', description=description, help=description)
        self.parser.add_argument('--force', action='store_true', help='Force setting up the metric again')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        if args.force and os.path.exists(f'{DATA_ROOT}/metrics/feqa'):
            shutil.rmtree(f'{DATA_ROOT}/metrics/feqa')

        # Clone the github repo
        if not os.path.exists(f'{DATA_ROOT}/metrics/feqa'):
            commands = [
                f'mkdir -p {DATA_ROOT}/metrics',
                f'cd {DATA_ROOT}/metrics',
                f'git clone https://github.com/danieldeutsch/feqa',
            ]
            command = ' && '.join(commands)
            process = Popen(command, shell=True)
            process.communicate()

        # Download the model files
        gdrive_files = {
            'qa_models/squad1.0/config.json': '1IwWhQf9MP2G-vOBsQD87kMMEBS0IvcXa',
            'qa_models/squad1.0/dev-v1.1.json': '1tsWhCsXSxxgkBMBnGB9wkOliJH8K3Prs',
            'qa_models/squad1.0/evaluate-v1.1.py': '1p-LlVVAGuMYjFckjK5HxdiK5xEuM-2Ev',
            'qa_models/squad1.0/pytorch_model.bin': '1pWMsSTTwcoX0l75bzNFjvSC7firawp9M',
            'qa_models/squad1.0/run_squad.py': '1yZKNFU7md4KPGmThPwsp4dt95HkKsArX',
            'qa_models/squad1.0/special_tokens_map.json': '1rbv75oE5x0rXxtGGXETTvLBoHK5h3Lfj',
            'qa_models/squad1.0/tokenizer_config.json': '1oPM62qOWofGnaLmlX_CWkYKbZ-KEMtym',
            'qa_models/squad1.0/train-v1.1.json': '1y9_EgnoBbm0SJeCaNZFfjOyraeA-qfqP',
            'qa_models/squad1.0/training_args.bin': '1r49Y1Cp2t6_II2xjOyxbvYVvp2EQj3zu',
            'qa_models/squad1.0/vocab.txt': '1iGZrP6_3PiiH0pcF4zoSbqAsWdFvimfF',
            'bart_qg/checkpoints/checkpoint_best.pt': '1GFnimonLFgGal1LT6KRgMJZLbxmNJvxF',
            'bart_qg/checkpoints/dict.src.txt': '17CShx4cUEQTl_gpLapnbMsc7CmDAaV7r',
            'bart_qg/checkpoints/dict.tgt.txt': '1_dUN7CQZdqPxoiezzWp5yByuEXVJFwce',
        }
        for file_path, file_id in gdrive_files.items():
            download_file_from_google_drive(file_id, f'{DATA_ROOT}/metrics/feqa/{file_path}', force=args.force)

        print('FEQA setup success')