import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import warnings
from collections import defaultdict
from scipy.stats import pearsonr, spearmanr
from typing import Any, Dict, List

from sacrerouge.io import JsonlReader


def flatten_judgments(judgments: Dict[str, Any]) -> Dict[str, float]:
    def nested_iterate(d: Dict[str, Any], prefix: List[str]):
        for key, value in d.items():
            if isinstance(value, dict):
                yield from nested_iterate(value, prefix + [key])
            else:
                yield (prefix + [key], value)

    flat = {}
    for path, value in nested_iterate(judgments, []):
        name = '_'.join(path)
        flat[name] = value
    return flat


def load_judgments(judgments_jsonl: str, metric1: str, metric2: str, summary_type: str):
    judgments_list = []
    skipped_instances_count = 0
    with JsonlReader(judgments_jsonl) as f:
        for judgments in f:
            # Flatten the judgments dictionary
            judgments['judgments'] = flatten_judgments(judgments['judgments'])

            # Only keep the judgments of the desired type
            if summary_type != 'all' and judgments['summary_type'] != summary_type:
                continue

            if metric1 not in judgments['judgments'] or metric2 not in judgments['judgments']:
                skipped_instances_count += 1
            else:
                judgments_list.append(judgments)

    if skipped_instances_count > 0:
        print(f'Warning: skipped {skipped_instances_count} judgments')

    return judgments_list


def group_by_instance_id(judgments_list):
    instance_id_to_judgments_list = defaultdict(list)
    for judgments in judgments_list:
        instance_id_to_judgments_list[judgments['instance_id']].append(judgments)
    return instance_id_to_judgments_list


def compute_summary_level_correlations(judgments_list, metric1: str, metric2: str):
    groups = group_by_instance_id(judgments_list)

    pearsons = []
    spearmans = []

    total_num_peers = 0
    num_instances = 0
    num_skipped = 0
    for judgments in groups.values():
        metrics1 = [j['judgments'][metric1] for j in judgments]
        metrics2 = [j['judgments'][metric2] for j in judgments]

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            r, _ = pearsonr(metrics1, metrics2)
            p, _ = spearmanr(metrics1, metrics2)

        if np.isnan(r) or np.isnan(p):
            num_skipped += 1
            continue

        total_num_peers += len(metrics1)
        num_instances += 1

        pearsons.append(r)
        spearmans.append(p)

    pearson = sum(pearsons) / len(pearsons)
    spearman = sum(spearmans) / len(spearmans)

    num_peers = total_num_peers / num_instances

    if num_skipped > 0:
        print(f'Warning: Skipped {num_skipped} rankings for summary-level correlation')

    return {
        'pearson': pearson,
        'spearman': spearman,
        'num_peers': num_peers,
        'num_instances': num_instances
    }


def group_by_peer_id(judgments_list):
    peer_id_to_judgments_list = defaultdict(list)
    for judgments in judgments_list:
        peer_id_to_judgments_list[judgments['peer_id']].append(judgments)
    return peer_id_to_judgments_list


def plot_metrics(metric1: str, metrics1: List[float], metric2: str, metrics2: List[float], plot_file: str):
    figure = plt.figure()
    plt.scatter(metrics1, metrics2)
    plt.title('System-Level Scatter Plot')
    plt.xlabel(metric1)
    plt.ylabel(metric2)
    dirname = os.path.dirname(plot_file)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    figure.savefig(plot_file)


def compute_system_level_correlations(judgments_list, metric1: str, metric2: str, plot_file: str):
    groups = group_by_peer_id(judgments_list)

    metrics1 = []
    metrics2 = []
    for judgments in groups.values():
        metrics1.append(sum(j['judgments'][metric1] for j in judgments) / len(judgments))
        metrics2.append(sum(j['judgments'][metric2] for j in judgments) / len(judgments))

    pearson, _ = pearsonr(metrics1, metrics2)
    spearman, _ = spearmanr(metrics1, metrics2)

    num_peers = len(groups)
    num_instances = len(list(groups.values())[0])

    if plot_file is not None:
        plot_metrics(metric1, metrics1, metric2, metrics2, plot_file)

    return {
        'pearson': pearson,
        'spearman': spearman,
        'num_peers': num_peers,
        'num_instances': num_instances
    }


def main(args):
    judgments_list = load_judgments(args.judgments_jsonl, args.metric1, args.metric2, args.summary_type)

    summary_level = compute_summary_level_correlations(judgments_list, args.metric1, args.metric2)
    system_level = compute_system_level_correlations(judgments_list, args.metric1, args.metric2, args.plot_file)

    results = {
        'metrics': [args.metric1, args.metric2],
        'summary_type': args.summary_type,
        'summary_level': summary_level,
        'system_level': system_level
    }
    if args.output_file:
        dirname = os.path.dirname(args.output_file)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(args.output_file, 'w') as out:
            out.write(json.dumps(results, indent=2))

    if not args.silent:
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('judgments_jsonl')
    argp.add_argument('metric1')
    argp.add_argument('metric2')
    argp.add_argument('summary_type', choices=['all', 'reference', 'peer'])
    argp.add_argument('--output-file')
    argp.add_argument('--silent', action='store_true')
    argp.add_argument('--plot-file')
    args = argp.parse_args()
    main(args)
