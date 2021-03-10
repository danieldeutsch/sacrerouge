import argparse
import functools
import itertools
import json
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict
from overrides import overrides
from scipy.stats import kendalltau, pearsonr, spearmanr
from typing import Any, Dict, List, Tuple, Union

from sacrerouge.commands import RootSubcommand
from sacrerouge.common.logging import prepare_global_logging
from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlReader
from sacrerouge.stats import convert_to_matrices, corr_ci, global_corr, summary_level_corr, system_level_corr

logger = logging.getLogger(__name__)


def load_metrics(metrics_files: List[str]) -> List[Metrics]:
    logger.info(f'Loading metrics from {metrics_files}')
    metrics_list = []
    for metrics_file in metrics_files:
        metrics_list.extend(JsonlReader(metrics_file, Metrics).read())
    logger.info(f'Loaded {len(metrics_list)} metrics objects')
    return metrics_list


def merge_metrics(metrics_list: List[Metrics]) -> List[Metrics]:
    logger.info(f'Merging multiple metrics objects for the same (instance, summary) into a single object')
    metrics_dicts = defaultdict(dict)
    for metrics in metrics_list:
        if metrics.summarizer_id not in metrics_dicts[metrics.instance_id]:
            metrics_dicts[metrics.instance_id][metrics.summarizer_id] = metrics
        else:
            metrics_dicts[metrics.instance_id][metrics.summarizer_id].merge(metrics)

    merged_metrics_list = []
    for metrics_dict in metrics_dicts.values():
        merged_metrics_list.extend(list(metrics_dict.values()))
    logger.info(f'Merged into {len(merged_metrics_list)} instances')
    return merged_metrics_list


def filter_metrics(metrics_list: List[Metrics], summarizer_type: str, *metric_names: Union[str, List[str]]) -> List[Metrics]:
    logger.info(f'Filtering instances to summarizer type "{summarizer_type}" and metrics "{metric_names}"')

    filtered = []
    incorrect_type = 0
    missing_counts = [0] * len(metric_names)
    for metrics in metrics_list:
        if summarizer_type == 'all' or summarizer_type == metrics.summarizer_type:
            keep = True
            for i, name in enumerate(metric_names):
                if name not in metrics.metrics:
                    keep = False
                    missing_counts[i] += 1
            if keep:
                filtered.append(metrics)
        else:
            incorrect_type += 1

    if incorrect_type > 0:
        logger.info(f'Filtered {incorrect_type} instances that were not summarizer type "{summarizer_type}"')
    for name, missing in zip(metric_names, missing_counts):
        if missing > 0:
            logger.info(f'Filtered {missing} instances that did not have metric "{name}"')
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


def _split_level_kwargs(kwargs: Dict) -> Tuple[Dict, Dict, Dict]:
    summary_kwargs = kwargs.pop('summary_level', {})
    system_kwargs = kwargs.pop('system_level', {})
    global_kwargs = kwargs.pop('global', {})

    summary_kwargs = dict(**kwargs, **summary_kwargs)
    system_kwargs = dict(**kwargs, **system_kwargs)
    global_kwargs = dict(**kwargs, **global_kwargs)
    return summary_kwargs, system_kwargs, global_kwargs


def _split_correlation_kwargs(kwargs: Dict) -> Tuple[Dict, Dict, Dict]:
    pearson_kwargs = kwargs.pop('pearson', {})
    spearman_kwargs = kwargs.pop('spearman', {})
    kendall_kwargs = kwargs.pop('kendall', {})

    pearson_kwargs = dict(**kwargs, **pearson_kwargs)
    spearman_kwargs = dict(**kwargs, **spearman_kwargs)
    kendall_kwargs = dict(**kwargs, **kendall_kwargs)
    return pearson_kwargs, spearman_kwargs, kendall_kwargs


def compute_summary_level_correlations(X: np.ndarray,
                                       Y: np.ndarray,
                                       ci_method: str,
                                       alpha: float,
                                       two_tailed: bool,
                                       ci_kwargs: Dict = None) -> Dict:
    ci_kwargs = ci_kwargs or {}
    pearson_kwargs, spearman_kwargs, kendall_kwargs = _split_correlation_kwargs(ci_kwargs)

    pearson = functools.partial(summary_level_corr, pearsonr)
    spearman = functools.partial(summary_level_corr, spearmanr)
    kendall = functools.partial(summary_level_corr, kendalltau)

    r, r_groups = pearson(X, Y, return_num_instances=True)
    r_lower, r_upper = corr_ci(pearson, X, Y, ci_method, alpha, two_tailed, kwargs=pearson_kwargs)

    rho, rho_groups = spearman(X, Y, return_num_instances=True)
    rho_lower, rho_upper = corr_ci(spearman, X, Y, ci_method, alpha, two_tailed, kwargs=spearman_kwargs)

    tau, tau_groups = kendall(X, Y, return_num_instances=True)
    tau_lower, tau_upper = corr_ci(kendall, X, Y, ci_method, alpha, two_tailed, kwargs=kendall_kwargs)

    assert r_groups == rho_groups == tau_groups

    return {
        'num_summary_groups': r_groups,
        'ci_method': ci_method,
        'alpha': alpha,
        'two_tailed': two_tailed,
        'pearson': {
            'r': r,
            'lower': r_lower,
            'upper': r_upper,
        },
        'spearman': {
            'rho': rho,
            'lower': rho_lower,
            'upper': rho_upper,
        },
        'kendall': {
            'tau': tau,
            'lower': tau_lower,
            'upper': tau_upper,
        }
    }


def compute_system_level_correlations(X: np.ndarray, Y: np.ndarray, ci_method: str, alpha: float, two_tailed: bool,
                                      ci_kwargs: Dict = None) -> Dict:
    ci_kwargs = ci_kwargs or {}
    pearson_kwargs, spearman_kwargs, kendall_kwargs = _split_correlation_kwargs(ci_kwargs)

    pearson = functools.partial(system_level_corr, pearsonr)
    spearman = functools.partial(system_level_corr, spearmanr)
    kendall = functools.partial(system_level_corr, kendalltau)

    r, r_pvalue = pearson(X, Y, return_pvalue=True)
    r_lower, r_upper = corr_ci(pearson, X, Y, ci_method, alpha, two_tailed, kwargs=pearson_kwargs)

    rho, rho_pvalue = spearman(X, Y, return_pvalue=True)
    rho_lower, rho_upper = corr_ci(spearman, X, Y, ci_method, alpha, two_tailed, kwargs=spearman_kwargs)

    tau, tau_pvalue = kendall(X, Y, return_pvalue=True)
    tau_lower, tau_upper = corr_ci(kendall, X, Y, ci_method, alpha, two_tailed, kwargs=kendall_kwargs)

    num_summarizers, num_instances = X.shape

    return {
        'num_summarizers': num_summarizers,
        'num_instances': num_instances,
        'ci_method': ci_method,
        'alpha': alpha,
        'two_tailed': two_tailed,
        'pearson': {
            'r': r,
            'p_value': r_pvalue,
            'lower': r_lower,
            'upper': r_upper
        },
        'spearman': {
            'rho': rho,
            'p_value': rho_pvalue,
            'lower': rho_lower,
            'upper': rho_upper
        },
        'kendall': {
            'tau': tau,
            'p_value': tau_pvalue,
            'lower': tau_lower,
            'upper': tau_upper
        },
    }


def compute_global_correlations(X: np.ndarray, Y: np.ndarray, ci_method: str, alpha: float, two_tailed: bool,
                                ci_kwargs: Dict = None) -> Dict:
    ci_kwargs = ci_kwargs or {}
    pearson_kwargs, spearman_kwargs, kendall_kwargs = _split_correlation_kwargs(ci_kwargs)

    pearson = functools.partial(global_corr, pearsonr)
    spearman = functools.partial(global_corr, spearmanr)
    kendall = functools.partial(global_corr, kendalltau)

    r, r_pvalue = pearson(X, Y, return_pvalue=True)
    r_lower, r_upper = corr_ci(pearson, X, Y, ci_method, alpha, two_tailed, kwargs=pearson_kwargs)

    rho, rho_pvalue = spearman(X, Y, return_pvalue=True)
    rho_lower, rho_upper = corr_ci(spearman, X, Y, ci_method, alpha, two_tailed, kwargs=spearman_kwargs)

    tau, tau_pvalue = kendall(X, Y, return_pvalue=True)
    tau_lower, tau_upper = corr_ci(kendall, X, Y, ci_method, alpha, two_tailed, kwargs=kendall_kwargs)

    num_summaries = int((~np.isnan(X)).sum())  # number of non-NaN scores

    return {
        'num_summaries': num_summaries,
        'ci_method': ci_method,
        'alpha': alpha,
        'two_tailed': two_tailed,
        'pearson': {
            'r': r,
            'p_value': r_pvalue,
            'lower': r_lower,
            'upper': r_upper
        },
        'spearman': {
            'rho': rho,
            'p_value': rho_pvalue,
            'lower': rho_lower,
            'upper': rho_upper
        },
        'kendall': {
            'tau': tau,
            'p_value': tau_pvalue,
            'lower': tau_lower,
            'upper': tau_upper
        },
    }


def _plot_values(values1: List[float],
                 values2: List[float],
                 metric1: str,
                 metric2: str,
                 label: str,
                 output_file: str) -> None:
    fig = plt.figure()
    plt.xlabel(metric1)
    plt.ylabel(metric2)
    plt.scatter(values1, values2, label=label)
    plt.legend()
    plt.tight_layout()

    dirname = os.path.dirname(output_file)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    fig.savefig(output_file)
    plt.close()


def _plot_system_level_metrics(metrics_list: List[Metrics],
                               metric1: str,
                               metric2: str,
                               output_file: str) -> None:
    metrics_list = list(aggregate_metrics(metrics_list).values())
    values1 = [metrics[metric1] for metrics in metrics_list]
    values2 = [metrics[metric2] for metrics in metrics_list]
    _plot_values(values1, values2, metric1, metric2, 'Systems', output_file)


def _plot_global_metrics(metrics_list: List[Metrics],
                         metric1: str,
                         metric2: str,
                         output_file: str) -> None:
    values1 = [metrics.metrics[metric1] for metrics in metrics_list]
    values2 = [metrics.metrics[metric2] for metrics in metrics_list]
    _plot_values(values1, values2, metric1, metric2, 'Summaries', output_file)


def compute_correlation(metrics_jsonl_files_or_metrics_list: Union[str, List[str], List[Metrics]],
                        metric1: str,
                        metric2: str,
                        summarizer_type: str,
                        skip_summary_level: bool = False,
                        skip_system_level: bool = False,
                        skip_global: bool = False,
                        system_level_output_plot: str = None,
                        global_output_plot: str = None,
                        ci_method: str = None,
                        alpha: float = 0.05,
                        two_tailed: bool = True,
                        ci_kwargs: Dict = None):
    if system_level_output_plot is not None:
        assert not skip_system_level, 'If `system_level_output_plot` is not `None`, system-level correlations must be calculated'
    if global_output_plot is not None:
        assert not skip_global, 'If `global_output_plot` is not `None`, global correlations must be calculated'

    ci_kwargs = ci_kwargs or {}
    summary_kwargs, system_kwargs, global_kwargs = _split_level_kwargs(ci_kwargs)

    if isinstance(metrics_jsonl_files_or_metrics_list, str):
        # A single file
        metrics_list = load_metrics([metrics_jsonl_files_or_metrics_list])
    elif isinstance(metrics_jsonl_files_or_metrics_list, list) and all(isinstance(item, str) for item in metrics_jsonl_files_or_metrics_list):
        # A list of files
        metrics_list = load_metrics(metrics_jsonl_files_or_metrics_list)
    else:
        # A list of metrics
        assert isinstance(metrics_jsonl_files_or_metrics_list, list) and all(isinstance(item, Metrics) for item in metrics_jsonl_files_or_metrics_list)
        metrics_list = metrics_jsonl_files_or_metrics_list

    # Merge duplicate metrics objects into one
    metrics_list = merge_metrics(metrics_list)

    for metrics in metrics_list:
        metrics.flatten_keys()

    metrics_list = filter_metrics(metrics_list, summarizer_type, metric1, metric2)
    for metrics in metrics_list:
        metrics.select_metrics([metric1, metric2])
        metrics.average_values()

    X, Y = convert_to_matrices(metrics_list, metric1, metric2)

    results = {
        'metric1': metric1,
        'metric2': metric2,
        'summarizer_type': summarizer_type
    }
    if not skip_summary_level:
        results['summary_level'] = compute_summary_level_correlations(X, Y, ci_method=ci_method, alpha=alpha,
                                                                      two_tailed=two_tailed, ci_kwargs=summary_kwargs)

    if not skip_system_level:
        results['system_level'] = compute_system_level_correlations(X, Y, ci_method=ci_method, alpha=alpha,
                                                                    two_tailed=two_tailed, ci_kwargs=system_kwargs)
        if system_level_output_plot is not None:
            _plot_system_level_metrics(metrics_list, metric1, metric2, system_level_output_plot)

    if not skip_global:
        results['global'] = compute_global_correlations(X, Y, ci_method=ci_method, alpha=alpha, two_tailed=two_tailed,
                                                        ci_kwargs=global_kwargs)
        if global_output_plot is not None:
            _plot_global_metrics(metrics_list, metric1, metric2, global_output_plot)

    return results


@RootSubcommand.register('correlate')
class CorrelateSubcommand(RootSubcommand):
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
            '--confidence-interval-method',
            choices=['none', 'bootstrap-system', 'bootstrap-input', 'bootstrap-both', 'fisher'],
            default='bootstrap-both',
            help='The method to use to calculate the confidence intervals on the correlation coefficients'
        )
        self.parser.add_argument(
            '--confidence',
            type=float,
            default=95,
            help='The confidence level of the confidence intervals'
        )
        self.parser.add_argument(
            '--num-tails',
            type=int,
            choices=[1, 2],
            default=2,
            help='The number of tails to use in the confidence interval calculation'
        )
        self.parser.add_argument(
            '--confidence-interval-kwargs',
            default='{}',
            help='A serialized JSON string that will be parsed and passed as kwargs to the confidence interval calculation'
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
            '--skip-summary-level',
            action='store_true',
            help='Indicates the summary-level correlations should not be calculated'
        )
        self.parser.add_argument(
            '--skip-system-level',
            action='store_true',
            help='Indicates the system-level correlations should not be calculated'
        )
        self.parser.add_argument(
            '--skip-global',
            action='store_true',
            help='Indicates the global correlations should not be calculated'
        )
        self.parser.add_argument(
            '--system-level-output-plot',
            type=str,
            help='If provided, saves a plot of the system-level scores to the corresponding file'
        )
        self.parser.add_argument(
            '--global-output-plot',
            type=str,
            help='If provided, saves a plot of the global scores to the corresponding file'
        )
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        prepare_global_logging(file_path=args.log_file, silent=args.silent)

        metric1, metric2 = args.metrics
        two_tailed = args.num_tails == 2
        alpha = 1.0 - args.confidence / 100
        ci_kwargs = json.loads(args.confidence_interval_kwargs)
        results = compute_correlation(args.metrics_jsonl_files, metric1, metric2, args.summarizer_type,
                                      skip_summary_level=args.skip_summary_level,
                                      skip_system_level=args.skip_system_level,
                                      skip_global=args.skip_global,
                                      system_level_output_plot=args.system_level_output_plot,
                                      global_output_plot=args.global_output_plot,
                                      ci_method=args.confidence_interval_method,
                                      alpha=alpha,
                                      two_tailed=two_tailed,
                                      ci_kwargs=ci_kwargs)

        if args.output_file:
            dirname = os.path.dirname(args.output_file)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(args.output_file, 'w') as out:
                out.write(json.dumps(results, indent=2))

        if not args.silent:
            logger.info(json.dumps(results, indent=2))
