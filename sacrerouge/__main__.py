import argparse

from sacrerouge.commands import correlate, evaluate, score, setup_dataset


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subcommands = [
        correlate.CorrelateSubcommand(),
        evaluate.EvaluateSubcommand(),
        score.ScoreSubcommand(),
        setup_dataset.SetupDatasetSubcommand(),
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
