import argparse
from overrides import overrides

from sacrerouge.common import Registrable
from sacrerouge.commands import RootSubcommand, DatasetSetupSubcommand


@RootSubcommand.register('setup-dataset')
class SetupDatasetSubcommand(RootSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup a dataset'
        self.parser = parser.add_parser('setup-dataset', description=description, help=description)
        subparsers = self.parser.add_subparsers()

        # Add all of the dataset setup commands using the registry
        for name, (cls_, _) in sorted(Registrable._registry[DatasetSetupSubcommand].items()):
            cls_().add_subparser(subparsers)

        self.parser.set_defaults(func=self.run)

    @overrides
    def run(self, args):
        if 'subfunc' in dir(args):
            args.subfunc(args)
        else:
            self.parser.print_help()
