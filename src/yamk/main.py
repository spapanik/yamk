import argparse
import sys

from yamk import __version__
from yamk.make import MakeCommand

sys.tracebacklimit = 0


def parse_args():
    parser = argparse.ArgumentParser(
        prog="yamk", description="Yet another make command",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Print the version and exit",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increae the level of verbosity",
    )
    parser.add_argument(
        "-m",
        "--makefile",
        metavar="Makefile",
        default="make.toml",
        help="The path to makefile",
    )
    parser.add_argument(
        "-x",
        "--variable",
        action="append",
        metavar="KEY=value",
        dest="variables",
        default=[],
        help="A list of variables to override the ones set in the makefile. "
        "They should be in the form <variable>=<value>",
    )
    parser.add_argument(
        "target", nargs="?", default="all", help="The target for yamk",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    MakeCommand(args).make()
