import argparse
import sys
import warnings

from yamk import __version__
from yamk.lib import RemovedInYam3, change_default
from yamk.make import MakeCommand

sys.tracebacklimit = 0


def parse_args():
    parser = argparse.ArgumentParser(
        prog="yamk", description="Yet another make command"
    )

    # positional arguments
    parser.add_argument("target", nargs="?", default="all", help="the target for yamk")

    # optional arguments
    parser.add_argument(
        "-d",
        "--directory",
        metavar="dir",
        default=".",
        help="the path to the directory that contains the makefile",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="rebuild all dependencies and the target",
    )
    parser.add_argument(
        "--change-default",
        action="store_true",
        help="build a cookbook.yml out of make.toml and exit",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-m",
        "--makefile",
        metavar="Makefile",
        help="the path to the makefile",
    )
    group.add_argument(
        "-c",
        "--cookbook",
        metavar="cookbook",
        help="the path to the cookbook",
    )
    parser.add_argument(
        "-s",
        "--shell",
        metavar="shell",
        help="the path to the shell used to execute the commands",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="print the version and exit",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="increase the level of verbosity",
    )
    parser.add_argument(
        "-x",
        "--variable",
        action="append",
        metavar="KEY=value",
        dest="variables",
        default=[],
        help="a list of variables to override the ones set in the makefile, "
        "which should be in the form <variable>=<value>",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    if args.makefile is not None:
        warnings.warn(
            "Using -m/--makefile is deprecated, and will be removed in yamk 3.0. "
            "Use -c/--cookbook instead.",
            RemovedInYam3,
        )
        args.cookbook = args.makefile
        args.makefile = None
    if args.change_default:
        change_default(args)
        return
    MakeCommand(args).make()
