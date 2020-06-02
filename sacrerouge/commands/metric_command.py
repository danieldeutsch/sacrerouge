import argparse
from overrides import overrides

from sacrerouge.commands import Subcommand
from sacrerouge.metrics import Metric


def add_metric_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Adds a MetricSubcommand for every registered metric."""
    for name, metric in Metric._registry.items():
        command = MetricSubcommand(name, metric)
        command.add_subparser(subparsers)


class MetricSubcommand(Subcommand):
    def __init__(self, name: str, metric: Metric) -> None:
        super().__init__()
        self.name = name
        self.metric = metric

    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser(self.name)

        # Inspect self.metric's constructor and add the corresponding arguments
        # to self.parser. Somehow we might want to combine the default argument logic
        # below with the normal "evaluate" command
        # TODO

        self.parser.add_argument('macro_output_json')
        self.parser.add_argument('micro_output_jsonl')
        self.parser.add_argument('--silent', action='store_true')
        self.parser.add_argument('--overrides')
        self.parser.set_defaults(func=self.run)

    @overrides
    def run(self, args):
        # Run evaluate with this particular metric. It might be smart to refactor
        # the evaluate command code to separate out a function that we can also call here
        pass