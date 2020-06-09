import argparse
from overrides import overrides

from sacrerouge.datasets.duc_tac.duc2004 import metrics, tasks
from sacrerouge.commands import Subcommand


class DUC2004Subcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('duc2004')
        self.parser.add_argument('data_root')
        self.parser.add_argument('output_dir')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        metrics.setup(args.data_root, args.output_dir)
        tasks.setup(args.data_root, args.output_dir)
