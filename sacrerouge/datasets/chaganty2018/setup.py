import json
import os
import tarfile
import urllib.request
from collections import defaultdict

from sacrerouge.io import JsonlReader, JsonlWriter


def download_raw_data(output_dir: str) -> None:
    urls = [
        'https://worksheets.codalab.org/rest/bundles/0x8dabd302e6674c65b0098a2a258fffb2/contents/blob/',
        'https://worksheets.codalab.org/rest/bundles/0x6c53667688d74786aaba63ba3bcc8e0e/contents/blob/',
        'https://worksheets.codalab.org/rest/bundles/0x57d766e803fe4e00882d58fabf9e6101/contents/blob/'
    ]
    paths = [
        f'{output_dir}/raw/articles.jsonl',
        f'{output_dir}/raw/data.tar.gz',
        f'{output_dir}/raw/lqual.jsonl'  # The output from running their "process.py lqual" script, not the file in the "data" folder
    ]

    os.makedirs(f'{output_dir}/raw', exist_ok=True)
    for url, path in zip(urls, paths):
        if os.path.exists(path):
            print(f'Skipping downloading {path}')
        else:
            urllib.request.urlretrieve(url, path)


def setup_documents(output_dir: str):
    with JsonlReader(f'{output_dir}/raw/articles.jsonl') as f:
        with JsonlWriter(f'{output_dir}/documents.jsonl') as out:
            for instance in f:
                instance_id = instance['id']
                text = instance['text']
                out.write({
                    'instance_id': instance_id,
                    'documents': [
                        {'text': text}
                    ]
                })


def load_metrics(output_dir: str):
    metrics_dicts = defaultdict(dict)
    with JsonlReader(f'{output_dir}/raw/lqual.jsonl') as f:
        for instance in f:
            instance_id = instance['id']
            summarizer_id = instance['system']

            # The 'human' field is the list of individual annotations, the
            # 'gold' field is their average, which we don't need
            hter = instance['prompts']['hter']['human']
            overall = instance['prompts']['overall']['human']
            grammar = instance['prompts']['grammar']['human']
            redundancy = instance['prompts']['redundancy']['human']

            # The automatic metrics are identical for all prompts
            metrics_dicts[instance_id][summarizer_id] = {
                'hter': hter,
                'overall': overall,
                'grammar': grammar,
                'redundancy': redundancy,
                'bleu-2': instance['prompts']['hter']['bleu-2'],
                'bleu-4': instance['prompts']['hter']['bleu-4'],
                'meteor': instance['prompts']['hter']['meteor'],
                'ter': instance['prompts']['hter']['ter'],
                'sim': instance['prompts']['hter']['sim'],
                'rouge-1': {'recall': instance['prompts']['hter']['ROUGE-1']},
                'rouge-2': {'recall': instance['prompts']['hter']['ROUGE-2']},
                'rouge-3': {'recall': instance['prompts']['hter']['ROUGE-3']},
                'rouge-4': {'recall': instance['prompts']['hter']['ROUGE-4']},
                'rouge-l': {'recall': instance['prompts']['hter']['ROUGE-L']},
                'rouge-su4': {'recall': instance['prompts']['hter']['ROUGE-SU4']}
            }
        return metrics_dicts


def load_summaries(output_dir: str):
    summaries = defaultdict(dict)
    with tarfile.open(f'{output_dir}/raw/data.tar.gz', 'r') as tar:
        lines = tar.extractfile('./lqual.jsonl').read().decode().splitlines()
        for line in lines:
            data = json.loads(line)
            instance_id = data['input']['contents']['id']
            text = data['input']['contents']['text']

            for summarizer_id in data['input']['contents']['system'].split(';'):
                if summarizer_id == 'reference':
                    summarizer_type = 'reference'
                else:
                    summarizer_type = 'peer'

                summary = {
                    'summarizer_id': summarizer_id,
                    'summarizer_type': summarizer_type,
                    'text': text
                }
                summaries[instance_id][summarizer_id] = summary
    return summaries


def save_data(summaries, metrics_dicts, output_dir: str):
    with JsonlWriter(f'{output_dir}/summaries.jsonl') as out_summaries:
        with JsonlWriter(f'{output_dir}/metrics.jsonl') as out_metrics:
            for instance_id in sorted(metrics_dicts.keys()):
                for summarizer_id in sorted(metrics_dicts[instance_id].keys()):
                    summary = summaries[instance_id][summarizer_id]
                    metrics = metrics_dicts[instance_id][summarizer_id]

                    if summary['summarizer_type'] == 'reference':
                        references = []
                    else:
                        references = [summaries[instance_id]['reference']]

                    out_summaries.write({
                        'instance_id': instance_id,
                        'summarizer_id': summarizer_id,
                        'summarizer_type': summary['summarizer_type'],
                        'summary': summary,
                        'references': references
                    })
                    out_metrics.write({
                        'instance_id': instance_id,
                        'summarizer_id': summarizer_id,
                        'summarizer_type': summary['summarizer_type'],
                        'metrics': {
                            'chaganty2018': metrics
                        }
                    })


def setup(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    download_raw_data(output_dir)
    setup_documents(output_dir)

    metrics_dicts = load_metrics(output_dir)
    summaries = load_summaries(output_dir)
    save_data(summaries, metrics_dicts, output_dir)
