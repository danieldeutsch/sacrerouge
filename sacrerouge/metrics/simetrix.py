import os
from collections import defaultdict
from subprocess import Popen, PIPE
from typing import List, Tuple

from sacrerouge.common import TemporaryDirectory
from sacrerouge.data import MetricsDict
from sacrerouge.data.types import SummaryType
from sacrerouge.metrics import Metric


@Metric.register('simetrix')
class SIMetrix(Metric):
    def __init__(self,
                 use_stemmer: bool = True,
                 remove_stopwords: bool = True,
                 jar_path: str = 'external/SIMetrix/simetrix.jar',
                 data_dir: str = 'external/SIMetrix/data'):
        super().__init__(['documents'], False)
        self.use_stemmer = use_stemmer
        self.remove_stopwords = remove_stopwords
        self.jar_path = jar_path
        self.data_dir = data_dir

    def _save_summary_like(self, summary: SummaryType, file_path: str) -> None:
        dirname = os.path.dirname(file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(file_path, 'w') as out:
            if isinstance(summary, list):
                out.write('\n'.join(summary))
            else:
                out.write(summary)

    def _parse_macro_file(self, file_path: str) -> List[MetricsDict]:
        metrics_dict = {}
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                columns = line.split()
                if i == 0:
                    header = columns
                else:
                    index = int(columns[0])
                    metrics = MetricsDict()
                    for j, name in enumerate(header[1:]):
                        # All the names begin with "Avg"
                        name = name[3:]
                        metrics[name] = float(columns[j + 1])
                    metrics_dict[index] = metrics

        # Sort and return a list according to the index
        metrics_list = []
        for index in sorted(metrics_dict.keys()):
            assert index == len(metrics_list)
            metrics_list.append(metrics_dict[index])
        return metrics_list

    def _parse_micro_file(self, file_path: str) -> List[List[MetricsDict]]:
        metrics_dicts = defaultdict(dict)
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                columns = line.split()
                if i == 0:
                    header = columns
                else:
                    instance_index = int(columns[0])
                    system_index = int(columns[1])
                    metrics = MetricsDict()
                    for j, name in enumerate(header[2:]):
                        metrics[name] = float(columns[j + 2])
                    metrics_dicts[instance_index][system_index] = metrics

        # Sort and return a list according to the index
        metrics_lists = [None] * len(metrics_dicts)
        for instance_index in sorted(metrics_dicts.keys()):
            metrics_dict = metrics_dicts[instance_index]
            metrics_lists[instance_index] = [None] * len(metrics_dict)
            for system_index in sorted(metrics_dict.keys()):
                metrics_lists[instance_index][system_index] = metrics_dict[system_index]
        return metrics_lists

    def _run(self,
             summaries_list: List[List[SummaryType]],
             documents_list: List[List[str]]) -> Tuple[List[MetricsDict], List[List[MetricsDict]]]:
        with TemporaryDirectory() as temp_dir:
            mappings_file_path = f'{temp_dir}/mappings.txt'
            with open(mappings_file_path, 'w') as out:
                for i, (summaries, documents) in enumerate(zip(summaries_list, documents_list)):
                    document_dir = f'{temp_dir}/documents/{i}'
                    for j, document in enumerate(documents):
                        document_file_path = f'{document_dir}/{j}.txt'
                        self._save_summary_like(document, document_file_path)

                    for j, summary in enumerate(summaries):
                        summary_file_path = f'{temp_dir}/summaries/{i}-{j}.txt'
                        self._save_summary_like(summary, summary_file_path)

                        out.write(f'{i} {j} {document_dir} {summary_file_path}\n')

            config_file_path = f'{temp_dir}/config'
            with open(config_file_path, 'w') as out:
                perform_stemming = 'Y' if self.use_stemmer else 'N'
                out.write(f'performStemming = {perform_stemming}\n')

                remove_stopwords = 'Y' if self.remove_stopwords else 'N'
                out.write(f'removeStopWords = {remove_stopwords}\n')
                out.write(f'stopFilePath = {self.data_dir}/smart_common_words.txt\n')

                out.write(f'divergence = Y\n')
                out.write(f'frequencyFeatures = Y\n')
                out.write(f'cosineOverlap = Y\n')
                out.write(f'topicWordFeatures = Y\n')
                out.write(f'backgroundCorpusFreqCounts = {self.data_dir}/bgFreqCounts.unstemmed.txt\n')
                out.write(f'backgroundIdfUnstemmed = {self.data_dir}/bgIdfValues.unstemmed.txt\n')
                out.write(f'backgroundIdfStemmed = {self.data_dir}/bgIdfValues.stemmed.txt\n')

            command = [
                'java',
                '-cp', self.jar_path,
                'edu.upenn.seas.simetrix.InputBasedEvaluation',
                mappings_file_path,
                config_file_path
            ]

            process = Popen(command, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            if stderr:
                raise Exception(f'SIMetrix failed with stderr: {stderr.decode()}')

            macro_results = self._parse_macro_file(f'{temp_dir}/mappings.txt.ieval.macro')
            micro_results = self._parse_micro_file(f'{temp_dir}/mappings.txt.ieval.micro')
            return macro_results, micro_results

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        documents_list: List[List[str]]) -> List[List[MetricsDict]]:
        _, micro_metrics_lists = self._run(summaries_list, documents_list)
        return micro_metrics_lists

    def evaluate(self,
                 summaries: List[List[SummaryType]],
                 documents_list: List[List[SummaryType]]) -> Tuple[MetricsDict, List[MetricsDict]]:
        summaries_list = [[summary] for summary in summaries]
        macro_metrics_list, micro_metrics_lists = self._run(summaries_list, documents_list)

        macro_metrics = macro_metrics_list[0]
        micro_metrics_list = [metrics_list[0] for metrics_list in micro_metrics_lists]
        return macro_metrics, micro_metrics_list
