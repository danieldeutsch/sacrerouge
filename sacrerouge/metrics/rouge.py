import argparse
import logging
import os
from collections import defaultdict
from overrides import overrides
from subprocess import Popen, PIPE
from typing import List, Optional, Tuple

from sacrerouge.commands import Subcommand
from sacrerouge.common import DATA_ROOT, TemporaryDirectory
from sacrerouge.common.util import download_file_from_google_drive
from sacrerouge.data import MetricsDict
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.data.jackknifers import ReferencesJackknifer
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric

logger = logging.getLogger(__name__)


@Metric.register('rouge')
class Rouge(ReferenceBasedMetric):
    def __init__(self,
                 max_ngram: int = 4,
                 use_porter_stemmer: bool = True,
                 remove_stopwords: bool = False,
                 max_bytes: Optional[int] = None,
                 max_words: Optional[int] = None,
                 compute_rouge_l: bool = False,
                 skip_bigram_gap_length: Optional[int] = None,
                 wlcs_weight: Optional[float] = None,
                 rouge_root: str = f'{DATA_ROOT}/metrics/ROUGE-1.5.5',
                 scoring_function: str = 'average'):
        super().__init__(['summary'], ['references'], jackknifer=ReferencesJackknifer())
        self.max_ngram = max_ngram
        self.use_porter_stemmer = use_porter_stemmer
        self.remove_stopwords = remove_stopwords
        self.max_bytes = max_bytes
        self.max_words = max_words
        self.compute_rouge_l = compute_rouge_l
        self.skip_bigram_gap_length = skip_bigram_gap_length
        self.wlcs_weight = wlcs_weight
        self.rouge_script_location = f'{rouge_root}/ROUGE-1.5.5.pl'
        self.rouge_eval_home = f'{rouge_root}/data'
        self.scoring_function = scoring_function

        if not os.path.exists(rouge_root):
            raise Exception(f'Path "{rouge_root}" does not exist. Have you setup ROUGE?')

    def _save_summary(self, summary: SummaryType, file_path: str) -> None:
        dirname = os.path.dirname(file_path)
        os.makedirs(dirname, exist_ok=True)
        with open(file_path, 'w') as out:
            if isinstance(summary, list):
                for sentence in summary:
                    out.write(sentence + '\n')
            else:
                out.write(summary)

    def _save_config_file(self,
                          config_filename: str,
                          summary_filenames_list: List[List[str]],
                          reference_filenames_list: List[List[str]]):
        output_dir = os.path.dirname(config_filename)
        with open(config_filename, 'w') as out:
            out.write(f'<ROUGE_EVAL version="1.0">\n')
            for i, (reference_filenames, summary_filenames) in enumerate(zip(reference_filenames_list, summary_filenames_list)):
                out.write(f'<EVAL ID="{i + 1}">\n')
                out.write(f'<INPUT-FORMAT TYPE="SPL"></INPUT-FORMAT>\n')
                out.write(f'<PEER-ROOT>{output_dir}</PEER-ROOT>\n')
                out.write(f'<MODEL-ROOT>{output_dir}</MODEL-ROOT>\n')
                out.write(f'<PEERS>\n')
                for j, summary_filename in enumerate(summary_filenames):
                    out.write(f'<P ID="{j + 1}">{summary_filename}</P>\n')
                out.write(f'</PEERS>\n')
                out.write(f'<MODELS>\n')
                for j, reference_filename in enumerate(reference_filenames):
                    symbol = chr(j + 65)
                    out.write(f'<M ID="{symbol}">{reference_filename}</M>\n')
                out.write(f'</MODELS>\n')
                out.write(f'</EVAL>\n')
            out.write(f'</ROUGE_EVAL>\n')

    def _parse_average_line(self, columns: List[str]) -> Tuple[str, str, float, float, float]:
        assert len(columns) == 8
        if columns[2][-2] == 'R':
            metric = 'recall'
        elif columns[2][-2] == 'P':
            metric = 'precision'
        elif columns[2][-2] == 'F':
            metric = 'f1'
        else:
            raise Exception(f'Unknown metric: {columns[2]}')

        summarizer_id = int(columns[0]) - 1
        value = float(columns[3]) * 100
        lower_ci = float(columns[5]) * 100
        upper_ci = float(columns[7][:-1]) * 100
        return summarizer_id, metric, value, lower_ci, upper_ci

    def _parse_individual_line(self, columns: List[str]) -> Tuple[int, int, float, float, float]:
        assert len(columns) == 7
        period = columns[3].index('.')
        instance_id = int(columns[3][:period]) - 1
        summarizer_id = int(columns[3][period + 1:]) - 1
        recall = float(columns[4][2:]) * 100
        precision = float(columns[5][2:]) * 100
        f1 = float(columns[6][2:]) * 100
        return instance_id, summarizer_id, recall, precision, f1

    def _parse_rouge_stdout(self, stdout: str):
        lines = stdout.splitlines()
        macro_metrics_dict = defaultdict(lambda: defaultdict(MetricsDict))
        micro_metrics_dicts = defaultdict(lambda: defaultdict(MetricsDict))
        for line in lines:
            if line in ['---------------------------------------------', '.............................................']:
                continue
            columns = line.split()
            rouge_metric = columns[1].lower()
            if columns[2] == 'Eval':
                instance_id, summarizer_id, recall, precision, f1 = self._parse_individual_line(columns)
                micro_metrics_dicts[instance_id][summarizer_id][rouge_metric] = {
                    'recall': recall,
                    'precision': precision,
                    'f1': f1
                }
            else:
                summarizer_id, metric, value, lower_ci, upper_ci = self._parse_average_line(columns)
                macro_metrics_dict[summarizer_id][rouge_metric][metric] = value

        # Flatten the metrics into arrays instead of dicts
        macro_metrics_list = [None] * len(macro_metrics_dict)
        for summarizer_id, metrics in macro_metrics_dict.items():
            macro_metrics_list[summarizer_id] = metrics

        micro_metrics_lists = [None] * len(micro_metrics_dicts)
        for instance_id, metrics_dict in micro_metrics_dicts.items():
            micro_metrics_lists[instance_id] = [None] * len(metrics_dict)
            for summarizer_id, metrics in metrics_dict.items():
                micro_metrics_lists[instance_id][summarizer_id] = metrics
        return macro_metrics_list, micro_metrics_lists

    def _run(self,
             summaries_list: List[List[SummaryType]],
             references_list: List[List[SummaryType]]) -> Tuple[List[MetricsDict], List[List[MetricsDict]]]:
        with TemporaryDirectory() as temp_dir:
            summary_filenames_list = []
            reference_filenames_list = []

            for i, (summaries, references) in enumerate(zip(summaries_list, references_list)):
                summary_filenames_list.append([])
                reference_filenames_list.append([])
                for j, summary in enumerate(summaries):
                    summary_filename = f'{i}/model.{j}.txt'
                    summary_filenames_list[-1].append(summary_filename)
                    self._save_summary(summary, f'{temp_dir}/{summary_filename}')

                for j, reference in enumerate(references):
                    symbol = chr(j + 65)
                    reference_filename = f'{i}/gold.{symbol}.txt'
                    reference_filenames_list[-1].append(reference_filename)
                    self._save_summary(reference, f'{temp_dir}/{reference_filename}')

            config_filename = f'{temp_dir}/config.xml'
            self._save_config_file(config_filename, summary_filenames_list, reference_filenames_list)

            command = [
                self.rouge_script_location,
                '-e', self.rouge_eval_home,
                '-n', str(self.max_ngram),
                '-a',
                '-c', '95',
                '-r', '1000',
                '-p', '0.5',
                '-t', '0',
                '-d'
            ]
            if self.use_porter_stemmer:
                command += ['-m']
            if self.remove_stopwords:
                command += ['-s']
            if self.max_bytes is not None:
                command += ['-b', str(self.max_bytes)]
            if self.max_words is not None:
                command += ['-l', str(self.max_words)]
            if not self.compute_rouge_l:
                command += ['-x']
            if self.skip_bigram_gap_length is not None:
                command += ['-2', str(self.skip_bigram_gap_length), '-u']
            if self.wlcs_weight is not None:
                command += ['-w', str(self.wlcs_weight)]
            if self.scoring_function == 'average':
                command += ['-f', 'A']
            elif self.scoring_function == 'max':
                command += ['-f', 'B']
            else:
                raise Exception(f'Unrecognized scoring function: "{self.scoring_function}"')
            command += [config_filename]

            # We used to fail if anything was written to stderr, but ROUGE writes
            # a warning if the number of peers per reference set is different, which
            # is expected in some situations for us (if we just have more summaries
            # to score for some reference sets than others). Therefore, we no longer fail
            # if stderr is not empty.
            logger.info(f'Running ROUGE command: "{" ".join(command)}"')
            process = Popen(command, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()

            macro_metrics_list, micro_metrics_lists = self._parse_rouge_stdout(stdout.decode())
            return macro_metrics_list, micro_metrics_lists

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[ReferenceType]]) -> List[List[MetricsDict]]:
        _, micro_metrics_lists = self._run(summaries_list, references_list)
        return micro_metrics_lists

    def evaluate(self,
                 summaries: List[SummaryType],
                 references_list: List[List[ReferenceType]]) -> Tuple[MetricsDict, List[MetricsDict]]:
        summaries_list = [[summary] for summary in summaries]
        macro_metrics_list, micro_metrics_lists = self._run(summaries_list, references_list)

        macro_metrics = macro_metrics_list[0]
        micro_metrics_list = [metrics_list[0] for metrics_list in micro_metrics_lists]
        return macro_metrics, micro_metrics_list


class RougeSetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the ROUGE metric'
        self.parser = parser.add_parser('rouge', description=description, help=description)
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        print(f'Downloading ROUGE-1.5.5')
        download_file_from_google_drive('1y0rDnTplQ83b2PQu_TgezbFpGOthP0gG', f'{DATA_ROOT}/metrics/ROUGE-1.5.5.zip')

        commands = [
            f'cd {DATA_ROOT}/metrics',
            f'unzip ROUGE-1.5.5.zip',
            f'rm ROUGE-1.5.5.zip'
        ]
        command = ' && '.join(commands)

        process = Popen(command, shell=True)
        process.communicate()
        if process.returncode != 0:
            print('ROUGE setup failure')

        # ROUGE has data files which may not successfully load (I think this might be platform-dependent, but
        # I have never verified this). Therefore, if it fails to run on a simple example, the user needs to
        # run some perl code within the ROUGE directory to correct the data file
        try:
            summary = 'Dan walked to the bakery this morning.'
            reference = 'Dan went to buy scones earlier this morning.'
            rouge = Rouge()
            rouge.score(summary, [reference])
            print('ROUGE setup success')
        except IndexError:
            print('ROUGE setup failure')
            print('It is very likely that you need to rebuild the ROUGE database file. See '
                  'https://github.com/danieldeutsch/sacrerouge/blob/master/doc/metrics/rouge.md for '
                  'instructions on how to rebuild the necessary file. Afterward, this example '
                  'should run without failing:')
            print()
            print('>>> from sacrerouge.metrics import Rouge')
            print('>>> ')
            print('>>> summary = "Dan walked to the bakery this morning."')
            print('>>> reference = "Dan went to buy scones earlier this morning."')
            print('>>> ')
            print('>>> rouge = Rouge()')
            print('>>> rouge.score(summary, [reference])')
