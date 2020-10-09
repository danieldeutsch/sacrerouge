import argparse
import itertools
import json
import logging
import numpy as np
import os
import warnings
from collections import defaultdict
from overrides import overrides
from scipy.stats import kendalltau, pearsonr, spearmanr
from typing import Any, Dict, List, Tuple, Union

from sacrerouge.commands import Subcommand
from sacrerouge.common.logging import prepare_global_logging
from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlReader

logger = logging.getLogger(__name__)


def load_metrics(metrics_files: List[str]) -> List[Metrics]:
    logger.info(f'Loading metrics from {metrics_files}')
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
    logger.info(f'Loaded {len(metrics_list)} instances')
    return metrics_list


def filter_metrics(metrics_list: List[Metrics], summarizer_type: str, metric1: str, metric2: str):
    logger.info(f'Filtering instances to summarizer type "{summarizer_type}" and metrics "{metric1}" and "{metric2}"')

    filtered = []
    incorrect_type = 0
    missing_metric1 = 0
    missing_metric2 = 0
    for metrics in metrics_list:
        if summarizer_type == 'all' or summarizer_type == metrics.summarizer_type:
            if metric1 not in metrics.metrics:
                missing_metric1 += 1
            elif metric2 not in metrics.metrics:
                missing_metric2 += 1
            else:
                filtered.append(metrics)
        else:
            incorrect_type += 1

    if incorrect_type > 0:
        logger.info(f'Filtered {incorrect_type} instances that were not summarizer type "{summarizer_type}"')
    if missing_metric1 > 0:
        logger.info(f'Filtered {missing_metric1} instances that did not have metric "{metric1}"')
    if missing_metric2 > 0:
        logger.info(f'Filtered {missing_metric2} instances that did not have metric "{metric2}"')
    logger.info(f'{len(filtered)} instances remain after filtering')

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
                                       metric2: str) -> Tuple[Dict[str, float], Dict[str, List[float]]]:
    pearsons = []
    spearmans = []
    kendalls = []
    num_nan = 0
    metrics_list = sorted(metrics_list, key=lambda metrics: metrics.instance_id)
    for _, group in itertools.groupby(metrics_list, key=lambda metrics: metrics.instance_id):
        group = list(group)
        values1 = [member.metrics[metric1] for member in group]
        values2 = [member.metrics[metric2] for member in group]

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            r, _ = pearsonr(values1, values2)
            rho, _ = spearmanr(values1, values2)
            tau, _ = kendalltau(values1, values2)

            if any(np.isnan([r, rho, tau])):
                num_nan += 1
            else:
                pearsons.append(r)
                spearmans.append(rho)
                kendalls.append(tau)

    if num_nan > 0:
        logger.warning(f'Skipped {num_nan} summary-level correlations because they were NaN')

    num_valid = len(pearsons)
    if num_valid > 0:
        pearson = sum(pearsons) / len(pearsons)
        spearman = sum(spearmans) / len(spearmans)
        kendall = sum(kendalls) / len(kendalls)
    else:
        pearson, spearman, kendall = 0, 0, 0

    averaged_correlations = {
        'pearson': {'r': pearson},
        'spearman': {'rho': spearman},
        'kendall': {'tau': kendall},
        'num_summary_groups': num_valid
    }
    individual_correlations = {
        'pearson': pearsons,
        'spearman': spearmans,
        'kendall': kendalls
    }

    return averaged_correlations, individual_correlations


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
                        summarizer_type: str,
                        return_all_summary_level: bool = False):
    if isinstance(metrics_jsonl_files, str):
        metrics_jsonl_files = [metrics_jsonl_files]

    metrics_list = load_metrics(metrics_jsonl_files)
    for metrics in metrics_list:
        metrics.flatten_keys()

    metrics_list = filter_metrics(metrics_list, summarizer_type, metric1, metric2)
    for metrics in metrics_list:
        metrics.select_metrics([metric1, metric2])
        metrics.average_values()

    summary_level, individual_summary_level = compute_summary_level_correlations(metrics_list, metric1, metric2)
    system_level = compute_system_level_correlations(metrics_list, metric1, metric2)
    global_level = compute_global_correlations(metrics_list, metric1, metric2)
    results = {
        'summary_level': summary_level,
        'system_level': system_level,
        'global': global_level
    }
    if return_all_summary_level:
        results = (results, individual_summary_level)
    return results


class CorrelateSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Calculate the correlation between two different metrics'
        self.parser = parser.add_parser('correlate', description=description, help=description)
        self.parser.add_argument(
            '--metrics-jsonl-files',
            nargs='+',
            help='The jsonl files with the metric values. If the values are split across multiple files, they can all '
                 'be passed as arguments.',
            required=True
        )
        self.parser.add_argument(
            '--metrics',
            nargs=2,
            type=str,
            help='The flattened names of the two metrics that should be correlated',
            required=True
        )
        self.parser.add_argument(
            '--summarizer-type',
            choices=['all', 'reference', 'peer'],
            help='The type of summarizer which should be included in the correlation calculation',
            required=True
        )
        self.parser.add_argument(
            '--output-file',
            type=str,
            help='The json output file which will contain the final correlations'
        )
        self.parser.add_argument(
            '--log-file',
            type=str,
            help='The file where the log should be written'
        )
        self.parser.add_argument(
            '--silent',
            action='store_true',
            help='Controls whether the log should be written to stdout'
        )
        self.parser.add_argument(
            '--summary-level-correlations-output',
            type=str,
            help='The file where all of the summary-level correlations should be written'
        )
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        prepare_global_logging(file_path=args.log_file, silent=args.silent)

        metric1, metric2 = args.metrics
        return_all_summary_level = args.summary_level_correlations_output is not None
        results = compute_correlation(args.metrics_jsonl_files, metric1, metric2, args.summarizer_type,
                                      return_all_summary_level=return_all_summary_level)

        # Strip off the original results from the individual summary correlations
        if return_all_summary_level:
            results, all_summary_level = results

        if args.output_file:
            dirname = os.path.dirname(args.output_file)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(args.output_file, 'w') as out:
                out.write(json.dumps(results, indent=2))

        if not args.silent:
            logger.info(json.dumps(results, indent=2))

        # Save the individual summary-level correlations if the output file is provided. `all_summary_level`
        # should only be defined if `return_all_summary_level` is true
        if return_all_summary_level:
            with open(args.summary_level_correlations_output, 'w') as out:
                out.write(json.dumps(all_summary_level, indent=2))
