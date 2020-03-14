import os
from subprocess import Popen, PIPE
from typing import List, Tuple

from sacrerouge.common import TemporaryDirectory
from sacrerouge.common.util import average_metrics
from sacrerouge.data.types import MetricsType, SummaryType
from sacrerouge.metrics import Metric


@Metric.register('simetrix')
class SIMetrix(Metric):
    def __init__(self,
                 use_stemmer: bool = True,
                 remove_stopwords: bool = True,
                 jar_path: str = 'external/SIMetrix/simetrix.jar',
                 data_dir: str = 'external/SIMetrix/data'):
        super().__init__()
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

    def _parse_micro_file(self, file_path: str):
        metrics_dict = {}
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                columns = line.split()
                if i == 0:
                    header = columns
                else:
                    index = int(columns[0])
                    metrics = {}
                    for j, name in enumerate(header[2:]):
                        metrics[name] = float(columns[j + 2])
                    metrics_dict[index] = metrics

        # Sort and return a list according to the index
        metrics_list = []
        for index in sorted(metrics_dict.keys()):
            assert index == len(metrics_list)
            metrics_list.append(metrics_dict[index])
        return metrics_list

    def score_all(self,
                  summaries: List[SummaryType],
                  documents_list: List[List[str]]) -> Tuple[MetricsType, List[MetricsType]]:
        with TemporaryDirectory() as temp_dir:
            mappings_file_path = f'{temp_dir}/mappings.txt'
            with open(mappings_file_path, 'w') as out:
                for i, (summary, documents) in enumerate(zip(summaries, documents_list)):
                    summary_file_path = f'{temp_dir}/summaries/{i}.txt'
                    self._save_summary_like(summary, summary_file_path)

                    document_dir = f'{temp_dir}/documents/{i}'
                    for j, document in enumerate(documents):
                        document_file_path = f'{document_dir}/{j}.txt'
                        self._save_summary_like(document, document_file_path)

                    out.write(f'{i} {i} {document_dir} {summary_file_path}\n')

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

            individual_results = self._parse_micro_file(f'{temp_dir}/mappings.txt.ieval.micro')
            aggregated_results = average_metrics(individual_results)
            return aggregated_results, individual_results
