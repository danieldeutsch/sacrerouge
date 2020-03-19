import argparse
from overrides import overrides

from sacrerouge.datasets.duc_tac.duc2007 import metrics, tasks
from sacrerouge.commands import Subcommand


class DUC2007Subcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('duc2007')
        self.parser.add_argument('data_root')
        self.parser.add_argument('output_dir')
        self.parser.set_defaults(subfunc=self.setup)

    @overrides
    def setup(self, args):
        tasks.setup(args.data_root, args.output_dir)
        metrics.setup(args.data_root, args.output_dir)
