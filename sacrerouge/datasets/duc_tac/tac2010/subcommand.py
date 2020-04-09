import argparse
from overrides import overrides

from sacrerouge.datasets.duc_tac.tac2010 import metrics, pyramids, task1
from sacrerouge.commands import Subcommand


class TAC2010Subcommand(Subcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        self.parser = parser.add_parser('tac2010')
        self.parser.add_argument('data_root')
        self.parser.add_argument('output_dir')
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        task1.setup(args.data_root, args.output_dir)
        metrics.setup(args.data_root, args.output_dir)
        pyramids.setup(args.data_root, args.output_dir)
