import json

from sacrerouge.common.util import download_url_to_file
from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlWriter


def _download_raw_data(output_dir: str, force: bool) -> None:
    download_url_to_file('https://github.com/PrimerAI/blanc/raw/master/data/CNN_DailyMail_555.json',
                         f'{output_dir}/raw/CNN_DailyMail_555.json', force=force)
    download_url_to_file('https://github.com/PrimerAI/blanc/raw/master/data/DailyNews_300.json',
                         f'{output_dir}/raw/DailyNews_300.json', force=force)
    download_url_to_file('https://github.com/PrimerAI/blanc/raw/master/data/DailyNews_300_aspects.json',
                         f'{output_dir}/raw/DailyNews_300_aspects.json', force=force)


def _load_generic_scores(input_file: str):
    data = json.load(open(input_file, 'r'))
    instances = []
    metrics_list = []
    documents = {}
    for i, instance in enumerate(data):
        document = instance['text'].strip()
        summary = instance['summary'].strip()
        scores = instance['scores']
        summarizer_id = str(i)

        if document not in documents:
            documents[document] = str(len(documents))
        instance_id = documents[document]

        instances.append({
            'instance_id': instance_id,
            'summarizer_id': summarizer_id,
            'summarizer_type': 'peer',
            'summary': {'text': summary},
            'document': {'text': document}
        })
        metrics_list.append(Metrics(instance_id, summarizer_id, 'peer', MetricsDict({'generic_quality': scores})))
    return instances, metrics_list


def _load_dailynews_aspects(input_file: str):
    data = json.load(open(input_file, 'r'))
    instances = []
    metrics_list = []
    documents = {}
    for i, instance in enumerate(data):
        document = instance['text'].strip()
        summary = instance['summary'].strip()
        fluent = instance['map_quality_scores']['Fluent']['scores']
        understandable = instance['map_quality_scores']['Understandable']['scores']
        informative = instance['map_quality_scores']['Informative']['scores']
        compact = instance['map_quality_scores']['Compact']['scores']
        overall = instance['map_quality_scores']['Overall']['scores']
        summarizer_id = str(i)

        if document not in documents:
            documents[document] = str(len(documents))
        instance_id = documents[document]

        instances.append({
            'instance_id': instance_id,
            'summarizer_id': summarizer_id,
            'summarizer_type': 'peer',
            'summary': {'text': summary},
            'document': {'text': document}
        })
        metrics_list.append(Metrics(instance_id, summarizer_id, 'peer', MetricsDict({
            'fluent': fluent,
            'understandable': understandable,
            'informative': informative,
            'compact': compact,
            'overall': overall,
        })))
    return instances, metrics_list


def _save(instances, output_file):
    with JsonlWriter(output_file) as out:
        for item in instances:
            out.write(item)


def setup(output_dir: str, force: bool) -> None:
    _download_raw_data(output_dir, force)
    cnn_dm_summaries, cnn_dm_metrics_list = _load_generic_scores(f'{output_dir}/raw/CNN_DailyMail_555.json')
    dailynews_summaries, dailynews_metrics_list = _load_generic_scores(f'{output_dir}/raw/DailyNews_300.json')
    dailynews_aspects_summaries, dailynews_aspects_metrics_list = _load_dailynews_aspects(f'{output_dir}/raw/DailyNews_300_aspects.json')

    _save(cnn_dm_summaries, f'{output_dir}/cnn-dailymail.summaries.jsonl')
    _save(cnn_dm_metrics_list, f'{output_dir}/cnn-dailymail.metrics.jsonl')

    _save(dailynews_summaries, f'{output_dir}/dailynews.summaries.jsonl')
    _save(dailynews_metrics_list, f'{output_dir}/dailynews.metrics.jsonl')

    _save(dailynews_aspects_summaries, f'{output_dir}/dailynews-aspects.summaries.jsonl')
    _save(dailynews_aspects_metrics_list, f'{output_dir}/dailynews-aspects.metrics.jsonl')
