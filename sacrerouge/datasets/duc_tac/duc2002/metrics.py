import lxml.html
import re
import tarfile
from collections import defaultdict
from io import BytesIO
from nltk.tokenize import sent_tokenize
from typing import Dict, List, Tuple

from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlWriter


def load_see_file(tar, member):
    text = tar.extractfile(member).read().decode(errors='replace')
    tree = lxml.html.document_fromstring(text)
    nodes = list(tree.xpath('//a[@id]'))
    sentences = [node.text_content() for node in nodes]
    return sentences


def load_summaries(results_dir):
    sds_summaries = defaultdict(dict)
    mds_abs_summaries = defaultdict(lambda: defaultdict(dict))
    mds_ext_summaries = defaultdict(lambda: defaultdict(dict))

    for filename in ['baseline1peers.tar.gz', 'baseline2peers.tar.gz', 'baseline3peers.tar.gz', 'manualpeers.tar.gz', 'submittedpeers.tar.gz']:
        with tarfile.open(f'{results_dir}/abstracts/phase1/SEEpeers/{filename}', 'r') as tar:
            for member in tar.getmembers():
                if member.name.endswith('.html'):
                    path = member.name.split('/')
                    filename = path[-1]
                    parts = filename.split('.')

                    sentences = load_see_file(tar, member)
                    summarizer_id = parts[4]
                    if summarizer_id.isalpha():
                        summarizer_type = 'reference'
                    else:
                        summarizer_type = 'peer'
                    summary = {
                        'summarizer_id': summarizer_id,
                        'summarizer_type': summarizer_type,
                        'text': sentences
                    }

                    if parts[1] == 'M':
                        instance_id = parts[0].lower()
                        length = parts[2]
                        if length == '010':
                            length = '10'
                        if length == '050':
                            length = '50'
                        mds_abs_summaries[instance_id][length][summarizer_id] = summary
                    else:
                        instance_id = parts[5]
                        sds_summaries[instance_id][summarizer_id] = summary

    for filename in ['model.extracts.tar', 'submissions.extracts.tar']:
        with tarfile.open(f'{results_dir}/extracts/{filename}', 'r') as tar:
            for member in tar.getmembers():
                # TODO
                pass

    return sds_summaries, mds_abs_summaries, mds_ext_summaries


def load_see_table(file_path: str, sds_metrics, mds_metrics):
    lines = open(file_path, 'r').read().splitlines()
    for line in lines[37:]:
        columns = line.split()
        assert len(columns) == 33

        summarizer_id = columns[8]
        is_multi = columns[1] == 'M'
        if is_multi:
            instance_id = columns[0].lower()
            length = columns[3]
            if length == '010':
                length = '10'
            if length == '050':
                length = '50'
            metrics = mds_metrics[instance_id][length][summarizer_id]
        else:
            instance_id = columns[2]
            metrics = sds_metrics[instance_id][summarizer_id]

        for i in range(12):
            if columns[10 + i] != '-':
                metrics['peer_quality'][f'Q{i + 1}'] = int(columns[10 + i])

        metrics['unmarked_units_related_to_subject'] = float(columns[22])
        metrics['num_peer_units'] = int(columns[23])
        metrics['num_marked_peer_units'] = int(columns[24])
        metrics['num_unmarked_peer_units'] = int(columns[25])
        metrics['num_model_units'] = int(columns[26])
        metrics['coverage']['mean'] = float(columns[27])
        metrics['coverage']['median'] = float(columns[28])
        metrics['coverage']['std'] = float(columns[29])
        metrics['length_adjusted_coverage']['mean'] = float(columns[30])
        metrics['length_adjusted_coverage']['median'] = float(columns[31])
        metrics['length_adjusted_coverage']['std'] = float(columns[32])


def load_extracts_table(file_path: str, mds_metrics):
    lines = open(file_path, 'r').read().splitlines()
    for line in lines[14:]:
        columns = line.split()
        assert len(columns) == 13, columns

        instance_id = columns[0].lower()
        length = f'{columns[2]}e'
        summarizer_id = columns[4]

        if 'sentence_precision' not in mds_metrics[instance_id][length][summarizer_id]:
            mds_metrics[instance_id][length][summarizer_id]['sentence_precision'] = []
        if 'sentence_recall' not in mds_metrics[instance_id][length][summarizer_id]:
            mds_metrics[instance_id][length][summarizer_id]['sentence_recall'] = []

        mds_metrics[instance_id][length][summarizer_id]['sentence_precision'].append(float(columns[11]))
        mds_metrics[instance_id][length][summarizer_id]['sentence_recall'].append(float(columns[12]))


def get_sds_references(summaries, instance_id, summarizer_id):
    summarizer_ids = list(summaries[instance_id].keys())
    reference_ids = list(filter(lambda sid: sid.isalpha(), summarizer_ids))

    references = []
    for reference_id in reference_ids:
        if summarizer_id == reference_id:
            continue
        references.append(summaries[instance_id][reference_id])
    return references


def get_mds_references(summaries, instance_id, length, summarizer_id):
    summarizer_ids = list(summaries[instance_id][length].keys())
    reference_ids = list(filter(lambda sid: sid.isalpha(), summarizer_ids))

    references = []
    for reference_id in reference_ids:
        if summarizer_id == reference_id:
            continue
        references.append(summaries[instance_id][length][reference_id])
    return references


def save_sds_metrics(summaries: Dict[str, Dict[str, List[str]]],
                     metrics: Dict[str, Dict[str, List[int]]],
                     task_name: str,
                     output_dir: str):
    with JsonlWriter(f'{output_dir}/{task_name}.summaries.jsonl') as out_summaries:
        with JsonlWriter(f'{output_dir}/{task_name}.metrics.jsonl') as out_metrics:
            for instance_id in sorted(summaries.keys()):
                for summarizer_id in summaries[instance_id].keys():
                    summary = summaries[instance_id][summarizer_id]
                    instance_metrics = metrics[instance_id][summarizer_id]
                    if len(instance_metrics) == 0:
                        continue

                    references = get_sds_references(summaries, instance_id, summarizer_id)

                    out_summaries.write({
                        'instance_id': instance_id,
                        'summarizer_id': summarizer_id,
                        'summarizer_type': summary['summarizer_type'],
                        'summary': summary,
                        'references': references
                    })
                    out_metrics.write(Metrics(instance_id, summarizer_id, summary['summarizer_type'], instance_metrics))


def save_mds_metrics(summaries: Dict[str, Dict[str, List[str]]],
                     metrics: Dict[str, Dict[str, List[int]]],
                     task_name: str,
                     output_dir: str):
    for length in ['10', '50', '100', '200']:
        with JsonlWriter(f'{output_dir}/{task_name}.{length}.summaries.jsonl') as out_summaries:
            with JsonlWriter(f'{output_dir}/{task_name}.{length}.metrics.jsonl') as out_metrics:
                for instance_id in sorted(summaries.keys()):
                    for summarizer_id in summaries[instance_id][length].keys():
                        summary = summaries[instance_id][length][summarizer_id]
                        instance_metrics = metrics[instance_id][length][summarizer_id]
                        if len(instance_metrics) == 0:
                            continue

                        references = get_mds_references(summaries, instance_id, length, summarizer_id)

                        out_summaries.write({
                            'instance_id': instance_id,
                            'summarizer_id': summarizer_id,
                            'summarizer_type': summary['summarizer_type'],
                            'summary': summary,
                            'references': references
                        })
                        out_metrics.write(Metrics(instance_id, summarizer_id, summary['summarizer_type'], instance_metrics))


def setup(data_root: str, output_dir: str) -> None:
    results_dir = f'{data_root}/scrapes/duc.nist.gov/past_duc/duc2002/results'
    main(results_dir, output_dir)


def main(results_dir, output_dir):
    sds_summaries, mds_abs_summaries, mds_ext_summaries = load_summaries(results_dir)

    sds_metrics = defaultdict(lambda: defaultdict(MetricsDict))
    mds_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(MetricsDict)))
    load_see_table(f'{results_dir}/abstracts/phase1/short.results.table', sds_metrics, mds_metrics)
    load_extracts_table(f'{results_dir}/extracts/extracts.results.table', mds_metrics)

    save_sds_metrics(sds_summaries, sds_metrics, 'task1', output_dir)
    save_mds_metrics(mds_abs_summaries, mds_metrics, 'task2', output_dir)