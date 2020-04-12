import argparse
import tarfile
from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlWriter


def load_summaries(results_tar: str):
    summaries = defaultdict(dict)
    with tarfile.open(results_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('results/ROUGE/models/') or member.name.startswith('results/ROUGE/peers/'):
                parts = member.name.split('/')[-1].split('.')
                instance_id = parts[0].lower()
                summarizer_id = parts[-1]
                if summarizer_id.isalpha():
                    summarizer_type = 'reference'
                else:
                    summarizer_type = 'peer'
                sentences = tar.extractfile(member).read().decode(errors='replace').splitlines()
                if len(sentences) == 0:
                    print(f'Instance {instance_id} and summarizer {summarizer_id} summary is empty. Skipping')
                    continue

                summary = {
                    'summarizer_id': summarizer_id,
                    'summarizer_type': summarizer_type,
                    'text': sentences
                }
                if summarizer_id in summaries[instance_id]:
                    assert summaries[instance_id][summarizer_id] == summary
                summaries[instance_id][summarizer_id] = summary
    return summaries


def load_rouge_jk_output(eval_tar: str, file_path: str, metrics: Dict[str, Dict[str, MetricsDict]]) -> None:
    jk_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    with tarfile.open(eval_tar, 'r') as tar:
        lines = tar.extractfile(file_path).read().decode().splitlines()
        for line in lines:
            columns = line.split()
            if len(columns) == 7 and columns[2] == 'Eval':
                summarizer_id = columns[0]
                rouge_metric = columns[1].lower() + '_jk'
                filename = columns[3].split('.')
                instance_id = filename[0].lower()
                summarizer_id = filename[-1]

                recall = float(columns[4][2:]) * 100
                precision = float(columns[5][2:]) * 100
                f1 = float(columns[6][2:]) * 100
                jk_metrics[instance_id][summarizer_id][rouge_metric]['recall'].append(recall)
                jk_metrics[instance_id][summarizer_id][rouge_metric]['precision'].append(precision)
                jk_metrics[instance_id][summarizer_id][rouge_metric]['f1'].append(f1)

        for instance_id in jk_metrics.keys():
            for summarizer_id in jk_metrics[instance_id].keys():
                for rouge_metric in jk_metrics[instance_id][summarizer_id].keys():
                    recalls = jk_metrics[instance_id][summarizer_id][rouge_metric]['recall']
                    precisions = jk_metrics[instance_id][summarizer_id][rouge_metric]['precision']
                    f1s = jk_metrics[instance_id][summarizer_id][rouge_metric]['f1']
                    metrics[instance_id][summarizer_id][rouge_metric] = {
                        'recall': sum(recalls) / len(recalls),
                        'precision': sum(precisions) / len(precisions),
                        'f1': sum(f1s) / len(f1s)
                    }


def load_responsiveness_table(eval_tar: str, metrics: Dict[str, Dict[str, MetricsDict]]) -> None:
    with tarfile.open(eval_tar, 'r') as tar:
        lines = tar.extractfile('results/responsiveness/responsiveness.table').read().decode().splitlines()
        for line in lines[6:]:
            columns = line.split()
            instance_id = columns[0].lower()
            summarizer_id = columns[3]
            score = int(columns[4])
            metrics[instance_id][summarizer_id]['responsiveness'] = score


def load_linguistic_quality_table(eval_tar: str, metrics: Dict[str, Dict[str, MetricsDict]]):
    with tarfile.open(eval_tar, 'r') as tar:
        lines = tar.extractfile('results/linguistic_quality/linguistic_quality.table').read().decode().splitlines()
        for line in lines[7:]:
            columns = line.split()
            instance_id = columns[0].lower()
            summarizer_id = columns[3]
            question = columns[4]
            score = int(columns[5])
            metrics[instance_id][summarizer_id]['linguistic_quality'][f'Q{question}'] = score


def load_pyramid_table(pyramid_tar: str, metrics: Dict[str, Dict[str, MetricsDict]]):
    with tarfile.open(pyramid_tar, 'r') as tar:
        # The "processed_pans.txt" file has obvious corrected errors, whereas "unprocessed_pans.txt" does not
        lines = tar.extractfile('processed_pans.txt').read().decode().splitlines()
        for line in lines:
            columns = line.split()
            instance_id = 'd' + columns[0].lower()
            summarizer_id = columns[1]

            # This file contains scores for both references and peers. However, the
            # annotation files show that only a portion of the references were used
            # to create the pyramid, and the remaining references were evaluated against
            # those pyramids. The pyramid references do not appear in this file.
            # Therefore, the pyramid scores between references and peers here can
            # be directly compared, and they don't need to be marked as jackknifed
            #
            # Also, for some clusters there are two sets of annotations. We just pick
            # whichever one comes last. I don't think it matters significantly
            metrics[instance_id][summarizer_id]['pyramid_score'] = float(columns[2])
            metrics[instance_id][summarizer_id]['modified_pyramid_score'] = float(columns[3])
            metrics[instance_id][summarizer_id]['num_scus'] = int(columns[4])
            metrics[instance_id][summarizer_id]['num_repetitions'] = int(columns[5])


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
                 output_dir: str):
    with JsonlWriter(f'{output_dir}/task1.summaries.jsonl') as out_summaries:
        with JsonlWriter(f'{output_dir}/task1.metrics.jsonl') as out_metrics:
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
    results_tar = f'{data_root}/scrapes/duc.nist.gov/past_duc/duc2005/results/NIST/results.tar'
    pyramid_tar = f'{data_root}/scrapes/duc.nist.gov/past_duc/duc2005/results/Pyramid/DUC2005.tar.gz'
    main(results_tar, pyramid_tar, output_dir)


def main(results_tar, pyramid_tar, output_dir):
    summaries = load_summaries(results_tar)

    metrics = defaultdict(lambda: defaultdict(MetricsDict))
    load_rouge_jk_output(results_tar, 'results/ROUGE/rougejk.m.out', metrics)
    load_responsiveness_table(results_tar, metrics)
    load_linguistic_quality_table(results_tar, metrics)
    load_pyramid_table(pyramid_tar, metrics)

    save_metrics(summaries, metrics, output_dir)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('results_tar')
    argp.add_argument('pyramid_tar')
    argp.add_argument('output_dir')
    args = argp.parse_args()

    main(args.results_tar, args.pyramid_tar, args.output_dir)
