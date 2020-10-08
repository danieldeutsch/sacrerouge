from typing import Any, Dict, List, Tuple

from sacrerouge.common.util import download_url_to_file
from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlReader, JsonlWriter


def download_human_judgments(output_dir: str, force: bool) -> str:
    url = 'https://storage.googleapis.com/sfr-summarization-repo-research/model_annotations.aligned.jsonl'
    file_path = f'{output_dir}/model_annotations.aligned.jsonl'
    download_url_to_file(url, file_path, force)
    return file_path


def load_judgments(file_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Metrics]]:
    summaries = []
    summaries_with_crowd = []
    metrics_list = []

    with JsonlReader(file_path) as f:
        for instance in f:
            instance_id = instance['id']
            summarizer_id = instance['model_id']
            filename = instance['filepath']
            summary = {'text': instance['decoded']}
            references = instance['references']
            expert_annotations = instance['expert_annotations']
            turker_annotations = instance['turker_annotations']

            # It appears that the first reference is always the ground-truth, the others are crowdsourced
            assert len(references) == 11
            references[0] = {
                'summarizer_id': 'ground-truth',
                'summarizer_type': 'reference',
                'text': references[0]
            }
            for i in range(1, 11):
                references[i] = {
                    'summarizer_id': f'turker-{i}',
                    'summarizer_type': 'reference',
                    'text': references[i]
                }

            summaries.append({
                'instance_id': instance_id,
                'summarizer_id': summarizer_id,
                'summarizer_type': 'peer',
                'file_path': filename,
                'summary': summary,
                'references': [references[0]]
            })
            summaries_with_crowd.append({
                'instance_id': instance_id,
                'summarizer_id': summarizer_id,
                'summarizer_type': 'peer',
                'file_path': filename,
                'summary': summary,
                'references': references
            })

            expert_metrics = MetricsDict({
                'coherence': [annotation['coherence'] for annotation in expert_annotations],
                'consistency': [annotation['consistency'] for annotation in expert_annotations],
                'fluency': [annotation['fluency'] for annotation in expert_annotations],
                'relevance': [annotation['relevance'] for annotation in expert_annotations]
            })
            turker_metrics = MetricsDict({
                'coherence': [annotation['coherence'] for annotation in turker_annotations],
                'consistency': [annotation['consistency'] for annotation in turker_annotations],
                'fluency': [annotation['fluency'] for annotation in turker_annotations],
                'relevance': [annotation['relevance'] for annotation in turker_annotations]
            })
            both = MetricsDict({
                'expert': expert_metrics,
                'turker': turker_metrics
            })
            metrics = Metrics(instance_id, summarizer_id, 'peer', both)
            metrics_list.append(metrics)

    return summaries, summaries_with_crowd, metrics_list


def save_data(data: List[Any], file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for item in data:
            out.write(item)


def setup(output_dir: str, force: bool) -> None:
    judgments_file = download_human_judgments(f'{output_dir}/raw', force)
    summaries, summaries_with_crowd, metrics = load_judgments(judgments_file)

    save_data(summaries, f'{output_dir}/summaries.jsonl')
    save_data(summaries_with_crowd, f'{output_dir}/summaries-with-crowd.jsonl')
    save_data(metrics, f'{output_dir}/metrics.jsonl')