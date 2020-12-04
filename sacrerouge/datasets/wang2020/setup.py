from typing import List

from sacrerouge.common.util import download_url_to_file
from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlReader, JsonlWriter


def _save_data(data: List, output_file: str) -> None:
    with JsonlWriter(output_file) as out:
        for item in data:
            out.write(item)


def _process_file(file_path: str, dataset: str, summarizer_id: str, summaries_output_file: str, metrics_output_file: str) -> None:
    instances = []
    metrics_list = []
    with JsonlReader(file_path) as f:
        for i, instance in enumerate(f):
            document = instance['article']
            summary = []
            total = 0
            for sentence in instance['summary_sentences']:
                summary.append(sentence['sentence'])
                num_yes = sum(1 if response['response'] == 'yes' else 0 for response in sentence['responses'])
                num_no = sum(1 if response['response'] == 'no' else 0 for response in sentence['responses'])
                assert num_yes + num_no == 3
                if num_yes > num_no:
                    total += 1
            score = total / len(summary)

            instance_id = f'{dataset}-{i}'
            instances.append({
                'instance_id': instance_id,
                'summarizer_id': summarizer_id,
                'summarizer_type': 'peer',
                'document': {
                    'text': document
                },
                'summary': {
                    'text': summary
                }
            })
            metrics_list.append(Metrics(instance_id, summarizer_id, 'peer', MetricsDict({'wang2020_crowd_faithfulness': score})))

    _save_data(instances, summaries_output_file)
    _save_data(metrics_list, metrics_output_file)


def setup(output_dir: str) -> None:
    cnndm_file = f'{output_dir}/mturk_cnndm.jsonl'
    xsum_file = f'{output_dir}/mturk_xsum.jsonl'
    download_url_to_file('https://raw.githubusercontent.com/W4ngatang/qags/master/data/mturk_cnndm.jsonl', cnndm_file)
    download_url_to_file('https://raw.githubusercontent.com/W4ngatang/qags/master/data/mturk_xsum.jsonl', xsum_file)

    _process_file(cnndm_file, 'cnndm', 'Gehrmann2018', f'{output_dir}/cnndm.summaries.jsonl', f'{output_dir}/cnndm.metrics.jsonl')
    _process_file(xsum_file, 'xsum', 'lewis2019', f'{output_dir}/xsum.summaries.jsonl', f'{output_dir}/xsum.metrics.jsonl')