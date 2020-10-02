import argparse
import hashlib
import logging
import os
import shutil
import zipfile
from overrides import overrides
from packaging import version
from typing import Any, Dict, List, Tuple

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT
from sacrerouge.common.util import download_file_from_google_drive
from sacrerouge.data import MetricsDict
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric

MIN_QAEVAL_VERSION = '0.0.1'
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
            super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())

        def score_multi_all(self,
                            summaries_list: List[List[SummaryType]],
                            references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
            raise Exception(
                f'Package "qaeval" could not be imported. Please install "qaeval" before running the metric. '
                f'The minimum required version is {MIN_QAEVAL_VERSION}')
else:
    from qaeval import AnswerSelector, QuestionAnsweringModel, QuestionGenerationModel
    from qaeval.answer_selection import NP_CHUNKS_STRATEGY, AnswerOffsets
    from qaeval.scoring import score_multiple_references

    QAEVAL_INSTALLED = True

    @Metric.register('qa-eval')
    class QAEval(ReferenceBasedMetric):
        def __init__(self,
                     answer_selection_strategy: str = NP_CHUNKS_STRATEGY,
                     generation_model_path: str = f'{DATA_ROOT}/metrics/qaeval/models/generation/model.tar.gz',
                     answering_model_dir: str = f'{DATA_ROOT}/metrics/qaeval/models/answering/model',
                     cuda_device: int = 0,
                     generation_batch_size: int = 8,
                     answering_batch_size: int = 8) -> None:
            super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())
            self.answer_selector = AnswerSelector(answer_selection_strategy)
            self.question_generator = QuestionGenerationModel(generation_model_path, cuda_device=cuda_device, batch_size=generation_batch_size)
            self.question_answerer = QuestionAnsweringModel(answering_model_dir, cuda_device=cuda_device, batch_size=answering_batch_size)

        def _flatten_summaries(self, summaries_list: List[List[SummaryType]]) -> List[List[str]]:
            flat_summaries_list = []
            for summaries in summaries_list:
                flat_summaries_list.append([])
                for summary in summaries:
                    if isinstance(summary, list):
                        summary = ' '.join(summary)
                    flat_summaries_list[-1].append(summary)
            return flat_summaries_list

        def _get_empty_summary_mask(self,
                                    summaries_list: List[List[str]],
                                    references_list: List[List[str]]) -> Tuple[List[List[str]], List[List[str]], List[List[bool]]]:
            is_empty_lists = []
            non_empty_summaries_list = []
            non_empty_references_list = []
            for summaries, references in zip(summaries_list, references_list):
                is_empty = []
                non_empty_summaries = []
                for summary in summaries:
                    if len(summary.strip()) > 0:
                        is_empty.append(False)
                        non_empty_summaries.append(summary)
                    else:
                        is_empty.append(True)

                is_empty_lists.append(is_empty)
                if len(non_empty_summaries) > 0:
                    non_empty_summaries_list.append(non_empty_summaries)
                    non_empty_references_list.append(references)

            return non_empty_summaries_list, non_empty_references_list, is_empty_lists

        def _get_question_id(self, instance_index: int, reference_index: int, start: int, end: int) -> str:
            m = hashlib.md5()
            m.update(str(instance_index).encode())
            m.update(str(reference_index).encode())
            m.update(str(start).encode())
            m.update(str(end).encode())
            return m.hexdigest()

        def _generate_qa_pairs(self, references_list: List[List[str]]) -> List[List[List[Dict[str, Any]]]]:
            # To minimize time, we generate questions for distinct references
            reference_to_index = {}
            distinct_references_list = []

            # Maps from (i, j) to the index in the `distinct_references_list`
            mapping = {}
            for i, references in enumerate(references_list):
                for j, reference in enumerate(references):
                    if reference not in reference_to_index:
                        reference_to_index[reference] = len(distinct_references_list)
                        distinct_references_list.append(reference)
                    mapping[(i, j)] = reference_to_index[reference]

            # Select the answers
            logger.info(f'Selecting answers from {len(distinct_references_list)} distinct summaries')
            answers_list = self.answer_selector.select_all(distinct_references_list)
            num_answers = sum(len(answers) for answers in answers_list)
            logger.info(f'Selected {num_answers} answers in total')

            # Generate the questions
            generation_inputs = []
            for reference, answers in zip(distinct_references_list, answers_list):
                for answer in answers:
                    sentence = reference[answer.sent_start:answer.sent_end]
                    start = answer.start - answer.sent_start
                    end = answer.end - answer.sent_start
                    generation_inputs.append((sentence, start, end))

            logging.info(f'Generating questions for {len(generation_inputs)} answers')
            question_list = self.question_generator.generate_all(generation_inputs)
            logging.info('Finished generating questions')

            # Remap the questions to align with the answers
            index = 0
            remapped_questions = []
            for i, answers in enumerate(answers_list):
                remapped_questions.append([])
                for _ in answers:
                    remapped_questions[-1].append(question_list[index])
                    index += 1
                assert len(remapped_questions[i]) == len(answers_list[i])
            assert len(remapped_questions) == len(answers_list)

            # Remap output to align with the inputs
            # qa_pairs_lists[input_instance][summary] = [(q, a)]
            qa_pairs_lists = []
            for i, references in enumerate(references_list):
                qa_pairs_lists.append([])
                for j, reference in enumerate(references):
                    index = mapping[(i, j)]
                    qa_pairs_lists[-1].append([])
                    for question, answer in zip(remapped_questions[index], answers_list[index]):
                        question_id = self._get_question_id(i, j, answer.start, answer.end)
                        qa_pairs_lists[-1][-1].append({
                            'question_id': question_id,
                            'question': question,
                            'answer': answer.text,
                            'sent_start': answer.sent_start,
                            'sent_end': answer.sent_end,
                            'answer_start': answer.start,
                            'answer_end': answer.end
                        })
            return qa_pairs_lists

        def _get_prediction_id(self, instance_index: int, summary_index: int, reference_index: int, question_index: int):
            m = hashlib.md5()
            m.update(str(instance_index).encode())
            m.update(str(summary_index).encode())
            m.update(str(reference_index).encode())
            m.update(str(question_index).encode())
            return m.hexdigest()

        def _answer_questions(self,
                              summaries_list: List[List[str]],
                              qa_pairs_lists: List[List[List[Dict[str, Any]]]]) -> List[List[List[List[Dict[str, Any]]]]]:
            # Some (question, context) pairs might be duplicates (for instance because of jackknifing), so it should
            # be a lot faster to deduplicate them
            qa_inputs = []
            context_to_input_index = {}
            mapping = {}

            for i, (summaries, qa_pairs_list) in enumerate(zip(summaries_list, qa_pairs_lists)):
                for j, summary in enumerate(summaries):
                    for k, qa_pairs in enumerate(qa_pairs_list):
                        for l, question_dict in enumerate(qa_pairs):
                            question = question_dict['question']
                            key = (question, summary)
                            if key not in context_to_input_index:
                                context_to_input_index[key] = len(qa_inputs)
                                qa_inputs.append(key)
                            mapping[(i, j, k, l)] = context_to_input_index[key]

            logger.info(f'Answering {len(qa_inputs)} distinct (question, context) pairs')
            predictions = self.question_answerer.answer_all(qa_inputs)
            logger.info('Finished answering questions')

            # all_predictions_lists[instance][summary][reference] = [(prediction, prob, null_prob)]
            all_predictions_lists = []
            for i, (summaries, qa_pairs_list) in enumerate(zip(summaries_list, qa_pairs_lists)):
                all_predictions_lists.append([])
                for j in range(len(summaries)):
                    all_predictions_lists[-1].append([])
                    for k, qa_pairs in enumerate(qa_pairs_list):
                        all_predictions_lists[-1][-1].append([])
                        for l, question_dict in enumerate(qa_pairs):
                            index = mapping[(i, j, k, l)]
                            prediction, probability, null_probability = predictions[index]
                            all_predictions_lists[-1][-1][-1].append({
                                'prediction_id': self._get_prediction_id(i, j, k, l),
                                'prediction': prediction,
                                'probability': probability,
                                'null_probability': null_probability
                            })
            return all_predictions_lists

        def _score_predictions(self,
                               qa_pairs_lists: List[List[List[Dict[str, Any]]]],
                               all_predictions_lists: List[List[List[List[Dict[str, Any]]]]]) -> Tuple[List[List[MetricsDict]], List[List[List[List[Dict[str, float]]]]]]:
            metrics_lists = []
            all_scores_lists = []
            for qa_pairs_list, predictions_lists in zip(qa_pairs_lists, all_predictions_lists):
                answers_list = []
                for qa_pairs in qa_pairs_list:
                    answers_list.append([qa['answer'] for qa in qa_pairs])

                metrics_lists.append([])
                all_scores_lists.append([])
                for predictions_list in predictions_lists:
                    pred_strings_list = []
                    probabilities_list = []
                    null_probabilities_list = []
                    for predictions in predictions_list:
                        preds = [pred['prediction'] for pred in predictions]
                        probabilities = [pred['probability'] for pred in predictions]
                        null_probabilities = [pred['null_probability'] for pred in predictions]
                        pred_strings_list.append(preds)
                        probabilities_list.append(probabilities)
                        null_probabilities_list.append(null_probabilities)

                    em, f1, ems_list, f1s_list = score_multiple_references(answers_list, pred_strings_list, probabilities_list, null_probabilities_list, return_all_scores=True)
                    metrics_lists[-1].append(MetricsDict({'qa-eval': {'em': em, 'f1': f1}}))

                    all_scores_lists[-1].append([])
                    for reference_em, reference_f1 in zip(ems_list, f1s_list):
                        all_scores_lists[-1][-1].append([{'em': x, 'f1': y} for x, y in zip(reference_em, reference_f1)])

            return metrics_lists, all_scores_lists

        def _combine_outputs(self,
                             metrics_list: List[List[MetricsDict]],
                             qa_pairs_lists: List[List[List[Dict[str, Any]]]],
                             all_predictions_lists: List[List[List[List[Dict[str, Any]]]]],
                             all_scores_lists: List[List[List[List[Dict[str, float]]]]]) -> List[List[List[List[Dict[str, Any]]]]]:
            combined_lists = []
            for metrics, qa_pairs_list, predictions_lists, scores_lists in zip(metrics_list, qa_pairs_lists, all_predictions_lists, all_scores_lists):
                combined_lists.append([])
                for metric, predictions_list, scores_list in zip(metrics, predictions_lists, scores_lists):
                    combined_lists[-1].append((metric, []))
                    for qa_pairs, predictions, scores in zip(qa_pairs_list, predictions_list, scores_list):
                        combined_lists[-1][-1][1].append([])
                        for qa, prediction, score in zip(qa_pairs, predictions, scores):
                            prediction = dict(**prediction)
                            prediction['em'] = score['em']
                            prediction['f1'] = score['f1']
                            combined_lists[-1][-1][1][-1].append({
                                'question': qa,
                                'prediction': prediction
                            })
            return combined_lists

        def _insert_empty_outputs(self,
                                  metrics_list: List[List[MetricsDict]],
                                  is_empty_lists: List[List[bool]],
                                  include_qa_list: bool) -> List[List[MetricsDict]]:
            # `is_empty_lists` tells us whether or not the respective input was empty. This runs in parallel with the
            # original input. `metrics_list` is the output of the non-empty data. We need to insert empty metrics
            # in the empty input positions, so we iterate over `is_empty_lists` and insert empty results and only
            # progress through `metrics_list` if it's non-empty.
            full_metrics_list = []
            i = 0
            for is_empty_list in is_empty_lists:
                full_metrics_list.append([])
                j = 0
                for is_empty in is_empty_list:
                    if is_empty:
                        empty_metrics = MetricsDict({'qa-eval': {'em': 0.0, 'f1': 0.0}})
                        if include_qa_list:
                            full_metrics_list[-1].append((empty_metrics, []))
                        else:
                            full_metrics_list[-1].append(empty_metrics)
                    else:
                        full_metrics_list[-1].append(metrics_list[i][j])
                        j += 1
                if j > 0:
                    # This means we consumed one from this row
                    i += 1
            return full_metrics_list

        def score_multi_all(self,
                            summaries_list: List[List[SummaryType]],
                            references_list: List[List[ReferenceType]],
                            return_qa_pairs: bool = False) -> List[List[MetricsDict]]:
            summaries_list = self._flatten_summaries(summaries_list)
            references_list = self._flatten_summaries(references_list)

            summaries_list, references_list, is_empty_lists = self._get_empty_summary_mask(summaries_list, references_list)

            qa_pairs_lists = self._generate_qa_pairs(references_list)
            all_predictions_lists = self._answer_questions(summaries_list, qa_pairs_lists)
            metrics_list, scores_lists = self._score_predictions(qa_pairs_lists, all_predictions_lists)

            if return_qa_pairs:
                output = self._combine_outputs(metrics_list, qa_pairs_lists, all_predictions_lists, scores_lists)
            else:
                output = metrics_list
            return self._insert_empty_outputs(output, is_empty_lists, return_qa_pairs)


class QAEvalSetupSubcommand(Subcommand):
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

        print('Downloading models complete')
