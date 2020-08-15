import argparse
import logging
from collections import defaultdict
from overrides import overrides
from typing import Dict, List

from sacrerouge.commands import Subcommand
from sacrerouge.common import Params
from sacrerouge.common.logging import prepare_global_logging
from sacrerouge.common.util import import_module_and_submodules
from sacrerouge.data import EvalInstance, Metrics
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.io import JsonlWriter
from sacrerouge.metrics import Metric

logger = logging.getLogger(__name__)


def add_score_arguments(parser: argparse.ArgumentParser, include_config_arguments: bool) -> None:
    if include_config_arguments:
        parser.add_argument(
            'config',
            type=str,
            help='The config file that specifies the dataset reader and metrics'
        )
        parser.add_argument(
            '--overrides',
            type=str,
            help='A serialized json that will override the parameters passed in "config"'
        )

    parser.add_argument(
        'output_jsonl',
        type=str,
        help='The path to where the input-level metrics should be written'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='The file where the log should be written'
    )
    parser.add_argument(
        '--silent',
        action='store_true',
        help='Controls whether the log should be written to stdout'
    )
    parser.add_argument(
        '--include-packages',
        nargs='+',
        help='A list of additional packages to include'
    )
    parser.add_argument(
        '--disable-peer-jackknifing',
        action='store_true',
        help='Disable running jackknifing for peer summaries'
    )


def _load_metrics(params: Params) -> List[Metric]:
    metrics = []
    for metric_params in params.pop('metrics'):
        metric = Metric.from_params(metric_params)
        metrics.append(metric)
    return metrics


def _score_with_metric(metric: Metric,
                       instances: List[EvalInstance],
                       metrics_dicts: Dict[str, Dict[str, Metrics]],
                       disable_peer_jackknifing: bool = False) -> None:
    # The summaries need to be grouped based on identical context. For instance, we group all of the summaries
    # that have the same reference documents together. This can sometimes make calculating the metric faster. The
    # following variables assist doing this.
    #
    # Maintains a list of the unique contexts which group the summaries
    fields_list = []

    # A mapping from the context to its index in `fields_list`
    field_to_index = {}

    # A nested list that will be parallel to `fields_list`. The entry at index `i` is a list of instances which should
    # be scored with `fields_list[i]`
    instances_list = []

    # A nested list that will be parallel to `instances_list` which contains the summary-specific fields
    # for the corresponding instance
    summary_fields_lists = []

    # A nested list that will be parallel to `instances_list` which marks if the calculation for that (summary, context)
    # pair represents jackknifing or not
    jackknifing_flags = []

    for instance in instances:
        # Select just the relevant fields for this metric
        summary_fields = instance.fields.select_fields(metric.required_summary_fields)
        context_fields = instance.fields.select_fields(metric.required_context_fields)

        # Score the instance normally using all of the fields. However,
        # if the metric requires jackknifing and this is a reference summary,
        # the metric is comparable to the jackknifing metrics.
        is_jackknifing = metric.requires_jackknifing() and instance.summarizer_type == 'reference'

        if context_fields not in field_to_index:
            field_to_index[context_fields] = len(field_to_index)
            fields_list.append(context_fields)
            instances_list.append([])
            summary_fields_lists.append([])
            jackknifing_flags.append([])

        index = field_to_index[context_fields]
        instances_list[index].append(instance)
        summary_fields_lists[index].append(summary_fields)
        jackknifing_flags[index].append(is_jackknifing)

        # Potentially run jackknifing for the peers
        if not disable_peer_jackknifing and metric.requires_jackknifing() and instance.summarizer_type == 'peer':
            jk_fields_list = metric.jackknifer.get_jackknifing_fields_list(context_fields)
            if jk_fields_list:
                for jk_fields in jk_fields_list:
                    if jk_fields not in field_to_index:
                        field_to_index[jk_fields] = len(field_to_index)
                        fields_list.append(jk_fields)
                        instances_list.append([])
                        summary_fields_lists.append([])
                        jackknifing_flags.append([])

                    index = field_to_index[jk_fields]
                    instances_list[index].append(instance)
                    summary_fields_lists[index].append(summary_fields)
                    jackknifing_flags[index].append(True)

    # Construct the arguments that will be passed to the scoring method
    summary_args = []
    for name in metric.required_summary_fields:
        summary_args.append([[summary_fields[name].to_input() for summary_fields in summary_fields_list] for summary_fields_list in summary_fields_lists])

    context_args = []
    for name in metric.required_context_fields:
        context_args.append([fields[name].to_input() for fields in fields_list])

    # Score the summaries
    results_lists = metric.score_multi_all(*summary_args, *context_args)

    # Used to aggregate the jk results
    jk_results = defaultdict(lambda: defaultdict(list))

    for i, results_list in enumerate(results_lists):
        for j, results in enumerate(results_list):
            instance = instances_list[i][j]
            is_jackknifing = jackknifing_flags[i][j]
            if is_jackknifing:
                jk_results[instance.instance_id][instance.summarizer_id].append(results)
            else:
                metrics_dicts[instance.instance_id][instance.summarizer_id].metrics.update(results)

    # Aggregate the jk results
    for instance_id in jk_results.keys():
        for summarizer_id, results in jk_results[instance_id].items():
            result = sum(results) / len(results)
            for name, value in result.items():
                metrics_dicts[instance_id][summarizer_id].metrics[name + '_jk'] = value


def _get_initial_metrics_dicts(instances: List[EvalInstance]) -> Dict[str, Dict[str, Metrics]]:
    metrics_dicts = defaultdict(dict)
    for instance in instances:
        metrics = Metrics(instance.instance_id, instance.summarizer_id, instance.summarizer_type)
        metrics_dicts[instance.instance_id][instance.summarizer_id] = metrics
    return metrics_dicts


def score_instances(instances: List[EvalInstance],
                    metrics: List[Metric],
                    disable_peer_jackknifing: bool = False) -> Dict[str, Dict[str, Metrics]]:
    metrics_dicts = _get_initial_metrics_dicts(instances)
    for metric in metrics:
        _score_with_metric(metric, instances, metrics_dicts, disable_peer_jackknifing=disable_peer_jackknifing)
    return metrics_dicts


def save_score_results(metrics_dicts: Dict[str, Dict[str, Metrics]], output_file: str, silent: bool) -> None:
    with JsonlWriter(output_file) as out:
        for instance_id in sorted(metrics_dicts.keys()):
            for summarizer_id in sorted(metrics_dicts[instance_id].keys()):
                out.write(metrics_dicts[instance_id][summarizer_id])


class ScoreSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Score all of the inputs to evaluate a metric'
        self.parser = parser.add_parser('score', description=description, help=description)
        add_score_arguments(self.parser, True)
        self.parser.set_defaults(func=self.run)

    @overrides
    def run(self, args):
        prepare_global_logging(file_path=args.log_file, silent=args.silent)

        import_module_and_submodules('sacrerouge')
        include_packages = args.include_packages or []
        for package in include_packages:
            import_module_and_submodules(package)

        params = Params.from_file(args.config, args.overrides)
        dataset_reader = DatasetReader.from_params(params.pop('dataset_reader'))
        metrics = _load_metrics(params)

        input_files = params.pop('input_files')
        if isinstance(input_files, str):
            input_files = [input_files]

        instances = dataset_reader.read(*input_files)
        metrics_dicts = score_instances(instances, metrics, args.disable_peer_jackknifing)

        save_score_results(metrics_dicts, args.output_jsonl, args.silent)
