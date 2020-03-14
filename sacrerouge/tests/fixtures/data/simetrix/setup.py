"""
This script parses the sample data and output from the SIMetrix package and
saves it for unit testing.
"""
import argparse
import sys
from glob import glob

sys.path.append('.')

from sacrerouge.io import JsonlWriter  # noqa


def load_sample_documents(input_dir: str):
    documents = {}
    for instance_id in ['input1', 'input2', 'input3']:
        documents[instance_id] = []
        for file_path in glob(f'{input_dir}/{instance_id}/*.txt'):
            lines = open(file_path, 'r').read().splitlines()
            sentences = []
            for line in lines:
                if line:
                    sentences.append(line)
            documents[instance_id].append(sentences)
    return documents


def load_sample_summaries(input_dir: str):
    summaries = {}
    for instance_id in ['input1', 'input2', 'input3']:
        summaries[instance_id] = {}
        for summarizer_id in ['fb', 'me', 'nb', 'rb', 'ts']:
            summaries[instance_id][summarizer_id] = open(f'{input_dir}/{instance_id}.{summarizer_id}.txt', 'r').read().splitlines()
    return summaries


def save_instances(documents, summaries, file_path):
    with JsonlWriter(file_path) as out:
        for instance_id in ['input1', 'input2', 'input3']:
            for summarizer_id in ['fb', 'me', 'nb', 'rb', 'ts']:
                docs = documents[instance_id]
                summary = summaries[instance_id][summarizer_id]
                out.write({
                    'instance_id': instance_id,
                    'summarizer_id': summarizer_id,
                    'documents': docs,
                    'summary': summary
                })


def load_expected_summary_level_output(file_path: str):
    metrics_list = []
    lines = open(file_path, 'r').read().splitlines()
    for i, line in enumerate(lines):
        columns = line.split()
        if i == 0:
            header = columns
        else:
            metrics = {
                'instance_id': columns[0],
                'summarizer_id': columns[1],
                'metrics': {}
            }
            for j, metric_name in enumerate(header[2:]):
                metrics['metrics'][metric_name] = float(columns[j + 2])
            metrics_list.append(metrics)
    return metrics_list


def load_expected_system_level_output(file_path: str):
    metrics_list = []
    lines = open(file_path, 'r').read().splitlines()
    for i, line in enumerate(lines):
        columns = line.split()
        if i == 0:
            header = columns
        else:
            metrics = {
                'summarizer_id': columns[0],
                'metrics': {}
            }
            for j, metric_name in enumerate(header[1:]):
                metrics['metrics'][metric_name] = float(columns[j + 1])
            metrics_list.append(metrics)
    return metrics_list


def save_metrics(metrics_list, file_path):
    with JsonlWriter(file_path) as out:
        for metrics in metrics_list:
            out.write(metrics)


def main(args):
    documents = load_sample_documents(f'{args.sample_eval_dir}/sampleInputs')
    summaries = load_sample_summaries(f'{args.sample_eval_dir}/sampleSummaries')
    save_instances(documents, summaries, f'{args.output_dir}/instances.jsonl')

    summary_level = load_expected_summary_level_output(f'{args.sample_eval_dir}/sampleMappings.txt.ieval.micro')
    system_level = load_expected_system_level_output(f'{args.sample_eval_dir}/sampleMappings.txt.ieval.macro')
    save_metrics(summary_level, f'{args.output_dir}/metrics.summary-level.jsonl')
    save_metrics(system_level, f'{args.output_dir}/metrics.system-level.jsonl')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('sample_eval_dir')
    argp.add_argument('output_dir')
    args = argp.parse_args()
    main(args)
