import argparse
from overrides import overrides

from sacrerouge.common import Registrable
from sacrerouge.commands import RootSubcommand, MetricSetupSubcommand


@RootSubcommand.register('setup-metric')
class SetupMetricSubcommand(RootSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup an evaluation metric'
        self.parser = parser.add_parser('setup-metric', description=description, help=description)
        subparsers = self.parser.add_subparsers()

        # Add all of the metric setup commands using the registry
        for name, (cls_, _) in sorted(Registrable._registry[MetricSetupSubcommand].items()):
            cls_().add_subparser(subparsers)

        self.parser.set_defaults(func=self.run)

    @overrides
    def run(self, args):
        if 'subfunc' in dir(args):
            args.subfunc(args)
        else:
            self.parser.print_help()
