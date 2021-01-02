import argparse
import hashlib
import logging
import os
import shutil
import zipfile
from overrides import overrides
from packaging import version
from typing import Any, Dict, List, Tuple

from sacrerouge.commands import MetricSetupSubcommand
from sacrerouge.common import DATA_ROOT
from sacrerouge.common.util import download_file_from_google_drive
from sacrerouge.data import MetricsDict
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric

MIN_QAEVAL_VERSION = '0.0.4'
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
    from qaeval.scoring.scorers import ExactMatchF1, LERC, MetaScorer

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
                     lerc_batch_size: int = 8) -> None:
            super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())
            self.answer_selector = AnswerSelector(answer_selection_strategy)
            self.question_generator = QuestionGenerationModel(generation_model_path, cuda_device=cuda_device, batch_size=generation_batch_size)
            self.question_answerer = QuestionAnsweringModel(answering_model_dir, cuda_device=cuda_device, batch_size=answering_batch_size)

            scorers = [ExactMatchF1()]
            if use_lerc:
                scorers.append(LERC(lerc_model_path, lerc_pretrained_model_path, cuda_device, lerc_batch_size))
            self.scorer = MetaScorer(scorers)

        def _flatten_summaries(self, summaries_list: List[List[SummaryType]]) -> List[List[str]]:
            # Flattens all of the summaries so they are `str` instead of `List[str]`
            flat_summaries_list = []
            for summaries in summaries_list:
                flat_summaries_list.append([])
                for summary in summaries:
                    if isinstance(summary, list):
                        summary = ' '.join(summary)
                    flat_summaries_list[-1].append(summary)
            return flat_summaries_list

        def _unroll_summaries(self,
                              summaries_list: List[List[str]],
                              references_list: List[List[str]]) -> Tuple[List[str], List[List[str]]]:
            # The summaries are originally grouped by identical references. This will flatten the list of summaries
            # and copy the references into a parallel list for easier processing.
            unrolled_summaries = []
            unrolled_references = []
            for summaries, references in zip(summaries_list, references_list):
                for summary in summaries:
                    unrolled_summaries.append(summary)
                    unrolled_references.append(references)
            return unrolled_summaries, unrolled_references

        def _get_empty_summary_mask(self,
                                    summaries: List[str],
                                    references_list: List[List[str]]) -> Tuple[List[str], List[List[str]], List[bool]]:
            # This will identify any summaries that have empty text. The output will be the list of non-empty summaries
            # with their corresponding references plus a list of booleans that is parallel will the input `summaries`
            # which mark whether or not they are empty
            is_empty_list = []
            non_empty_summaries = []
            non_empty_references_list = []

            for summary, references in zip(summaries, references_list):
                if len(summary.strip()) > 0:
                    is_empty_list.append(False)
                    non_empty_summaries.append(summary)
                    non_empty_references_list.append(references)
                else:
                    is_empty_list.append(True)
            return non_empty_summaries, non_empty_references_list, is_empty_list

        def _get_question_id(self, instance_index: int, reference_index: int, start: int, end: int) -> str:
            m = hashlib.md5()
            m.update(str(instance_index).encode())
            m.update(str(reference_index).encode())
            m.update(str(start).encode())
            m.update(str(end).encode())
            return m.hexdigest()

        def _generate_qa_pairs(self, references_list: List[List[str]]) -> List[List[List[Dict[str, Any]]]]:
            # This will generate the question-answer pairs for each reference. Since references may be repeated,
            # we first deduplicate the references to minimize the expensive work.
            #
            # `reference_to_index` keeps track of where each of the unique references are in `distinct_references_list`
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
            # qa_pairs_lists[summary_index][reference_index] = [(q, a)]
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

        def _get_prediction_id(self, prediction_index: int):
            m = hashlib.md5()
            m.update(str(prediction_index).encode())
            return m.hexdigest()

        def _answer_questions(self,
                              summaries: List[str],
                              qa_pairs_lists: List[List[List[Dict[str, Any]]]]) -> List[List[List[Dict[str, Any]]]]:
            # Answers all of the questions. Some of the (question, context) pairs may be duplicates, for instance because
            # of jackknifing. It will be a lot faster to deduplicate them first.
            #
            # `qa_inputs` will contain the unique inputs, `context_to_input_index` maps from the (question, context) pair
            # to its index in `qa_inputs`, and `mapping` will map from the i-th summary, j-th reference, and k-th question
            # to the index of the corresponding data in `qa_inputs`
            qa_inputs = []
            context_to_input_index = {}
            mapping = {}

            for i, (summary, qa_pairs_list) in enumerate(zip(summaries, qa_pairs_lists)):
                for j, qa_pairs in enumerate(qa_pairs_list):
                    for k, qa in enumerate(qa_pairs):
                        question = qa['question']
                        key = (question, summary)
                        if key not in context_to_input_index:
                            context_to_input_index[key] = len(qa_inputs)
                            qa_inputs.append(key)
                        mapping[(i, j, k)] = context_to_input_index[key]

            logger.info(f'Answering {len(qa_inputs)} distinct (question, context) pairs')
            predictions = self.question_answerer.answer_all(qa_inputs)
            logger.info('Finished answering questions')

            # Remap from the distinct answers back to the original QA lists
            predictions_lists = []
            for i, (summary, qa_pairs_list) in enumerate(zip(summaries, qa_pairs_lists)):
                predictions_lists.append([])
                for j, qa_pairs in enumerate(qa_pairs_list):
                    predictions_lists[-1].append([])
                    for k, qa in enumerate(qa_pairs):
                        index = mapping[(i, j, k)]
                        prediction, probability, null_probability = predictions[index]
                        predictions_lists[-1][-1].append({
                            'prediction_id': self._get_prediction_id(index),
                            'prediction': prediction,
                            'probability': probability,
                            'null_probability': null_probability
                        })
            return predictions_lists

        def _score_predictions(self,
                               summaries: List[str],
                               qa_pairs_lists: List[List[List[Dict[str, Any]]]],
                               predictions_lists: List[List[List[Dict[str, Any]]]]) -> Tuple[List[MetricsDict], List[List[List[Dict[str, float]]]]]:
            metrics_list = []
            scores_list = []

            for summary, qa_pairs_list, predictions_list in zip(summaries, qa_pairs_lists, predictions_lists):
                # This is for 1 (summary, references) pair
                input_questions_list = []
                input_answers_list = []
                input_predictions_list = []
                input_probabilities_list = []
                input_null_probabilities_list = []
                for qa_pairs, predictions in zip(qa_pairs_list, predictions_list):
                    # This is the set of QA pairs for 1 reference
                    input_questions_list.append([])
                    input_answers_list.append([])
                    input_predictions_list.append([])
                    input_probabilities_list.append([])
                    input_null_probabilities_list.append([])
                    for qa, prediction in zip(qa_pairs, predictions):
                        input_questions_list[-1].append(qa['question'])
                        input_answers_list[-1].append(qa['answer'])
                        input_predictions_list[-1].append(prediction['prediction'])
                        input_probabilities_list[-1].append(prediction['probability'])
                        input_null_probabilities_list[-1].append(prediction['null_probability'])

                metrics, scores = self.scorer.score_multi_ref(summary, input_questions_list, input_answers_list, input_predictions_list, input_probabilities_list, input_null_probabilities_list)
                metrics = MetricsDict({'qa-eval': metrics})
                metrics_list.append(metrics)
                scores_list.append(scores)

            return metrics_list, scores_list

        def _combine_outputs(self,
                             metrics_list: List[MetricsDict],
                             qa_pairs_lists: List[List[List[Dict[str, Any]]]],
                             predictions_lists: List[List[List[Dict[str, Any]]]],
                             scores_lists: List[List[List[Dict[str, float]]]]) -> List[List[List[Dict[str, Any]]]]:
            # This method will combine the metrics and QA pair metadata together into a tuple so they can
            # both be returned together
            combined = []
            for metrics, qa_pairs_list, predictions_list, scores_list in zip(metrics_list, qa_pairs_lists, predictions_lists, scores_lists):
                # This is for 1 (summary, reference) pair
                combined.append((metrics, []))
                for qa_pairs, predictions, scores in zip(qa_pairs_list, predictions_list, scores_list):
                    # This is for 1 reference
                    combined[-1][1].append([])
                    for qa, prediction, score in zip(qa_pairs, predictions, scores):
                        prediction = dict(**prediction)
                        prediction['em'] = score['em']
                        prediction['f1'] = score['f1']
                        combined[-1][1][-1].append({'question': qa, 'prediction': prediction})
            return combined

        def _insert_empty_outputs(self,
                                  metrics_list: List[MetricsDict],
                                  is_empty_list: List[bool],
                                  include_qa_list: bool) -> List[Any]:
            full_metrics_list = []
            index = 0
            for is_empty in is_empty_list:
                if is_empty:
                    empty_metrics = MetricsDict({'qa-eval': {'em': 0.0, 'f1': 0.0}})
                    if include_qa_list:
                        full_metrics_list.append((empty_metrics, []))
                    else:
                        full_metrics_list.append(empty_metrics)
                else:
                    full_metrics_list.append(metrics_list[index])
                    index += 1
            return full_metrics_list

        def _realign_output(self,
                            summaries_list: List[List[SummaryType]],
                            output: List[Any]) -> List[List[Any]]:
            realigned = []
            index = 0
            for summaries in summaries_list:
                realigned.append([])
                for _ in summaries:
                    realigned[-1].append(output[index])
                    index += 1
            return realigned

        def score_multi_all(self,
                            summaries_list: List[List[SummaryType]],
                            references_list: List[List[ReferenceType]],
                            return_qa_pairs: bool = False) -> List[List[MetricsDict]]:
            summaries_list = self._flatten_summaries(summaries_list)
            references_list = self._flatten_summaries(references_list)

            # Unroll the summaries into lists of parallel (summary, references) pairs. The additional list around
            # the summaries can potentially make the code confusing. Unrolling the list makes it slightly easier to understand
            unrolled_summaries, unrolled_references_list = self._unroll_summaries(summaries_list, references_list)

            # Remove any input summaries that are empty. They mess up the processing otherwise
            unrolled_summaries, unrolled_references_list, is_empty_list = self._get_empty_summary_mask(unrolled_summaries, unrolled_references_list)

            qa_pairs_lists = self._generate_qa_pairs(unrolled_references_list)
            predictions_lists = self._answer_questions(unrolled_summaries, qa_pairs_lists)
            metrics_list, scores_lists = self._score_predictions(unrolled_summaries, qa_pairs_lists, predictions_lists)

            self._combine_outputs(metrics_list, qa_pairs_lists, predictions_lists, scores_lists)
            if return_qa_pairs:
                unrolled_output = self._combine_outputs(metrics_list, qa_pairs_lists, predictions_lists, scores_lists)
            else:
                unrolled_output = metrics_list
            unrolled_output = self._insert_empty_outputs(unrolled_output, is_empty_list, return_qa_pairs)

            output = self._realign_output(summaries_list, unrolled_output)
            return output


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
