import argparse
import itertools
import json
import os
from collections import defaultdict
from overrides import overrides
from scipy.stats import kendalltau, pearsonr, spearmanr
from typing import Any, Dict, List, Union

from sacrerouge.commands import Subcommand
from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlReader


def load_metrics(metrics_files: List[str]) -> List[Metrics]:
    metrics_dicts = defaultdict(dict)
    for metrics_file in metrics_files:
        with JsonlReader(metrics_file, Metrics) as f:
            for metrics in f:
                if metrics.summarizer_id not in metrics_dicts[metrics.instance_id]:
                    metrics_dicts[metrics.instance_id][metrics.summarizer_id] = metrics
                else:
                    metrics_dicts[metrics.instance_id][metrics.summarizer_id].merge(metrics)

    metrics_list = []
    for metrics_dict in metrics_dicts.values():
        metrics_list.extend(list(metrics_dict.values()))
    return metrics_list


def filter_metrics(metrics_list: List[Metrics], summarizer_type: str, metric1: str, metric2: str):
    filtered = []
    skipped = 0
    for metrics in metrics_list:
        if summarizer_type == 'all' or summarizer_type == metrics.summarizer_type:
            if metric1 in metrics.metrics and metric2 in metrics.metrics:
                filtered.append(metrics)
            else:
                skipped += 1

    if skipped > 0:
        print(f'Warning: Skipped {skipped} inputs because at least one metric was missing')
    return filtered


def aggregate_metrics(metrics_list: List[Metrics]) -> Dict[str, MetricsDict]:
    # The instances must be sorted by the key in order to use itertools.groupby
    metrics_list = sorted(metrics_list, key=lambda metrics: metrics.summarizer_id)
    key_to_metrics = {}
    for key, group in itertools.groupby(metrics_list, lambda metrics: metrics.summarizer_id):
        group_metrics = [member.metrics for member in group]
        key_to_metrics[key] = sum(group_metrics) / len(group_metrics)
    return key_to_metrics


def compute_summary_level_correlations(metrics_list: List[Dict[str, Any]],
                                       metric1: str,
                                       metric2: str) -> Dict[str, float]:
    pearsons = []
    spearmans = []
    kendalls = []

    metrics_list = sorted(metrics_list, key=lambda metrics: metrics.instance_id)
    for _, group in itertools.groupby(metrics_list, key=lambda metrics: metrics.instance_id):
        group = list(group)
        values1 = [member.metrics[metric1] for member in group]
        values2 = [member.metrics[metric2] for member in group]

        r, _ = pearsonr(values1, values2)
        rho, _ = spearmanr(values1, values2)
        tau, _ = kendalltau(values1, values2)

        pearsons.append(r)
        spearmans.append(rho)
        kendalls.append(tau)

    pearson = sum(pearsons) / len(pearsons)
    spearman = sum(spearmans) / len(spearmans)
    kendall = sum(kendalls) / len(kendalls)
    return {
        'pearson': {
            'r': pearson
        },
        'spearman': {
            'rho': spearman
        },
        'kendall': {
            'tau': kendall
        }
    }


def compute_system_level_correlations(metrics_list: List[Dict[str, Any]],
                                      metric1: str,
                                      metric2: str) -> Dict[str, float]:
    metrics_list = list(aggregate_metrics(metrics_list).values())

    values1 = [metrics[metric1] for metrics in metrics_list]
    values2 = [metrics[metric2] for metrics in metrics_list]

    r, r_pvalue = pearsonr(values1, values2)
    rho, rho_pvalue = spearmanr(values1, values2)
    tau, tau_pvalue = kendalltau(values1, values2)
    num_summarizers = len(metrics_list)

    return {
        'pearson': {
            'r': r,
            'p_value': r_pvalue
        },
        'spearman': {
            'rho': rho,
            'p_value': rho_pvalue
        },
        'kendall': {
            'tau': tau,
            'p_value': tau_pvalue
        },
        'num_summarizers': num_summarizers
    }


def compute_global_correlations(metrics_list: List[Dict[str, Any]],
                                metric1: str,
                                metric2: str) -> Dict[str, float]:
    values1 = [metrics.metrics[metric1] for metrics in metrics_list]
    values2 = [metrics.metrics[metric2] for metrics in metrics_list]

    r, r_pvalue = pearsonr(values1, values2)
    rho, rho_pvalue = spearmanr(values1, values2)
    tau, tau_pvalue = kendalltau(values1, values2)
    num_summaries = len(metrics_list)

    return {
        'pearson': {
            'r': r,
            'p_value': r_pvalue
        },
        'spearman': {
            'rho': rho,
            'p_value': rho_pvalue
        },
        'kendall': {
            'tau': tau,
            'p_value': tau_pvalue
        },
        'num_summaries': num_summaries
    }


def compute_correlation(metrics_jsonl_files: Union[str, List[str]],
                        metric1: str,
                        metric2: str,
                        summarizer_type: str):
    if isinstance(metrics_jsonl_files, str):
        metrics_jsonl_files = [metrics_jsonl_files]

    metrics_list = load_metrics(metrics_jsonl_files)
    for metrics in metrics_list:
        metrics.flatten_keys()
        metrics.average_values()

    metrics_list = filter_metrics(metrics_list, summarizer_type, metric1, metric2)

    summary_level = compute_summary_level_correlations(metrics_list, metric1, metric2)
    system_level = compute_system_level_correlations(metrics_list, metric1, metric2)
    global_level = compute_global_correlations(metrics_list, metric1, metric2)
    results = {
        'summary_level': summary_level,
        'system_level': system_level,
        'global': global_level
    }
    return results


class CorrelateSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('correlate')
        self.parser.add_argument('--metrics-jsonl-files', nargs='+')
        self.parser.add_argument('--metrics', nargs=2)
        self.parser.add_argument('--summarizer-type', choices=['all', 'reference', 'peer'])
        self.parser.add_argument('--output-file')
        self.parser.add_argument('--silent', action='store_true')
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        metric1, metric2 = args.metrics
        results = compute_correlation(args.metrics_jsonl_files, metric1, metric2, args.summarizer_type)

        if args.output_file:
            dirname = os.path.dirname(args.output_file)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(args.output_file, 'w') as out:
                out.write(json.dumps(results, indent=2))

        if not args.silent:
            print(json.dumps(results, indent=2))
