import argparse
import jsons
import logging
import os
from overrides import overrides
from typing import List, Tuple

from sacrerouge.commands import RootSubcommand
from sacrerouge.common import Params
from sacrerouge.common.logging import prepare_global_logging
from sacrerouge.common.util import import_module_and_submodules
from sacrerouge.data import EvalInstance, Metrics, MetricsDict
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.io import JsonlWriter
from sacrerouge.metrics import Metric

logger = logging.getLogger(__name__)


def load_metrics(params: Params) -> List[Metric]:
    metrics = []
    for metric_params in params.pop('metrics'):
        metric = Metric.from_params(metric_params)
        metrics.append(metric)
    return metrics


def get_initial_micro_list(instances: List[EvalInstance]) -> List[Metrics]:
    micro_list = []
    for instance in instances:
        micro_list.append(Metrics(instance.instance_id, instance.summarizer_id, instance.summarizer_type))
    return micro_list


def evaluate_instances(instances: List[EvalInstance], metrics: List[Metric]) -> Tuple[MetricsDict, List[Metrics]]:
    macro = MetricsDict()
    micro_list = get_initial_micro_list(instances)

    for metric in metrics:
        # Prepare the input arguments
        summary_args = []
        for field in metric.required_summary_fields:
            summary_args.append([instance.fields[field].to_input() for instance in instances])

        context_args = []
        for field in metric.required_context_fields:
            context_args.append([instance.fields[field].to_input() for instance in instances])

        # Score all the summaries
        this_macro, this_micro_list = metric.evaluate(*summary_args, *context_args)

        # Update the global metrics dictionaries
        macro.update(this_macro)
        for micro, this_micro in zip(micro_list, this_micro_list):
            micro.metrics.update(this_micro)

    return macro, micro_list


def save_evaluation_results(macro_results: MetricsDict,
                            micro_results_list: List[Metrics],
                            macro_output_json: str,
                            micro_output_jsonl: str,
                            silent: bool) -> None:
    dirname = os.path.dirname(macro_output_json)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    serialized_macro = jsons.dumps({'metrics': macro_results}, jdkwargs={'indent': 2})
    with open(macro_output_json, 'w') as out:
        out.write(serialized_macro)
    if not silent:
        logger.info(serialized_macro)

    with JsonlWriter(micro_output_jsonl) as out:
        for metrics_dict in micro_results_list:
            out.write(metrics_dict)


def add_evaluate_arguments(parser: argparse.ArgumentParser, include_config_arguments: bool) -> None:
    if include_config_arguments:
        parser.add_argument(
            '--config',
            type=str,
            help='The config file that specifies the dataset reader and metrics',
            required=True
        )
        parser.add_argument(
            '--overrides',
            type=str,
            help='A serialized json that will override the parameters passed in "config"'
        )

    parser.add_argument(
        '--macro-output-json',
        type=str,
        help='The path to where the system-level metrics should be written',
        required=True
    )
    parser.add_argument(
        '--micro-output-jsonl',
        type=str,
        help='The path to where the input-level metrics should be written',
        required=True
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


@RootSubcommand.register('evaluate')
class EvaluateSubcommand(RootSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Evaluate a summarization model'
        self.parser = parser.add_parser('evaluate', description=description, help=description)
        add_evaluate_arguments(self.parser, True)
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
        metrics = load_metrics(params)

        input_files = params.pop('input_files')
        if isinstance(input_files, str):
            input_files = [input_files]

        instances = dataset_reader.read(*input_files)
        macro, micro_list = evaluate_instances(instances, metrics)

        save_evaluation_results(macro, micro_list, args.macro_output_json, args.micro_output_jsonl, args.silent)
