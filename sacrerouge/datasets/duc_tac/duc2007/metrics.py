import argparse
import tarfile
from collections import defaultdict
from typing import Dict

from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlWriter


def load_main_summaries(main_eval_tar_path: str):
    summaries = defaultdict(dict)
    with tarfile.open(main_eval_tar_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('mainEval/ROUGE/models/') or member.name.startswith('mainEval/ROUGE/peers/'):
                path = member.name.split('/')
                instance_id = path[-1].split('.')[0].lower()
                summarizer_id = path[-1].split('.')[-1]

                if summarizer_id.isalpha():
                    summarizer_type = 'reference'
                else:
                    summarizer_type = 'peer'

                sentences = tar.extractfile(member).read().decode(errors='replace').splitlines()
                summary = {
                    'summarizer_id': summarizer_id,
                    'summarizer_type': summarizer_type,
                    'text': sentences
                }
                summaries[instance_id][summarizer_id] = summary
    return summaries


def load_update_summaries(update_eval_tar_path: str):
    summaries = defaultdict(lambda: defaultdict(dict))
    with tarfile.open(update_eval_tar_path, 'r') as tar:
        for member in tar.getmembers():
            if member.name.startswith('updateEval/ROUGE/models/') or member.name.startswith('updateEval/ROUGE/peers/'):
                path = member.name.split('/')
                cluster = path[-1].split('.')[0][:-2].lower()
                group = path[-1].split('.')[0][-1]
                summarizer_id = path[-1].split('.')[-1]

                if summarizer_id.isalpha():
                    summarizer_type = 'reference'
                else:
                    summarizer_type = 'peer'

                sentences = tar.extractfile(member).read().decode(errors='replace').splitlines()
                summary = {
                    'summarizer_id': summarizer_id,
                    'summarizer_type': summarizer_type,
                    'text': sentences
                }
                summaries[cluster][summarizer_id][group] = summary
    return summaries


def load_main_rouge_jk_output(eval_tar: str, file_path: str, metrics: Dict[str, Dict[str, Dict[str, MetricsDict]]]):
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


def load_update_rouge_jk_output(eval_tar: str, file_path: str, metrics: Dict[str, Dict[str, Dict[str, MetricsDict]]]):
    jk_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
    with tarfile.open(eval_tar, 'r') as tar:
        lines = tar.extractfile(file_path).read().decode().splitlines()
        for line in lines:
            columns = line.split()
            if len(columns) == 7 and columns[2] == 'Eval':
                summarizer_id = columns[0]
                rouge_metric = columns[1].lower() + '_jk'
                filename = columns[3].split('.')
                instance_id = filename[0].split('-')[0].lower()
                group = filename[0].split('-')[1]
                summarizer_id = filename[-1]

                recall = float(columns[4][2:]) * 100
                precision = float(columns[5][2:]) * 100
                f1 = float(columns[6][2:]) * 100
                jk_metrics[instance_id][group][summarizer_id][rouge_metric]['recall'].append(recall)
                jk_metrics[instance_id][group][summarizer_id][rouge_metric]['precision'].append(precision)
                jk_metrics[instance_id][group][summarizer_id][rouge_metric]['f1'].append(f1)

        for instance_id in jk_metrics.keys():
            for group in ['A', 'B', 'C']:
                for summarizer_id in jk_metrics[instance_id][group].keys():
                    for rouge_metric in jk_metrics[instance_id][group][summarizer_id].keys():
                        recalls = jk_metrics[instance_id][group][summarizer_id][rouge_metric]['recall']
                        precisions = jk_metrics[instance_id][group][summarizer_id][rouge_metric]['precision']
                        f1s = jk_metrics[instance_id][group][summarizer_id][rouge_metric]['f1']
                        metrics[instance_id][group][summarizer_id][rouge_metric] = {
                            'recall': sum(recalls) / len(recalls),
                            'precision': sum(precisions) / len(precisions),
                            'f1': sum(f1s) / len(f1s)
                        }


def load_main_content_table(main_eval_tar_path: str, metrics: Dict[str, Dict[str, Dict[str, MetricsDict]]]):
    with tarfile.open(main_eval_tar_path, 'r') as tar:
        lines = tar.extractfile('mainEval/manual/content.table').read().decode().splitlines()
        for line in lines[6:]:
            columns = line.split()
            instance_id = columns[0].lower()
            summarizer_id = columns[3]
            score = int(columns[4])
            metrics[instance_id][summarizer_id]['content_responsiveness'] = score


def load_update_content_table(update_eval_tar_path: str, metrics: Dict[str, Dict[str, Dict[str, MetricsDict]]]):
    with tarfile.open(update_eval_tar_path, 'r') as tar:
        lines = tar.extractfile('updateEval/Responsiveness/content.table').read().decode().splitlines()
        for line in lines[6:]:
            columns = line.split()
            instance_id = columns[0].split('-')[0].lower()
            group = columns[0].split('-')[1]
            summarizer_id = columns[3]
            score = int(columns[4])
            metrics[instance_id][group][summarizer_id]['content_responsiveness'] = score


def load_main_linguistic_quality_table(main_eval_tar_path: str, metrics: Dict[str, Dict[str, Dict[str, MetricsDict]]]):
    with tarfile.open(main_eval_tar_path, 'r') as tar:
        lines = tar.extractfile('mainEval/manual/linguistic_quality.table').read().decode().splitlines()
        for line in lines[7:]:
            columns = line.split()
            instance_id = columns[0].lower()
            summarizer_id = columns[3]
            question = columns[4]
            score = int(columns[5])
            metrics[instance_id][summarizer_id]['linguistic_quality'][f'Q{question}'] = score


def get_references(summaries, instance_id, summarizer_id, group=None):
    summarizer_ids = list(summaries[instance_id].keys())
    reference_ids = list(filter(lambda sid: sid.isalpha(), summarizer_ids))

    references = []
    for reference_id in reference_ids:
        if summarizer_id == reference_id:
            continue
        if group:
            references.append(summaries[instance_id][reference_id][group])
        else:
            references.append(summaries[instance_id][reference_id])
    return references


def save_main_summaries_metrics(summaries, metrics, output_dir: str):
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
                    out_metrics.write({
                        'instance_id': instance_id,
                        'summarizer_id': summarizer_id,
                        'summarizer_type': summary['summarizer_type'],
                        'metrics': instance_metrics
                    })


def save_update_summaries_metrics(summaries, metrics, output_dir: str):
    with JsonlWriter(f'{output_dir}/task2.A-B-C.summaries.jsonl') as out_summaries_A_B_C:
        with JsonlWriter(f'{output_dir}/task2.A.summaries.jsonl') as out_summaries_A:
            with JsonlWriter(f'{output_dir}/task2.B.summaries.jsonl') as out_summaries_B:
                with JsonlWriter(f'{output_dir}/task2.C.summaries.jsonl') as out_summaries_C:
                    with JsonlWriter(f'{output_dir}/task2.A-B-C.metrics.jsonl') as out_metrics_A_B_C:
                        with JsonlWriter(f'{output_dir}/task2.A.metrics.jsonl') as out_metrics_A:
                            with JsonlWriter(f'{output_dir}/task2.B.metrics.jsonl') as out_metrics_B:
                                with JsonlWriter(f'{output_dir}/task2.C.metrics.jsonl') as out_metrics_C:
                                    for instance_id in sorted(summaries.keys()):
                                        for summarizer_id in sorted(summaries[instance_id].keys()):
                                            summary_A = summaries[instance_id][summarizer_id]['A']
                                            summary_B = summaries[instance_id][summarizer_id]['B']
                                            summary_C = summaries[instance_id][summarizer_id]['C']

                                            references_A = get_references(summaries, instance_id, summarizer_id, 'A')
                                            references_B = get_references(summaries, instance_id, summarizer_id, 'B')
                                            references_C = get_references(summaries, instance_id, summarizer_id, 'C')

                                            metrics_A = metrics[instance_id]['A'][summarizer_id]
                                            metrics_B = metrics[instance_id]['B'][summarizer_id]
                                            metrics_C = metrics[instance_id]['C'][summarizer_id]

                                            summary_instance_A = {
                                                'instance_id': f'{instance_id}-A',
                                                'summarizer_id': summarizer_id,
                                                'summarizer_type': summary_A['summarizer_type'],
                                                'summary': summary_A,
                                                'references': references_A,
                                            }
                                            summary_instance_B = {
                                                'instance_id': f'{instance_id}-B',
                                                'summarizer_id': summarizer_id,
                                                'summarizer_type': summary_B['summarizer_type'],
                                                'summary': summary_B,
                                                'references': references_B,
                                                'metrics': metrics_B
                                            }
                                            summary_instance_C = {
                                                'instance_id': f'{instance_id}-C',
                                                'summarizer_id': summarizer_id,
                                                'summarizer_type': summary_B['summarizer_type'],
                                                'summary': summary_C,
                                                'references': references_C,
                                                'metrics': metrics_C
                                            }
                                            metric_instance_A = Metrics(f'{instance_id}-A', summarizer_id, summary_A['summarizer_type'], metrics_A)
                                            metric_instance_B = Metrics(f'{instance_id}-B', summarizer_id, summary_B['summarizer_type'], metrics_B)
                                            metric_instance_C = Metrics(f'{instance_id}-C', summarizer_id, summary_C['summarizer_type'], metrics_C)

                                            out_summaries_A_B_C.write(summary_instance_A)
                                            out_summaries_A_B_C.write(summary_instance_B)
                                            out_summaries_A_B_C.write(summary_instance_C)
                                            out_summaries_A.write(summary_instance_A)
                                            out_summaries_B.write(summary_instance_B)
                                            out_summaries_C.write(summary_instance_C)

                                            out_metrics_A_B_C.write(metric_instance_A)
                                            out_metrics_A_B_C.write(metric_instance_B)
                                            out_metrics_A_B_C.write(metric_instance_C)
                                            out_metrics_A.write(metric_instance_A)
                                            out_metrics_B.write(metric_instance_B)
                                            out_metrics_C.write(metric_instance_C)


def setup(data_root: str, output_dir: str):
    main_eval_tar = f'{data_root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2007/results/mainEval.tar.gz'
    update_eval_tar = f'{data_root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2007/results/updateEval.tar.gz'
    main(main_eval_tar, update_eval_tar, output_dir)


def main(main_eval_tar, update_eval_tar, output_dir):
    main_summaries = load_main_summaries(main_eval_tar)
    update_summaries = load_update_summaries(update_eval_tar)

    main_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(MetricsDict)))
    update_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(MetricsDict)))

    load_main_rouge_jk_output(main_eval_tar, 'mainEval/ROUGE/rougejk.m.out', main_metrics)
    load_update_rouge_jk_output(update_eval_tar, 'updateEval/ROUGE/rougejk.m.out', update_metrics)

    load_main_content_table(main_eval_tar, main_metrics)
    load_update_content_table(update_eval_tar, update_metrics)

    load_main_linguistic_quality_table(main_eval_tar, main_metrics)

    load_main_rouge_jk_output(main_eval_tar, 'mainEval/BE/simplejk.m.hm.out', main_metrics)
    load_update_rouge_jk_output(update_eval_tar, 'updateEval/BE/simplejk.m.hm.out', update_metrics)

    save_main_summaries_metrics(main_summaries, main_metrics, output_dir)
    save_update_summaries_metrics(update_summaries, update_metrics, output_dir)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('main_eval_tar')
    argp.add_argument('update_eval_tar')
    argp.add_argument('output_dir')
    args = argp.parse_args()

    main(args.main_eval_tar, args.update_eval_tar, args.output_dir)
