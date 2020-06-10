import lxml.html
import os
import tarfile
from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlWriter


def load_summaries(summaries_tar: str, dirs: List[str]):
    summaries = defaultdict(dict)
    with tarfile.open(summaries_tar, 'r') as tar:
        for member in tar.getmembers():
            dirname = os.path.basename(os.path.dirname(member.name))
            if dirname in dirs and member.name.endswith('.html'):
                path = member.name.split('/')
                filename = path[-1]
                sections = filename.split('.')
                summarizer_id = sections[4]
                if summarizer_id.isalpha():
                    summarizer_type = 'reference'
                else:
                    summarizer_type = 'peer'

                # Some of these files appear to be html and others plain text
                text = tar.extractfile(member).read().decode(errors='replace')
                if text.startswith('<html>'):
                    tree = lxml.html.document_fromstring(text)
                    nodes = list(tree.xpath('//a[@id]'))
                    sentences = [node.text_content() for node in nodes]
                else:
                    sentences = text.splitlines()

                summary = {
                    'summarizer_id': summarizer_id,
                    'summarizer_type': summarizer_type,
                    'text': sentences
                }

                is_multi = sections[1] == 'M'
                if is_multi:
                    assert len(sections) == 6
                    cluster = sections[0].lower()
                    summaries[cluster][summarizer_id] = summary
                else:
                    assert len(sections) == 8
                    doc_id = '.'.join(sections[5:7])
                    summaries[doc_id][summarizer_id] = summary
    return summaries


def load_results_table(file_path: str, metrics):
    with open(file_path, 'r') as f:
        for line in f:
            columns = line.strip().split()
            assert len(columns) == 34, (len(columns), columns)
            if columns[1] == 'M':
                instance_id = columns[0].lower()
            else:
                instance_id = columns[2]

            summarizer_id = columns[8]

            summary_length = int(columns[3])
            # Length-10 summaries did not have quality questions
            if summary_length != 10:
                for i in range(12):
                    metrics[instance_id][summarizer_id]['peer_quality'][f'Q{i + 1}'] = int(columns[11 + i])

            metrics[instance_id][summarizer_id]['unmarked_units_related_to_subject'] = float(columns[23])
            metrics[instance_id][summarizer_id]['num_peer_units'] = int(columns[24])
            metrics[instance_id][summarizer_id]['num_marked_peer_units'] = int(columns[25])
            metrics[instance_id][summarizer_id]['num_unmarked_peer_units'] = int(columns[26])
            metrics[instance_id][summarizer_id]['num_model_units'] = int(columns[27])
            metrics[instance_id][summarizer_id]['coverage']['mean'] = float(columns[28])
            metrics[instance_id][summarizer_id]['coverage']['median'] = float(columns[29])
            metrics[instance_id][summarizer_id]['coverage']['std'] = float(columns[30])
            metrics[instance_id][summarizer_id]['length_adjusted_coverage']['mean'] = float(columns[31])
            metrics[instance_id][summarizer_id]['length_adjusted_coverage']['median'] = float(columns[32])
            metrics[instance_id][summarizer_id]['length_adjusted_coverage']['std'] = float(columns[33])


def load_responsiveness_table(file_path: str, metrics):
    with open(file_path, 'r') as f:
        for line in f:
            columns = line.strip().split()
            assert len(columns) == 7
            instance_id = columns[0].lower()
            summarizer_id = columns[2]
            score1 = int(columns[4])
            score2 = int(columns[6])
            metrics[instance_id][summarizer_id]['responsiveness'] = [score1, score2]


def load_usefulness_table(file_path: str, metrics):
    with open(file_path, 'r') as f:
        for line in f:
            columns = line.strip().split()
            assert len(columns) == 8
            instance_id = columns[1]
            # Annoying, the period was removed
            instance_id = instance_id[:-4] + '.' + instance_id[-4:]
            summarizer_id = columns[3]
            score1 = int(columns[5])
            score2 = int(columns[7])
            metrics[instance_id][summarizer_id]['usefulness'] = [score1, score2]


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
    results_dir = f'{data_root}/scrapes/duc.nist.gov/past_duc/duc2003/results'
    main(results_dir, output_dir)


def main(results_dir, output_dir):
    summaries_tar = f'{results_dir}/detagged.duc2003.abstracts.tar.gz'
    task1_summaries = load_summaries(summaries_tar, ['peer1.1', 'peer6.1', 'peer7.1'])
    task2_summaries = load_summaries(summaries_tar, ['peer2.2', 'peer3.2', 'peer6.2', 'peer7.2'])
    task3_summaries = load_summaries(summaries_tar, ['peer2.3', 'peer3.3', 'peer6.3', 'peer7.3'])
    task4_summaries = load_summaries(summaries_tar, ['peer4.4', 'peer5.4', 'peer6.4', 'peer7.4'])

    metrics = defaultdict(lambda: defaultdict(MetricsDict))
    load_results_table(f'{results_dir}/original.results.corrected.improved.withPenaltyForExcess/short.results.table1',
                       metrics)

    task2_metrics = defaultdict(lambda: defaultdict(MetricsDict))
    load_results_table(f'{results_dir}/original.results.corrected.improved.withPenaltyForExcess/short.results.table2',
                       metrics)

    task3_metrics = defaultdict(lambda: defaultdict(MetricsDict))
    load_results_table(f'{results_dir}/original.results.corrected.improved.withPenaltyForExcess/short.results.table3',
                       metrics)

    task4_metrics = defaultdict(lambda: defaultdict(MetricsDict))
    load_results_table(f'{results_dir}/original.results.corrected.improved.withPenaltyForExcess/short.results.table4',
                       metrics)

    load_responsiveness_table(f'{results_dir}/results.table.R.paired.noheader', metrics)
    load_usefulness_table(f'{results_dir}/results.table.U.paired.noheader', metrics)

    save_metrics(task1_summaries, metrics, 'task1', output_dir)
    save_metrics(task2_summaries, metrics, 'task2', output_dir)
    save_metrics(task3_summaries, metrics, 'task3', output_dir)
    save_metrics(task4_summaries, metrics, 'task4', output_dir)
