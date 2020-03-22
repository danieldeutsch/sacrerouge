import argparse


class Subcommand(object):
    def add_subparser(self, parser: argparse._SubParsersAction) -> None:
        raise NotImplementedError

    def run(self, args):
        raise NotImplementedError
