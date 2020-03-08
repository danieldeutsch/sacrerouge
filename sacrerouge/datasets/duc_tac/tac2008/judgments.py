import argparse
import tarfile
from collections import defaultdict

from sacrerouge.io import JsonlWriter


def parse_filename(filename: str):
    parts = filename.split('.')
    assert len(parts) == 5
    instance_id = parts[0].split('-')[0].lower()
    group = parts[0].split('-')[1]
    summary_id = parts[4]
    return instance_id, group, summary_id


def load_summaries(eval_tar: str):
    summaries = defaultdict(lambda: defaultdict(dict))
    with tarfile.open(eval_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and (member.name.startswith('UpdateSumm08_eval/ROUGE/models/') or member.name.startswith('UpdateSumm08_eval/ROUGE/peers/')):
                path = member.name.split('/')
                filename = path[-1]
                instance_id, group, summary_id = parse_filename(filename)

                sentences = tar.extractfile(member).read().decode(errors='replace').splitlines()
                sentences = list(filter(None, map(lambda sentence: sentence.strip(), sentences)))
                summary = {
                    'id': summary_id,
                    'text': sentences
                }
                summaries[instance_id][summary_id][group] = summary
    return summaries


def load_manual_judgments(eval_tar: str):
    judgments = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    with tarfile.open(eval_tar, 'r') as tar:
        lines = tar.extractfile('UpdateSumm08_eval/manual/manual.model').read().decode().splitlines()
        for line in lines:
            columns = line.split()
            instance_id = columns[0].split('-')[0].lower()
            group = columns[0].split('-')[1]
            summary_id = columns[1]
            judgments[instance_id][group][summary_id] = {
                'num_scus_jk': int(columns[2]),
                'modified_pyramid_score_jk': float(columns[4]),
                'linguistic_quality': int(columns[5]),
                'overall_responsiveness': int(columns[6])
            }

        lines = tar.extractfile('UpdateSumm08_eval/manual/manual.peer').read().decode().splitlines()
        for line in lines:
            columns = line.split()
            instance_id = columns[0].split('-')[0].lower()
            group = columns[0].split('-')[1]
            summary_id = columns[1]
            judgments[instance_id][group][summary_id] = {
                'modified_pyramid_score': float(columns[2]),
                'num_scus': int(columns[3]),
                'num_repetitions': int(columns[4]),
                'modified_pyramid_score_jk': float(columns[6]),
                'linguistic_quality': int(columns[7]),
                'overall_responsiveness': int(columns[8])
            }
    return judgments


def load_rouge_output(eval_tar: str, file_path: str):
    judgments = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    with tarfile.open(eval_tar, 'r') as tar:
        lines = tar.extractfile(file_path).read().decode().splitlines()
        for line in lines:
            columns = line.split()
            if len(columns) == 7 and columns[2] == 'Eval':
                summary_id = columns[0]
                rouge_metric = columns[1].lower()
                instance_id, group, summary_id = parse_filename(columns[3])
                recall = float(columns[4][2:]) * 100
                precision = float(columns[5][2:]) * 100
                f1 = float(columns[6][2:]) * 100
                judgments[instance_id][group][summary_id][rouge_metric] = {
                    'recall': recall,
                    'precision': precision,
                    'f1': f1
                }
    return judgments


def load_rouge_jk_output(eval_tar: str, file_path: str):
    jk_judgments = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))
    with tarfile.open(eval_tar, 'r') as tar:
        lines = tar.extractfile(file_path).read().decode().splitlines()
        for line in lines:
            columns = line.split()
            if len(columns) == 7 and columns[2] == 'Eval':
                summary_id = columns[0]
                rouge_metric = columns[1].lower() + '_jk'
                instance_id, group, summary_id = parse_filename(columns[3])

                recall = float(columns[4][2:]) * 100
                precision = float(columns[5][2:]) * 100
                f1 = float(columns[6][2:]) * 100
                jk_judgments[instance_id][group][summary_id][rouge_metric]['recall'].append(recall)
                jk_judgments[instance_id][group][summary_id][rouge_metric]['precision'].append(precision)
                jk_judgments[instance_id][group][summary_id][rouge_metric]['f1'].append(f1)

        judgments = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        for instance_id in jk_judgments.keys():
            for group in ['A', 'B']:
                for summary_id in jk_judgments[instance_id][group].keys():
                    for rouge_metric in jk_judgments[instance_id][group][summary_id].keys():
                        recalls = jk_judgments[instance_id][group][summary_id][rouge_metric]['recall']
                        precisions = jk_judgments[instance_id][group][summary_id][rouge_metric]['precision']
                        f1s = jk_judgments[instance_id][group][summary_id][rouge_metric]['f1']
                        judgments[instance_id][group][summary_id][rouge_metric] = {
                            'recall': sum(recalls) / len(recalls),
                            'precision': sum(precisions) / len(precisions),
                            'f1': sum(f1s) / len(f1s)
                        }
    return judgments


def merge_judgments(judgments1, judgments2):
    for instance_id in judgments2.keys():
        for group in ['A', 'B']:
            for summary_id in judgments2[instance_id][group].keys():
                for metric, value in judgments2[instance_id][group][summary_id].items():
                    judgments1[instance_id][group][summary_id][metric] = value


def get_references(summaries, instance_id, summary_id, group):
    summary_ids = list(summaries[instance_id].keys())
    reference_ids = list(filter(lambda sid: sid.isalpha(), summary_ids))

    references = []
    for reference_id in reference_ids:
        if summary_id == reference_id:
            continue
        references.append(summaries[instance_id][reference_id][group])
    return references


def save_judgments(summaries, judgments, output_dir: str):
    with JsonlWriter(f'{args.output_dir}/task1.A.judgments.jsonl') as out_A:
        with JsonlWriter(f'{args.output_dir}/task1.B.judgments.jsonl') as out_B:
            for instance_id in sorted(summaries.keys()):
                for summary_id in sorted(summaries[instance_id].keys()):
                    if summary_id.isalpha():
                        summary_type = 'reference'
                    elif summary_id == '0':
                        summary_type = 'baseline'
                    else:
                        summary_type = 'peer'

                    summary_A = summaries[instance_id][summary_id]['A']
                    summary_B = summaries[instance_id][summary_id]['B']

                    references_A = get_references(summaries, instance_id, summary_id, 'A')
                    references_B = get_references(summaries, instance_id, summary_id, 'B')

                    judgments_A = judgments[instance_id]['A'][summary_id]
                    judgments_B = judgments[instance_id]['B'][summary_id]

                    out_A.write({
                        'instance_id': instance_id,
                        'type': summary_type,
                        'summary': summary_A,
                        'references': references_A,
                        'judgments': judgments_A
                    })
                    out_B.write({
                        'instance_id': instance_id,
                        'type': summary_type,
                        'summary': summary_B,
                        'references': references_B,
                        'judgments': judgments_B
                    })


def main(args):
    summaries = load_summaries(args.eval_tar)

    judgments = load_manual_judgments(args.eval_tar)
    rouge = load_rouge_output(args.eval_tar, 'UpdateSumm08_eval/ROUGE/rouge.m.out')
    rouge_jk = load_rouge_jk_output(args.eval_tar, 'UpdateSumm08_eval/ROUGE/rougejk.m.out')
    be = load_rouge_output(args.eval_tar, 'UpdateSumm08_eval/BE/simple.m.hm.out')
    be_jk = load_rouge_jk_output(args.eval_tar, 'UpdateSumm08_eval/BE/simplejk.m.hm.out')

    merge_judgments(judgments, rouge)
    merge_judgments(judgments, rouge_jk)
    merge_judgments(judgments, be)
    merge_judgments(judgments, be_jk)

    save_judgments(summaries, judgments, args.output_dir)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('eval_tar')
    argp.add_argument('output_dir')
    args = argp.parse_args()
    main(args)
