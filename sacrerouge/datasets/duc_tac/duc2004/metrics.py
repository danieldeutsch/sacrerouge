import tarfile
from collections import defaultdict
from io import BytesIO
from nltk.tokenize import sent_tokenize
from typing import Dict, List

from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlWriter


def load_task1_summaries(results_tar: str):
    summaries = defaultdict(lambda: defaultdict(dict))

    with tarfile.open(results_tar, 'r') as tar:
        for inner_tar_path in ['duc2004_results/ROUGE/duc2004.task1.ROUGE.peers.tar.gz', 'duc2004_results/ROUGE/duc2004.task1.ROUGE.models.tar.gz']:
            inner_tar_bytes = tar.extractfile(inner_tar_path).read()
            with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
                for member in inner_tar.getmembers():
                    if member.isfile():
                        path = member.name.split('/')
                        parts = path[-1].split('.')

                        filename = parts[5] + '.' + parts[6]
                        summarizer_id = parts[4]
                        if summarizer_id.isalpha():
                            summarizer_type = 'reference'
                        else:
                            summarizer_type = 'peer'

                        text = [inner_tar.extractfile(member).read().decode().strip()]
                        summary = {
                            'summarizer_id': summarizer_id,
                            'summarizer_type': summarizer_type,
                            'text': text
                        }
                        summaries[filename][summarizer_id] = summary
    return summaries


def load_task2_summaries(results_tar: str):
    summaries = defaultdict(lambda: defaultdict(dict))

    with tarfile.open(results_tar, 'r') as tar:
        for inner_tar_path in ['duc2004_results/ROUGE/duc2004.task2.ROUGE.peers.tar.gz', 'duc2004_results/ROUGE/duc2004.task2.ROUGE.models.tar.gz']:
            inner_tar_bytes = tar.extractfile(inner_tar_path).read()
            with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
                for member in inner_tar.getmembers():
                    if member.isfile():
                        path = member.name.split('/')
                        parts = path[-1].split('.')

                        instance_id = parts[0].lower()
                        summarizer_id = parts[4]
                        if summarizer_id.isalpha():
                            summarizer_type = 'reference'
                        else:
                            summarizer_type = 'peer'

                        lines = inner_tar.extractfile(member).read().decode().splitlines()
                        sentences = []
                        for line in lines:
                            for sentence in sent_tokenize(line):
                                sentences.append(sentence)

                        summary = {
                            'summarizer_id': summarizer_id,
                            'summarizer_type': summarizer_type,
                            'text': sentences
                        }
                        summaries[instance_id][summarizer_id] = summary
    return summaries


def load_task3_summaries(results_tar: str):
    summaries = defaultdict(lambda: defaultdict(dict))

    with tarfile.open(results_tar, 'r') as tar:
        for inner_tar_path in ['duc2004_results/ROUGE/duc2004.task3.ROUGE.peers.tar.gz', 'duc2004_results/ROUGE/duc2004.task3.ROUGE.models.tar.gz']:
            inner_tar_bytes = tar.extractfile(inner_tar_path).read()
            with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
                for member in inner_tar.getmembers():
                    if member.isfile():
                        path = member.name.split('/')
                        parts = path[-1].split('.')

                        filename = parts[5] + '.' + parts[6] + '.' + parts[7]
                        summarizer_id = parts[4]
                        if summarizer_id.isalpha():
                            summarizer_type = 'reference'
                        else:
                            summarizer_type = 'peer'

                        text = [inner_tar.extractfile(member).read().decode().strip()]
                        summary = {
                            'summarizer_id': summarizer_id,
                            'summarizer_type': summarizer_type,
                            'text': text
                        }
                        summaries[filename][summarizer_id] = summary
    return summaries


def load_task4_summaries(results_tar: str):
    summaries = defaultdict(lambda: defaultdict(dict))

    with tarfile.open(results_tar, 'r') as tar:
        for inner_tar_path in ['duc2004_results/ROUGE/duc2004.task4.ROUGE.peers.tar.gz', 'duc2004_results/ROUGE/duc2004.task4.ROUGE.models.tar.gz']:
            inner_tar_bytes = tar.extractfile(inner_tar_path).read()
            with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
                for member in inner_tar.getmembers():
                    if member.isfile():
                        path = member.name.split('/')
                        parts = path[-1].split('.')

                        instance_id = parts[0].lower()
                        summarizer_id = parts[4]
                        if summarizer_id.isalpha():
                            summarizer_type = 'reference'
                        else:
                            summarizer_type = 'peer'

                        lines = inner_tar.extractfile(member).read().decode(errors='replace').splitlines()
                        sentences = []
                        for line in lines:
                            for sentence in sent_tokenize(line):
                                sentences.append(sentence)

                        summary = {
                            'summarizer_id': summarizer_id,
                            'summarizer_type': summarizer_type,
                            'text': sentences
                        }
                        summaries[instance_id][summarizer_id] = summary
    return summaries


def load_task5_summaries(results_tar: str):
    summaries = defaultdict(lambda: defaultdict(dict))

    with tarfile.open(results_tar, 'r') as tar:
        for inner_tar_path in ['duc2004_results/ROUGE/duc2004.task5.ROUGE.peers.tar.gz', 'duc2004_results/ROUGE/duc2004.task5.ROUGE.models.tar.gz']:
            inner_tar_bytes = tar.extractfile(inner_tar_path).read()
            with tarfile.open(fileobj=BytesIO(inner_tar_bytes)) as inner_tar:
                for member in inner_tar.getmembers():
                    if member.isfile():
                        path = member.name.split('/')
                        parts = path[-1].split('.')

                        instance_id = parts[0].lower()
                        summarizer_id = parts[4]
                        if summarizer_id.isalpha():
                            summarizer_type = 'reference'
                        else:
                            summarizer_type = 'peer'

                        lines = inner_tar.extractfile(member).read().decode(errors='replace').splitlines()
                        sentences = []
                        for line in lines:
                            for sentence in sent_tokenize(line):
                                sentences.append(sentence)

                        summary = {
                            'summarizer_id': summarizer_id,
                            'summarizer_type': summarizer_type,
                            'text': sentences
                        }
                        summaries[instance_id][summarizer_id] = summary
    return summaries


def load_see_table(results_tar: str, file_path: str, metrics):
    with tarfile.open(results_tar, 'r') as tar:
        lines = tar.extractfile(file_path).read().decode().splitlines()
        for line in lines[34:]:
            columns = line.split()
            assert len(columns) == 23

            instance_id = columns[0].lower()
            summarizer_id = columns[7]
            metrics[instance_id][summarizer_id]['peer_quality']['Q1'] = int(columns[8])
            metrics[instance_id][summarizer_id]['peer_quality']['Q2'] = int(columns[9])
            metrics[instance_id][summarizer_id]['peer_quality']['Q3'] = int(columns[10])
            metrics[instance_id][summarizer_id]['peer_quality']['Q4'] = int(columns[11])
            metrics[instance_id][summarizer_id]['peer_quality']['Q5'] = int(columns[12])
            metrics[instance_id][summarizer_id]['peer_quality']['Q6'] = int(columns[13])
            metrics[instance_id][summarizer_id]['peer_quality']['Q7'] = int(columns[14])
            metrics[instance_id][summarizer_id]['unmarked_units_related_to_subject'] = float(columns[15])
            metrics[instance_id][summarizer_id]['num_peer_units'] = int(columns[16])
            metrics[instance_id][summarizer_id]['num_marked_peer_units'] = int(columns[17])
            metrics[instance_id][summarizer_id]['num_unmarked_peer_units'] = int(columns[18])
            metrics[instance_id][summarizer_id]['num_model_units'] = int(columns[19])
            metrics[instance_id][summarizer_id]['coverage']['mean'] = float(columns[20])
            metrics[instance_id][summarizer_id]['coverage']['median'] = float(columns[21])
            metrics[instance_id][summarizer_id]['coverage']['std'] = float(columns[22])


def load_responsiveness_table(results_tar: str, metrics):
    with tarfile.open(results_tar, 'r') as tar:
        lines = tar.extractfile('duc2004_results/Responsiveness/results.table.R').read().decode().splitlines()
        for line in lines[7:]:
            columns = line.split()
            assert len(columns) == 5

            instance_id = columns[0].lower()
            summarizer_id = columns[3]
            metrics[instance_id][summarizer_id]['responsiveness'] = int(columns[4])


def get_references(summaries, instance_id, summarizer_id):
    summarizer_ids = list(summaries[instance_id].keys())
    reference_ids = list(filter(lambda sid: sid.isalpha(), summarizer_ids))

    references = []
    for reference_id in reference_ids:
        if summarizer_id == reference_id:
            continue
        references.append(summaries[instance_id][reference_id])
    return references


def save_metrics(summaries: Dict[str, Dict[str, List[str]]],
                 metrics: Dict[str, Dict[str, List[int]]],
                 task_name: str,
                 output_dir: str):
    with JsonlWriter(f'{output_dir}/{task_name}.summaries.jsonl') as out_summaries:
        with JsonlWriter(f'{output_dir}/{task_name}.metrics.jsonl') as out_metrics:
            for instance_id in sorted(summaries.keys()):
                for summarizer_id in summaries[instance_id].keys():
                    summary = summaries[instance_id][summarizer_id]
                    instance_metrics = metrics[instance_id][summarizer_id]
                    references = get_references(summaries, instance_id, summarizer_id)

                    out_summaries.write({
                        'instance_id': instance_id,
                        'summarizer_id': summarizer_id,
                        'summarizer_type': summary['summarizer_type'],
                        'summary': summary,
                        'references': references
                    })
                    out_metrics.write(Metrics(instance_id, summarizer_id, summary['summarizer_type'], instance_metrics))


def setup(data_root: str, output_dir: str) -> None:
    results_tar = f'{data_root}/scrapes/duc.nist.gov/past_duc/duc2004/duc2004_results.tgz'
    main(results_tar, output_dir)


def main(results_tar, output_dir):
    task1_summaries = load_task1_summaries(results_tar)
    task2_summaries = load_task2_summaries(results_tar)
    task3_summaries = load_task3_summaries(results_tar)
    task4_summaries = load_task4_summaries(results_tar)
    task5_summaries = load_task5_summaries(results_tar)

    # Tasks 1, 3, and 4 don't have manual judgments.
    # We decided not to parse all of the ROUGE results for the tasks because
    # it does not seem worth the effort since it can be recalculated.
    task2_metrics = defaultdict(lambda: defaultdict(MetricsDict))
    load_see_table(results_tar, 'duc2004_results/SEE/short.results.table2', task2_metrics)

    task5_metrics = defaultdict(lambda: defaultdict(MetricsDict))
    load_see_table(results_tar, 'duc2004_results/SEE/short.results.table5', task5_metrics)
    load_responsiveness_table(results_tar, task5_metrics)

    save_metrics(task2_summaries, task2_metrics, 'task2', output_dir)
    save_metrics(task5_summaries, task5_metrics, 'task5', output_dir)

