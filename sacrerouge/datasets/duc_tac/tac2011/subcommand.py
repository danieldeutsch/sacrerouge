import argparse
from overrides import overrides

from sacrerouge.datasets.duc_tac.tac2011 import metrics, pyramids, task1
from sacrerouge.commands import Subcommand


class TAC2011Subcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('tac2011')
        self.parser.add_argument('gigaword_root')
        self.parser.add_argument('data_root')
        self.parser.add_argument('output_dir')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        task1.setup(args.gigaword_root, args.data_root, args.output_dir)
        metrics.setup(args.data_root, args.output_dir)
        pyramids.setup(args.data_root, args.output_dir)