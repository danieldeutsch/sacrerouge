import os
from collections import defaultdict
from subprocess import Popen, PIPE
from typing import List, Optional, Tuple

from sacrerouge.common import TemporaryDirectory
from sacrerouge.data import MetricsDict
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric


@Metric.register('rouge')
class Rouge(Metric):
    def __init__(self,
                 max_ngram: int = 4,
                 use_porter_stemmer: bool = True,
                 remove_stopwords: bool = False,
                 max_bytes: Optional[int] = None,
                 max_words: Optional[int] = None,
                 compute_rouge_l: bool = False,
                 skip_bigram_gap_length: Optional[int] = None,
                 wlcs_weight: Optional[float] = None,
                 rouge_script_location: str = 'external/ROUGE-1.5.5/ROUGE-1.5.5.pl',
                 rouge_eval_home: str = 'external/ROUGE-1.5.5/data'):
        super().__init__()
        self.max_ngram = max_ngram
        self.use_porter_stemmer = use_porter_stemmer
        self.remove_stopwords = remove_stopwords
        self.max_bytes = max_bytes
        self.max_words = max_words
        self.compute_rouge_l = compute_rouge_l
        self.skip_bigram_gap_length = skip_bigram_gap_length
        self.wlcs_weight = wlcs_weight
        self.rouge_script_location = rouge_script_location
        self.rouge_eval_home = rouge_eval_home

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
                '-f', 'A',
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
            command += [config_filename]

            process = Popen(command, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            if stderr:
                raise Exception(f'Rouge failed with stderr: {stderr.decode()}')

            macro_metrics_list, micro_metrics_lists = self._parse_rouge_stdout(stdout.decode())
            return macro_metrics_list, micro_metrics_lists

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[List[SummaryType]]) -> List[List[MetricsDict]]:
        _, micro_metrics_lists = self._run(summaries_list, references_list)
        return micro_metrics_lists

    def evaluate(self,
                 summaries: List[List[SummaryType]],
                 references_list: List[List[SummaryType]]) -> Tuple[MetricsDict, List[MetricsDict]]:
        summaries_list = [[summary] for summary in summaries]
        macro_metrics_list, micro_metrics_lists = self._run(summaries_list, references_list)

        macro_metrics = macro_metrics_list[0]
        micro_metrics_list = [metrics_list[0] for metrics_list in micro_metrics_lists]
        return macro_metrics, micro_metrics_list
