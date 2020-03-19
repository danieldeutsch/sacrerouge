import argparse
from overrides import overrides

from sacrerouge.commands import Subcommand
from sacrerouge.datasets.duc_tac import duc2005, duc2006


class SetupSubcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('setup')
        subparsers = self.parser.add_subparsers()

        subcommands = [
            duc2005.DUC2005Subcommand(),
            duc2006.DUC2006Subcommand()
        ]
        for subcommand in subcommands:
            subcommand.add_subparser(subparsers)

        self.parser.set_defaults(func=self.setup)

    @overrides
    def setup(self, args):
        if 'subfunc' in dir(args):
            args.subfunc(args)
        else:
            self.parser.print_help()
