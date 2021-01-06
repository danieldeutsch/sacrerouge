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
from sacrerouge.metrics import Metric, DocumentBasedMetric

logger = logging.getLogger(__name__)


@Metric.register('qags')
class QAGS(DocumentBasedMetric):
    def __init__(self,
                 environment_name: str = None,
                 qags_root: str = f'{DATA_ROOT}/metrics/QAGS',
                 cuda_device: int = 0):
        super().__init__(['summary'], ['documents'])
        self.environment_name = environment_name
        self.qags_root = qags_root
        self.cuda_device = cuda_device

        if self.environment_name is not None:
            if 'CONDA_INIT' not in os.environ:
                raise Exception('If `environment_name` is not none, environment variable "CONDA_INIT" must be set to the path to "conda.sh"')

    def _ensure_single_document(self, documents_list: List[List[DocumentType]]):
        # For now, the code only works if there's 1 input document. The QA model only evalutes against one document,
        # so I think it may have to fundamentally change for multi-documents
        for documents in documents_list:
            assert len(documents) == 1

    def _save_input(self,
                    summaries_list: List[List[SummaryType]],
                    documents_list: List[List[DocumentType]],
                    summaries_file: str,
                    documents_file: str) -> None:
        # Serialize the summaries and documents into two parallel files
        os.makedirs(os.path.dirname(summaries_file), exist_ok=True)
        os.makedirs(os.path.dirname(documents_file), exist_ok=True)

        with open(summaries_file, 'w') as out_summaries:
            with open(documents_file, 'w') as out_documents:
                for summaries, documents in zip(summaries_list, documents_list):
                    assert len(documents) == 1
                    document = documents[0]
                    if isinstance(document, list):
                        document = ' '.join(document)
                    for summary in summaries:
                        if isinstance(summary, list):
                            summary = ' '.join(summary)
                        out_summaries.write(summary + '\n')
                        out_documents.write(document + '\n')

    def _select_answers(self, summaries_file: str, output_dir: str) -> None:
        # Select the (document, answer) pairs
        commands = []
        if self.environment_name is not None:
            commands.append(f'source {os.environ["CONDA_INIT"]}')
            commands.append(f'conda activate {self.environment_name}')
        commands.append(f'cd {self.qags_root}/qags')
        commands.append(f'python qg_utils.py --command extract_ans --data_file {summaries_file} --out_dir {output_dir}')
        command = ' && '.join(commands)
        logger.info(f'Running QAGS command: "{command}"')
        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()

    def _preprocess_answers(self, summary_answer_file: str, output_dir: str) -> None:
        # Copy the output file to a new file that is expected by the fairseq preprocessing. Both the src and
        # trg file are required, but the trg can  be a dummy
        os.makedirs(output_dir)
        shutil.copy(summary_answer_file, f'{output_dir}/test.src')
        shutil.copy(summary_answer_file, f'{output_dir}/test.trg')

        # Run the preprocessing
        commands = []
        if self.environment_name is not None:
            commands.append(f'source {os.environ["CONDA_INIT"]}')
            commands.append(f'conda activate {self.environment_name}')
        commands.append(f'cd {self.qags_root}/qags')
        commands.append(f'sh fairseq/scripts/aw/preprocess_qags.sh {output_dir} {self.qags_root}/models/dict.txt')
        command = ' && '.join(commands)
        logger.info(f'Running QAGS command: "{command}"')
        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()

    def _generate_questions(self, input_dir: str, output_file: str) -> None:
        # Generate the questions
        bert_path = f'{self.qags_root}/models/qg/best_pretrained_bert.pt'
        model_path = f'{self.qags_root}/models/qg/qg_best.pt'

        # The script adds .txt to the filename, which it already has, so we remove it here
        output_file = output_file[:-4]

        commands = []
        if self.environment_name is not None:
            commands.append(f'source {os.environ["CONDA_INIT"]}')
            commands.append(f'conda activate {self.environment_name}')
        commands.append(f'cd {self.qags_root}/qags')
        commands.append(f'HACK_PATH={bert_path} sh scripts/gen_qg.sh {self.cuda_device} {model_path} {input_dir} {output_file}')
        command = ' && '.join(commands)
        logger.info(f'Running QAGS command: "{command}"')
        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()

    def _parse_questions(self, input_file: str, output_dir: str) -> None:
        commands = []
        if self.environment_name is not None:
            commands.append(f'source {os.environ["CONDA_INIT"]}')
            commands.append(f'conda activate {self.environment_name}')
        commands.append(f'cd {self.qags_root}/qags')
        commands.append(f'python qg_utils.py --command extract_gen --data_file {input_file} --out_dir {output_dir}')
        command = ' && '.join(commands)
        logger.info(f'Running QAGS command: "{command}"')
        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()

    def _preprocess_all_questions(self,
                                  summaries_file: str,
                                  documents_file: str,
                                  input_questions_file: str,
                                  input_probs_file: str,
                                  output_dir: str) -> None:
        commands = []
        if self.environment_name is not None:
            commands.append(f'source {os.environ["CONDA_INIT"]}')
            commands.append(f'conda activate {self.environment_name}')
        commands.append(f'cd {self.qags_root}/qags')
        commands.append(
            f'python qa_utils.py --command format-qa-data '
            f'--out_dir {output_dir} --src_txt_file {documents_file} '
            f'--gen_txt_file {summaries_file} '
            f'--gen_qst_file {input_questions_file} '
            f'--gen_prob_file {input_probs_file} '
            f'--use_all_qsts'
        )
        command = ' && '.join(commands)
        logger.info(f'Running QAGS command: "{command}"')
        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()

    def _run_qa_model(self, input_file: str, prediction_file: str) -> None:
        output_dir = os.path.dirname(prediction_file)
        os.makedirs(output_dir)
        commands = []
        if self.environment_name is not None:
            commands.append(f'source {os.environ["CONDA_INIT"]}')
            commands.append(f'conda activate {self.environment_name}')
        commands.append(f'cd {self.qags_root}/qags')
        commands.append(
            f'python finetune_pt_squad.py '
            f'--bert_model bert-large-uncased '
            f'--load_model_from_dir {self.qags_root}/models/qa '
            f'--version_2_with_negative '
            f'--do_predict '
            f'--do_lower_case '
            f'--predict_file {input_file} '
            f'--output_dir {output_dir} '
            f'--prediction_file {prediction_file} '
        )
        command = ' && '.join(commands)
        logger.info(f'Running QAGS command: "{command}"')
        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()

    def _filter_questions(self,
                          summaries_file: str,
                          documents_file: str,
                          input_questions_file: str,
                          input_probs_file: str,
                          answers_file: str,
                          predictions_file: str,
                          output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        commands = []
        if self.environment_name is not None:
            commands.append(f'source {os.environ["CONDA_INIT"]}')
            commands.append(f'conda activate {self.environment_name}')
        commands.append(f'cd {self.qags_root}/qags')
        commands.append(
            f'python qa_utils.py --command format-qa-data '
            f'--out_dir {output_dir} --src_txt_file {documents_file} '
            f'--gen_txt_file {summaries_file} '
            f'--gen_qst_file {input_questions_file} '
            f'--gen_prob_file {input_probs_file} '
            f'--use_exp_anss '
            f'--gen_ans_file {answers_file} ' 
            f'--gen_prd_file {predictions_file}'
        )
        command = ' && '.join(commands)
        logger.info(f'Running QAGS command: "{command}"')
        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()

    def _calculate_scores(self, summary_scores_file: str, document_scores_file: str, output_dir: str):
        os.makedirs(output_dir)
        commands = []
        if self.environment_name is not None:
            commands.append(f'source {os.environ["CONDA_INIT"]}')
            commands.append(f'conda activate {self.environment_name}')
        commands.append(f'cd {self.qags_root}/qags')
        commands.append(
            f'python qa_utils.py --command compute-qags '
            f'--source_ans_file {summary_scores_file} '
            f'--target_ans_file {document_scores_file} '
            f'--out_dir {output_dir}'
        )
        command = ' && '.join(commands)
        logger.info(f'Running QAGS command: "{command}"')
        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()

    def _parse_scores(self, summaries_list: List[List[SummaryType]], scores_file: str) -> List[List[MetricsDict]]:
        scores = list(map(float, open(scores_file, 'r').read().splitlines()))
        metrics_list = []
        index = 0
        for summaries in summaries_list:
            metrics_list.append([])
            for _ in summaries:
                metrics_list[-1].append(MetricsDict({'QAGS': scores[index]}))
                index += 1
        return metrics_list

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        documents_list: List[List[DocumentType]]) -> List[List[MetricsDict]]:
        self._ensure_single_document(documents_list)

        with TemporaryDirectory() as temp_dir:
            summaries_file = f'{temp_dir}/00-input/summaries.txt'
            documents_file = f'{temp_dir}/00-input/documents.txt'
            self._save_input(summaries_list, documents_list, summaries_file, documents_file)

            summary_answer_dir = f'{temp_dir}/01-summary-answers-pairs'
            answer_file = f'{summary_answer_dir}/test_10ans.txt'
            summary_answer_file = f'{summary_answer_dir}/test_w_10ans.txt'
            self._select_answers(summaries_file, summary_answer_dir)

            generation_input_root_dir = f'{temp_dir}/02-generation-input'
            generation_input_dir = f'{generation_input_root_dir}/processed'
            self._preprocess_answers(summary_answer_file, generation_input_root_dir)

            questions_dir = f'{temp_dir}/03-questions'
            questions_log_file = f'{questions_dir}/log.txt'
            all_questions_file = f'{questions_dir}/gens.txt'
            all_questions_probs_file = f'{questions_dir}/probs.txt'
            self._generate_questions(generation_input_dir, questions_log_file)
            self._parse_questions(questions_log_file, questions_dir)

            all_questions_input_file = f'{questions_dir}/gen.json'
            self._preprocess_all_questions(summaries_file, documents_file, all_questions_file,
                                           all_questions_probs_file, questions_dir)

            all_predictions_dir = f'{temp_dir}/04-predictions'
            all_predictions_file = f'{all_predictions_dir}/predictions.json'
            self._run_qa_model(all_questions_input_file, all_predictions_file)

            filtered_questions_dir = f'{temp_dir}/05-filtered-questions'
            filtered_questions_summary_input_file = f'{filtered_questions_dir}/gen.json'
            filtered_questions_document_input_file = f'{filtered_questions_dir}/src.json'
            self._filter_questions(summaries_file, documents_file, all_questions_file,
                                   all_questions_probs_file, answer_file, all_predictions_file, filtered_questions_dir)

            filtered_predictions_dir = f'{temp_dir}/06-filtered-predictions'
            filtered_summary_predictions = f'{filtered_predictions_dir}/gen/predictions.json'
            filtered_document_predictions = f'{filtered_predictions_dir}/src/predictions.json'
            self._run_qa_model(filtered_questions_summary_input_file, filtered_summary_predictions)
            self._run_qa_model(filtered_questions_document_input_file, filtered_document_predictions)

            scores_dir = f'{temp_dir}/07-scores'
            scores_file = f'{scores_dir}/qags_scores.txt'
            self._calculate_scores(filtered_summary_predictions, filtered_document_predictions, scores_dir)

            scores = self._parse_scores(summaries_list, scores_file)
            return scores


@MetricSetupSubcommand.register('qags')
class QAGSSetupSubcommand(MetricSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the QAGS metric'
        self.parser = parser.add_parser('qags', description=description, help=description)
        self.parser.add_argument('--force', action='store_true', help='Force setting up the metric again')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        if args.force and os.path.exists(f'{DATA_ROOT}/metrics/QAGS'):
            shutil.rmtree(f'{DATA_ROOT}/metrics/QAGS')

        # Clone the github repo
        if not os.path.exists(f'{DATA_ROOT}/metrics/QAGS/qags'):
            commands = [
                f'mkdir -p {DATA_ROOT}/metrics/QAGS',
                f'cd {DATA_ROOT}/metrics/QAGS',
                f'git clone https://github.com/danieldeutsch/qags',
            ]
            command = ' && '.join(commands)
            process = Popen(command, shell=True)
            process.communicate()

        # Download the model files
        gdrive_files = {
            'dict.txt': '16WLYT3kWwDqQKThsKPprzC2l9VddtLGW',
            'qa/bert_config.json': '1wJCAl10Es8RNoTEXbFbsXEbNzTePmnED',
            'qa/config.json': '10mPwP5r0tVOzUWF7R44EuCGJoGC-aMoh',
            'qa/pytorch_model.bin': '18pMy2fByYXtenpETMcpW4R9cBraTz500',
            'qa/training_args.bin': '18PEqwlSTNKS4yG3dXsVLELFx28Suba5m',
            'qa/vocab.txt': '1YLZocwcWiEiHPyPw-ZKKJ1kHxP-x6Ev6',
            'qg/best_pretrained_bert.pt': '1OTl9Q7-09oR52Ct85WNumOn6yO0kAkKj',
            'qg/qg_best.pt': '15ajJYSEjZ-cuQ7KlCxfOVKnzkPGVudpJ',
        }
        for file_path, file_id in gdrive_files.items():
            download_file_from_google_drive(file_id, f'{DATA_ROOT}/metrics/QAGS/models/{file_path}', force=args.force)

        print('QAGS setup success')