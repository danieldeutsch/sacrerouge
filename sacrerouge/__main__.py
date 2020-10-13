from sacrerouge import build_argument_parser


def main():
    parser = build_argument_parser()
    args = parser.parse_args()
    if 'func' in dir(args):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
