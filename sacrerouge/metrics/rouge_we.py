import atexit
import os
import requests
import time
from collections import defaultdict
from subprocess import Popen, PIPE
from typing import Any, Dict, List, Optional, Tuple

from sacrerouge.common import TemporaryDirectory
from sacrerouge.data.types import MetricsType, SummaryType
from sacrerouge.metrics import Metric


@Metric.register('rouge-we')
class RougeWE(Metric):
    def __init__(self,
                 max_ngram: int = 4,
                 use_porter_stemmer: bool = True,
                 remove_stopwords: bool = False,
                 max_bytes: Optional[int] = None,
                 max_words: Optional[int] = None,
                 compute_rouge_l: bool = False,
                 skip_bigram_gap_length: Optional[int] = None,
                 wlcs_weight: Optional[float] = None,
                 rouge_we_script_location: str = 'external/ROUGE-WE/rouge-we/ROUGE-WE-1.0.0.pl',
                 rouge_we_data_dir: str = 'external/ROUGE-WE/rouge-we/rouge_1.5.5_data',
                 word_vectors_server_script: str = 'external/ROUGE-WE/rouge-we/word2vec_server.m.py',
                 word_vectors_file: str = 'external/ROUGE-WE/GoogleNews-vectors-negative300.bin.gz',
                 environment_name: str = 'rouge-we'):
        super().__init__()
        self.max_ngram = max_ngram
        self.use_porter_stemmer = use_porter_stemmer
        self.remove_stopwords = remove_stopwords
        self.max_bytes = max_bytes
        self.max_words = max_words
        self.compute_rouge_l = compute_rouge_l
        self.skip_bigram_gap_length = skip_bigram_gap_length
        self.wlcs_weight = wlcs_weight
        self.rouge_we_script_location = rouge_we_script_location
        self.rouge_we_data_dir = rouge_we_data_dir
        self.word_vectors_server_script = word_vectors_server_script
        self.word_vectors_file = word_vectors_file
        self.environment_name = environment_name

    def _start_server(self, retry_interval: int = 5, timeout: int = 300):
        conda_command = f'source activate {self.environment_name}'
        run_command = f'python {self.word_vectors_server_script} -m {self.word_vectors_file}'
        command = f'{conda_command} && {run_command}'

        # Start the subprocess and repeatedly try to ping it to see if it's ready
        process = Popen(command, shell=True)

        def _kill_server():
            process.kill()
        atexit.register(_kill_server)

        start = time.time()
        while True:
            try:
                requests.get('http://localhost:8888/word2vecdiff')
                return
            except requests.exceptions.ConnectionError:
                time.sleep(retry_interval)
                elapsed = time.time() - start
                if elapsed >= timeout:
                    break

        raise Exception('Unable to start ROUGE-WE server')

    def _save_summary(self, summary: SummaryType, file_path: str) -> None:
        with open(file_path, 'w') as out:
            if isinstance(summary, list):
                out.write('\n'.join(summary))
            else:
                out.write(summary)

    def _save_config_file(self,
                          config_filename: str,
                          summary_filenames: List[str],
                          reference_filenames_list: List[List[str]]):
        output_dir = os.path.dirname(config_filename)
        with open(config_filename, 'w') as out:
            out.write(f'<ROUGE_EVAL version="1.0">\n')
            for i, (reference_filenames, summary_filename) in enumerate(zip(reference_filenames_list, summary_filenames)):
                out.write(f'<EVAL ID="{i + 1}">\n')
                out.write(f'<INPUT-FORMAT TYPE="SPL"></INPUT-FORMAT>\n')
                out.write(f'<PEER-ROOT>{output_dir}</PEER-ROOT>\n')
                out.write(f'<MODEL-ROOT>{output_dir}</MODEL-ROOT>\n')
                out.write(f'<PEERS>\n')
                out.write(f'<P ID="1">{summary_filename}</P>\n')
                out.write(f'</PEERS>\n')
                out.write(f'<MODELS>\n')
                for j, reference_filename in enumerate(reference_filenames):
                    symbol = chr(j + 65)
                    out.write(f'<M ID="{symbol}">{reference_filename}</M>\n')
                out.write(f'</MODELS>\n')
                out.write(f'</EVAL>\n')
            out.write(f'</ROUGE_EVAL>\n')

    def _parse_rouge_average_line(self, columns: List[str]) -> Tuple[str, float, float, float]:
        assert len(columns) == 8
        if columns[2][-2] == 'R':
            metric = 'recall'
        elif columns[2][-2] == 'P':
            metric = 'precision'
        elif columns[2][-2] == 'F':
            metric = 'f1'
        else:
            raise Exception(f'Unknown metric: {columns[2]}')

        value = float(columns[3])
        lower_ci = float(columns[5])
        upper_ci = float(columns[7][:-1])
        return metric, value, lower_ci, upper_ci

    def _parse_individual_line(self, columns: List[str]) -> Tuple[int, float, float, float]:
        assert len(columns) == 7
        index = int(columns[3][:-2]) - 1
        recall = float(columns[4][2:])
        precision = float(columns[5][2:])
        f1 = float(columns[6][2:])
        return index, recall, precision, f1

    def _parse_rouge_stdout(self, stdout: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        lines = stdout.splitlines()
        aggregate_metrics = defaultdict(dict)
        index_to_individual_metrics = defaultdict(dict)
        for line in lines:
            if line in ['---------------------------------------------', '.............................................']:
                continue
            columns = line.split()
            rouge_metric = columns[1].lower()
            if columns[2] == 'Eval':
                index, recall, precision, f1 = self._parse_individual_line(columns)
                index_to_individual_metrics[index][rouge_metric] = {
                    'recall': recall * 100,
                    'precision': precision * 100,
                    'f1': f1 * 100
                }
            else:
                metric, value, _, _ = self._parse_rouge_average_line(columns)
                aggregate_metrics[rouge_metric][metric] = value * 100

        individual_metrics = [None] * len(index_to_individual_metrics)
        for index, metrics in index_to_individual_metrics.items():
            individual_metrics[index] = metrics

        return aggregate_metrics, individual_metrics

    def score_all(self,
                  summaries: List[SummaryType],
                  references_list: List[List[SummaryType]]) -> Tuple[MetricsType, List[MetricsType]]:
        # It is faster and easier to run ROUGE on the entire set and extract
        # the individual scores than it is to run ROUGE on each individual instance
        # and then aggregate the metrics. Therefore, we override `score_all` and
        # make `score` call `score_all`.
        self._start_server()

        with TemporaryDirectory() as temp_dir:
            summary_filenames = []
            reference_filenames_list = []

            for i, (summary, references) in enumerate(zip(summaries, references_list)):
                summary_filename = f'model.{i}.txt'
                summary_filenames.append(summary_filename)
                self._save_summary(summary, f'{temp_dir}/{summary_filename}')

                reference_filenames = []
                for j, reference in enumerate(references):
                    symbol = chr(j + 65)
                    reference_filename = f'gold.{symbol}.{i}.txt'
                    reference_filenames.append(reference_filename)
                    self._save_summary(reference, f'{temp_dir}/{reference_filename}')
                reference_filenames_list.append(reference_filenames)

                config_filename = f'{temp_dir}/config.xml'
                self._save_config_file(config_filename, summary_filenames, reference_filenames_list)

            command = [
                self.rouge_we_script_location,
                '-e', self.rouge_we_data_dir,
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

            aggregate_metrics, individual_metrics = self._parse_rouge_stdout(stdout.decode())
            return aggregate_metrics, individual_metrics

    def score(self,
              summary: SummaryType,
              references: List[SummaryType]) -> MetricsType:
        return self.score_all([summary], [references])[0]
