from __future__ import annotations

import sys
from argparse import REMAINDER, ArgumentParser, BooleanOptionalAction
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from yamk.__version__ import __version__
from yamk.lib.utils import SUPPORTED_FILE_EXTENSIONS

if TYPE_CHECKING:
    from argparse import Namespace

    from typing_extensions import Self  # upgrade: py3.10: import from typing


sys.tracebacklimit = 0


@dataclass(slots=True)
class CliArgs:
    bare: bool
    cookbook: Path
    cookbook_type: Literal["json", "yaml", "toml"] | None
    dry_run: bool
    echo_override: bool
    extra: list[str]
    force_make: bool
    print_timing_report: bool
    retries: int
    shell: str | None
    target: str
    up_to_date: list[str]
    variables: dict[str, str]
    verbosity: int

    @classmethod
    def from_args(cls, args: Namespace) -> Self:
        arg_vars = vars(args)
        directory = arg_vars.pop("directory")
        cookbook = arg_vars.pop("cookbook")
        arg_vars["echo_override"] = bool(arg_vars["echo_override"])
        arg_vars["cookbook"] = cls.find_cookbook(directory, cookbook)
        arg_vars["variables"] = dict(
            var.split("=", maxsplit=1) for var in arg_vars["variables"]
        )
        return cls(**arg_vars)

    @staticmethod
    def find_cookbook(directory: str, cookbook: str | None) -> Path:
        absolute_path = Path(directory).absolute()
        if cookbook:
            return absolute_path.joinpath(cookbook)

        candidates = (
            absolute_path.joinpath("cookbook").with_suffix(suffix)
            for suffix in SUPPORTED_FILE_EXTENSIONS
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        msg = f"No candidate cookbook found in {directory}"
        raise FileNotFoundError(msg)


def parse_args() -> CliArgs:
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
        dest="up_to_date",
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
        dest="echo_override",
        help="a boolean flag to enable or disable the echo of the commands",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        dest="force_make",
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
        dest="print_timing_report",
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

    return CliArgs.from_args(args)
