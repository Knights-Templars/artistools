import argparse


def addargs(parser):
    pass


def main(argsraw=None):
    """Show a list of available artistools commands."""
    import argcomplete
    import importlib

    parser = argparse.ArgumentParser()
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = False

    for command, (submodulename, funcname) in sorted(artistools.commandlist.items()):
        submodule = importlib.import_module(submodulename, package='artistools')
        subparser = subparsers.add_parser(command)
        submodule.addargs(subparser)
        subparser.set_defaults(func=getattr(submodule, funcname))

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if args.func is not None:
        args.func(args=args)
    else:
        # parser.print_help()
        print('artistools provides the following commands:\n')

        # for script in sorted(console_scripts):
        #     command = script.split('=')[0].strip()
        #     print(f'  {command}')

        for command in sorted(artistools.commandlist):
            print(f'  {command}')


if __name__ == '__main__':
    # multiprocessing.freeze_support()
    main()