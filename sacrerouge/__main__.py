import argparse

from sacrerouge.commands import correlate, evaluate, score, setup_dataset, setup_metric
from sacrerouge.common import command_registry


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    cr = command_registry.CommandRegistry("sacrerouge")

    subcommands = [
        correlate.CorrelateSubcommand(cr, []),##
        evaluate.EvaluateSubcommand(cr, []),##
        score.ScoreSubcommand(cr, []),##
        setup_dataset.SetupDatasetSubcommand(cr, []),##
        setup_metric.SetupMetricSubcommand(cr, [])##
    ]
    #for subcommand in subcommands:
    #    subcommand.add_subparser(subparsers)

    dynamic_parser = cr.create_parser()

    #args = parser.parse_args()
    args = dynamic_parser.parse_args()
    print(args)
    if 'func' in dir(args):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
