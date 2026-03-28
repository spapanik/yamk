from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypedDict
from unittest import mock

from yamk.command.make import MakeCommand

if TYPE_CHECKING:
    from typing_extensions import Unpack  # upgrade: py3.10: import from typing

TEST_DATA_ROOT = Path(__file__).resolve().parent.joinpath("data")
TEST_COOKBOOK = TEST_DATA_ROOT.joinpath("mk.toml")
DEFAULT_VALUES: MakeCommandArgs = {
    "bare": False,
    "cookbook": TEST_COOKBOOK,
    "cookbook_type": None,
    "dry_run": False,
    "echo_override": False,
    "extra": [],
    "force_make": False,
    "print_timing_report": False,
    "retries": 0,
    "shell": None,
    "up_to_date": [],
    "variables": {},
    "verbosity": 0,
}


class MakeCommandArgs(TypedDict, total=False):
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
    up_to_date: list[str]
    variables: dict[str, str]
    verbosity: int


def runner_exit_success() -> mock.MagicMock:
    return mock.MagicMock(return_value=mock.MagicMock(returncode=0))


def runner_exit_failure() -> mock.MagicMock:
    return mock.MagicMock(return_value=mock.MagicMock(returncode=42))


def get_make_command(
    target: str, cookbook_name: str | None = None, **kwargs: Unpack[MakeCommandArgs]
) -> MakeCommand:
    if cookbook_name:
        kwargs["cookbook"] = TEST_DATA_ROOT.joinpath(cookbook_name)

    make_args = DEFAULT_VALUES.copy()
    make_args.update(kwargs)

    return MakeCommand(target, **make_args)
