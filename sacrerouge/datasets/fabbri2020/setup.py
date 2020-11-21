import os
import shutil
import tarfile
from typing import Any, Dict, List, Tuple

from sacrerouge.common.util import download_file_from_google_drive, download_url_to_file
from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.datasets.fabbri2020.pair_data import run_pair_data
from sacrerouge.io import JsonlReader, JsonlWriter


def download_human_judgments(output_dir: str, force: bool) -> str:
    url = 'https://storage.googleapis.com/sfr-summarization-repo-research/model_annotations.aligned.jsonl'
    file_path = f'{output_dir}/model_annotations.aligned.jsonl'
    download_url_to_file(url, file_path, force)
    return file_path


def download_system_outputs(output_dir: str, force: bool) -> str:
    expanded_dir = f'{output_dir}/expanded/'
    for system_id in range(0, 24):
        url = f'https://storage.googleapis.com/sfr-summarization-repo-research/M{system_id}.tar.gz'
        file_path = f'{output_dir}/M{system_id}.tar.gz'
        download_url_to_file(url, file_path, force)

        model_expanded_dir = f'{expanded_dir}/M{system_id}'
        if os.path.exists(model_expanded_dir) and force:
            shutil.rmtree(model_expanded_dir)

        if not os.path.exists(model_expanded_dir):
            with tarfile.open(file_path, 'r') as tar:
                tar.extractall(expanded_dir)
    return expanded_dir


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
            document = instance['text']

            # It appears that the first reference is always the ground-truth, the others are crowdsourced, although
            # this is not 100% confirmed. It is only based on me looking through a handful of examples.
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
                'document': {'text': document},
                'summary': summary,
                'references': [references[0]]
            })
            summaries_with_crowd.append({
                'instance_id': instance_id,
                'summarizer_id': summarizer_id,
                'summarizer_type': 'peer',
                'file_path': filename,
                'document': {'text': document},
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


def setup_documents(cnn_tar: str, dailymail_tar: str, output_dir: str, force: bool) -> None:
    cnn_dir = f'{output_dir}/raw/cnndm/cnn'
    dm_dir = f'{output_dir}/raw/cnndm/dailymail'
    for tar_path, target_path in [(cnn_tar, cnn_dir), (dailymail_tar, dm_dir)]:
        if os.path.exists(target_path) and force:
            print(f'Removing {target_path}')
            shutil.rmtree(target_path)

        if not os.path.exists(target_path):
            print(f'Untarring {tar_path} (it\'s pretty slow...)')
            with tarfile.open(tar_path, 'r') as tar:
                tar.extractall(f'{output_dir}/raw/cnndm')


def save_data(data: List[Any], file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for item in data:
            out.write(item)


def setup(cnn_tar: str, dailymail_tar: str, output_dir: str, force: bool) -> None:
    # Download the expert and turker annotations
    download_human_judgments(f'{output_dir}/raw', force)

    # Download the system outputs
    model_output_dir = download_system_outputs(f'{output_dir}/raw/model-outputs', force)

    # Untar all of the documents
    setup_documents(cnn_tar, dailymail_tar, output_dir, force)

    # Pair together the summaries and input documents. The script will output the
    # results into "model_annotations.aligned.paired.jsonl"
    run_pair_data(data_annotations=f'{output_dir}/raw/model_annotations.aligned.jsonl',
                  model_outputs=model_output_dir,
                  story_files=f'{output_dir}/raw')

    summaries, summaries_with_crowd, metrics = load_judgments(f'{output_dir}/raw/model_annotations.aligned.paired.jsonl')
    save_data(summaries, f'{output_dir}/summaries.jsonl')
    save_data(summaries_with_crowd, f'{output_dir}/summaries-with-crowd.jsonl')
    save_data(metrics, f'{output_dir}/metrics.jsonl')

    # TODO Save all of the documents + summaries that were not judged. I'm not really sure
    # what to do with them because several of the models have different output files. We need
    # to come up with some way of distinguishing them. For instance, M5 has
    # "outputs_rouge.aligned.jsonl" and "outputs_rouge+coh.aligned.jsonl", but the "summaries.jsonl"
    # file will just mark whichever summary was judged as "M5"