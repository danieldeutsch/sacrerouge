import argparse

from sacrerouge.common import Registrable

class Subcommand(Registrable):
    def add_subparser(self, parser: argparse._SubParsersAction) -> None:
        raise NotImplementedError

    def run(self, args):
        raise NotImplementedError
