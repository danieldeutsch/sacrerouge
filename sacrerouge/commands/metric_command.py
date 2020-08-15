import argparse
from overrides import overrides
from typing import Type

from sacrerouge.commands import Subcommand
from sacrerouge.commands.evaluate import add_evaluate_arguments, evaluate_instances, save_evaluation_results
from sacrerouge.commands.score import add_score_arguments, save_score_results, score_instances
from sacrerouge.common import Registrable
from sacrerouge.common.arguments import add_metric_arguments, get_dataset_reader_from_argument, get_metric_from_arguments
from sacrerouge.common.logging import prepare_global_logging
from sacrerouge.common.util import import_module_and_submodules
from sacrerouge.metrics import Metric


def add_metric_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Adds a MetricSubcommand for every registered metric."""
    for name, (metric, _) in Registrable._registry[Metric].items():
        command = MetricSubcommand(name, metric)
        command.add_subparser(subparsers)


def add_dataset_reader_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--dataset-reader',
        type=str,
        required=True,
        help='The name or the parameters as a serialized json for the dataset reader'
    )
    parser.add_argument(
        '--input-files',
        nargs='+',
        required=True,
        help='The input files to be passed to the dataset reader'
    )


class MetricSubcommand(Subcommand):
    def __init__(self, name: str, metric_type: Type) -> None:
        super().__init__()
        self.name = name
        self.metric_type = metric_type

    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = f'Run "evaluate" or "score" with the "{self.name}" metric.'
        self.parser = parser.add_parser(self.name, description=description, help=description)
        subparsers = self.parser.add_subparsers()

        description = f'Run "evaluate" with the "{self.name}" metric.'
        self.evaluate_parser = subparsers.add_parser('evaluate', description=description, help=description)
        add_evaluate_arguments(self.evaluate_parser, False)
        add_metric_arguments(self.evaluate_parser, self.metric_type)
        add_dataset_reader_arguments(self.evaluate_parser)
        self.evaluate_parser.set_defaults(func=self.run_evaluate)

        description = f'Run "score" with the "{self.name}" metric.'
        self.score_parser = subparsers.add_parser('score', description=description, help=description)
        add_score_arguments(self.score_parser, False)
        add_metric_arguments(self.score_parser, self.metric_type)
        add_dataset_reader_arguments(self.score_parser)
        self.score_parser.set_defaults(func=self.run_score)

    def run_evaluate(self, args: argparse.Namespace) -> None:
        prepare_global_logging(file_path=args.log_file, silent=args.silent)

        import_module_and_submodules('sacrerouge')
        include_packages = args.include_packages or []
        for package in include_packages:
            import_module_and_submodules(package)

        dataset_reader = get_dataset_reader_from_argument(args.dataset_reader)
        metric = get_metric_from_arguments(self.metric_type, args)
        input_files = args.input_files

        instances = dataset_reader.read(*input_files)
        macro, micro_list = evaluate_instances(instances, [metric])

        save_evaluation_results(macro, micro_list, args.macro_output_json, args.micro_output_jsonl, args.silent)

    def run_score(self, args: argparse.Namespace) -> None:
        prepare_global_logging(file_path=args.log_file, silent=args.silent)

        import_module_and_submodules('sacrerouge')
        include_packages = args.include_packages or []
        for package in include_packages:
            import_module_and_submodules(package)

        dataset_reader = get_dataset_reader_from_argument(args.dataset_reader)
        metric = get_metric_from_arguments(self.metric_type, args)
        input_files = args.input_files

        instances = dataset_reader.read(*input_files)
        metrics_dicts = score_instances(instances, [metric], args.disable_peer_jackknifing)

        save_score_results(metrics_dicts, args.output_jsonl, args.silent)