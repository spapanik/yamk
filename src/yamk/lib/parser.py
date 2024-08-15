import sys
from argparse import REMAINDER, ArgumentParser, BooleanOptionalAction, Namespace

from yamk.__version__ import __version__
from yamk.lib.utils import SUPPORTED_FILE_EXTENSIONS

sys.tracebacklimit = 0


def parse_args() -> Namespace:
    parser = ArgumentParser(description="Yet another make command")
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
        dest="verbosity",
        help="increase the level of verbosity",
    )

    parser.add_argument("target", help="the target for yam")

    parser.add_argument(
        "-a",
        "--assume",
        action="append",
        metavar="dependency",
        default=[],
        help="assume that dependency is up to date (works only with phony ones)",
    )
    parser.add_argument(
        "-b",
        "--bare",
        action="store_true",
        help="build only the target, without checking the dependencies",
    )
    parser.add_argument(
        "-c",
        "--cookbook",
        metavar="cookbook",
        help="the path to the cookbook",
    )
    parser.add_argument(
        "-d",
        "--directory",
        metavar="dir",
        default=".",
        help="the path to the directory that contains the cookbook",
    )
    parser.add_argument(
        "-e",
        "--echo",
        action=BooleanOptionalAction,
        help="a boolean flag to enable or disable the echo of the commands",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="rebuild all dependencies and the target",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="only print the commands to be executed",
    )
    parser.add_argument(
        "-r",
        "--retries",
        metavar="retries",
        type=int,
        default=0,
        help="retry commands for <retries> number of times",
    )
    parser.add_argument(
        "-s",
        "--shell",
        metavar="shell",
        help="the path to the shell used to execute the commands",
    )
    parser.add_argument(
        "-t",
        "--cookbook-type",
        choices=set(SUPPORTED_FILE_EXTENSIONS.values()),
        help="the type of the cookbook. defaults to file extension",
    )
    parser.add_argument(
        "-T",
        "--time",
        action="store_true",
        help="print a timing report",
    )
    parser.add_argument(
        "-x",
        "--variable",
        action="append",
        metavar="KEY=value",
        dest="variables",
        default=[],
        help="a list of variables to override the ones set in the cookbook, "
        "which should be in the form <variable>=<value>",
    )

    parser.add_argument(
        "extra",
        nargs=REMAINDER,
        help="extra args to be passed to the recipe",
    )

    args = parser.parse_args()
    if args.verbosity > 0:
        sys.tracebacklimit = 1000

    return args
