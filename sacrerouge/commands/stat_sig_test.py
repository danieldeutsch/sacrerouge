import argparse
import functools
import json
import logging
import numpy as np
import os
import random
from overrides import overrides
from scipy.stats import kendalltau, pearsonr, spearmanr
from typing import Dict, List, Tuple, Union

from sacrerouge.commands import RootSubcommand
from sacrerouge.commands.correlate import load_metrics, filter_metrics, merge_metrics
from sacrerouge.common.logging import prepare_global_logging
from sacrerouge.data import Metrics
from sacrerouge.stats import convert_to_matrices, corr_diff_test, global_corr, summary_level_corr, system_level_corr

logger = logging.getLogger(__name__)


def _get_hypotheses(two_tailed: bool,
                    dependent_metric: str,
                    metric_A: str,
                    metric_B: str,) -> Tuple[str, str]:
    if two_tailed:
        return f'r({metric_A}, {dependent_metric}) == r({metric_B}, {dependent_metric})', \
               f'r({metric_A}, {dependent_metric}) != r({metric_B}, {dependent_metric})'
    else:
        return f'r({metric_A}, {dependent_metric}) <= r({metric_B}, {dependent_metric})', \
               f'r({metric_A}, {dependent_metric}) > r({metric_B}, {dependent_metric})'


def _run_test(corr_func,
              X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
              test_method: str,
              alpha: float,
              two_tailed: bool) -> Dict:
    pearson = functools.partial(corr_func, pearsonr)
    spearman = functools.partial(corr_func, spearmanr)
    kendall = functools.partial(corr_func, kendalltau)

    r_pvalue = corr_diff_test(pearson, X, Y, Z, test_method, two_tailed)
    rho_pvalue = corr_diff_test(spearman, X, Y, Z, test_method, two_tailed)
    tau_pvalue = corr_diff_test(kendall, X, Y, Z, test_method, two_tailed)

    # For some reason, without casting `pvalue <= alpha` to a bool, the result
    # would be type `bool_` which was not json serializable
    return {
        'pearson': {
            'pvalue': r_pvalue,
            'is_significant': bool(r_pvalue <= alpha)
        },
        'spearman': {
            'pvalue': rho_pvalue,
            'is_significant': bool(rho_pvalue <= alpha)
        },
        'kendall': {
            'pvalue': tau_pvalue,
            'is_significant': bool(tau_pvalue <= alpha)
        },
    }


def run_hypothesis_tests(metrics_jsonl_files_or_metrics_list: Union[str, List[str], List[Metrics]],
                         dependent_metric: str,
                         metric_A: str,
                         metric_B: str,
                         summarizer_type: str,
                         test_method: str = 'permutation-both',
                         alpha: float = 0.05,
                         two_tailed: bool = True,
                         skip_summary_level: bool = False,
                         skip_system_level: bool = False,
                         skip_global: bool = False) -> Dict:
    if isinstance(metrics_jsonl_files_or_metrics_list, str):
        # A single file
        metrics_list = load_metrics([metrics_jsonl_files_or_metrics_list])
    elif isinstance(metrics_jsonl_files_or_metrics_list, list) and all(
            isinstance(item, str) for item in metrics_jsonl_files_or_metrics_list):
        # A list of files
        metrics_list = load_metrics(metrics_jsonl_files_or_metrics_list)
    else:
        # A list of metrics
        assert isinstance(metrics_jsonl_files_or_metrics_list, list) and all(
            isinstance(item, Metrics) for item in metrics_jsonl_files_or_metrics_list)
        metrics_list = metrics_jsonl_files_or_metrics_list

    # Merge duplicate metrics objects into one
    metrics_list = merge_metrics(metrics_list)

    for metrics in metrics_list:
        metrics.flatten_keys()

    metrics_list = filter_metrics(metrics_list, summarizer_type, dependent_metric, metric_A, metric_B)
    for metrics in metrics_list:
        metrics.select_metrics([dependent_metric, metric_A, metric_B])
        metrics.average_values()

    # Follow the math in the paper: the dependent metric is Z
    X, Y, Z = convert_to_matrices(metrics_list, metric_A, metric_B, dependent_metric)

    H0, H1 = _get_hypotheses(two_tailed, dependent_metric, metric_A, metric_B)
    results = {
        'dependent_metric': dependent_metric,
        'metric_A': metric_A,
        'metric_B': metric_B,
        'summarizer_type': summarizer_type,
        'test_method': test_method,
        'alpha': alpha,
        'two_tailed': two_tailed,
        'H0': H0,
        'H1': H1
    }
    if not skip_summary_level:
        results['summary_level'] = _run_test(summary_level_corr, X, Y, Z, test_method, alpha, two_tailed)

    if not skip_system_level:
        results['system_level'] = _run_test(system_level_corr, X, Y, Z, test_method, alpha, two_tailed)

    if not skip_global:
        results['global'] = _run_test(global_corr, X, Y, Z, test_method, alpha, two_tailed)

    return results


@RootSubcommand.register('stat-sig-test')
class StatisticalSignificanceTestSubcommand(RootSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Run hypothesis testing on the difference between the correlation between metric A and the ' \
                      'dependent metric versus metric B and the dependent metric'
        self.parser = parser.add_parser('stat-sig-test', description=description, help=description)
        self.parser.add_argument(
            '--metrics-jsonl-files',
            nargs='+',
            help='The jsonl files with the metric values. If the values are split across multiple files, they can all '
                 'be passed as arguments.',
            required=True
        )
        self.parser.add_argument(
            '--dependent-metric',
            type=str,
            help='The flattened name of the dependent metric against which A and B will be correlated',
            required=True
        )
        self.parser.add_argument(
            '--metric-A',
            type=str,
            help='The flattened name of metric A',
            required=True
        )
        self.parser.add_argument(
            '--metric-B',
            type=str,
            help='The flattened name of metric B',
            required=True
        )
        self.parser.add_argument(
            '--summarizer-type',
            choices=['all', 'reference', 'peer'],
            help='The type of summarizer which should be included in the correlation calculation',
            required=True
        )
        self.parser.add_argument(
            '--hypothesis-test',
            choices=['bootstrap-system', 'bootstrap-input', 'bootstrap-both', 'permutation-both',
                     'permutation-input', 'permutation-system', 'williams'],
            default='permutation-both',
            help='The hypothesis test to use'
        )
        self.parser.add_argument(
            '--confidence',
            type=float,
            default=95,
            help='The confidence level of the hypothesis test'
        )
        self.parser.add_argument(
            '--num-tails',
            type=int,
            choices=[1, 2],
            default=1,
            help='The number of tails to use in the hypothesis test'
        )
        self.parser.add_argument(
            '--random-seed',
            type=int,
            help='The random seed to use for numpy. Python random will be this number plus one'
        )
        self.parser.add_argument(
            '--skip-summary-level',
            action='store_true',
            help='Indicates the summary-level correlations should not be tested'
        )
        self.parser.add_argument(
            '--skip-system-level',
            action='store_true',
            help='Indicates the system-level correlations should not be tested'
        )
        self.parser.add_argument(
            '--skip-global',
            action='store_true',
            help='Indicates the global correlations should not be tested'
        )
        self.parser.add_argument(
            '--output-file',
            type=str,
            help='The json output file which will contain the test results'
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
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        prepare_global_logging(file_path=args.log_file, silent=args.silent)

        if args.random_seed is not None:
            np.random.seed(args.random_seed)
            random.seed(args.random_seed + 1)

        two_tailed = args.num_tails == 2
        alpha = 1.0 - args.confidence / 100
        results = run_hypothesis_tests(args.metrics_jsonl_files,
                                       args.dependent_metric,
                                       args.metric_A,
                                       args.metric_B,
                                       args.summarizer_type,
                                       test_method=args.hypothesis_test,
                                       alpha=alpha,
                                       two_tailed=two_tailed,
                                       skip_summary_level=args.skip_summary_level,
                                       skip_system_level=args.skip_system_level,
                                       skip_global=args.skip_global)

        if args.output_file:
            dirname = os.path.dirname(args.output_file)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            with open(args.output_file, 'w') as out:
                out.write(json.dumps(results, indent=2))

        if not args.silent:
            logger.info(json.dumps(results, indent=2))