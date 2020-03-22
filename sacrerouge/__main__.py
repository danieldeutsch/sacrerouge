import argparse

from sacrerouge.commands import score, setup


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subcommands = [
        score.ScoreSubcommand(),
        setup.SetupSubcommand(),
    ]
    for subcommand in subcommands:
        subcommand.add_subparser(subparsers)

    args = parser.parse_args()
    if 'func' in dir(args):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
