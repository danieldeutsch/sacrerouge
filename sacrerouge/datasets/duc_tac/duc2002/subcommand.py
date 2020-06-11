import argparse
from overrides import overrides

from sacrerouge.datasets.duc_tac.duc2002 import tasks
from sacrerouge.commands import Subcommand


class DUC2002Subcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('duc2002')
        self.parser.add_argument('data_root')
        self.parser.add_argument('output_dir')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        tasks.setup(args.data_root, args.output_dir)
