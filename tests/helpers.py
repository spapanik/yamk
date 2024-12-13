from __future__ import annotations

from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict
from unittest import mock

from yamk.command.make import MakeCommand

if TYPE_CHECKING:
    from typing_extensions import Unpack  # upgrade: py3.10: import from typing

TEST_DATA_ROOT = Path(__file__).resolve().parent.joinpath("data")
TEST_COOKBOOK = TEST_DATA_ROOT.joinpath("mk.toml")
DEFAULT_VALUES = {
    "directory": ".",
    "cookbook": TEST_COOKBOOK,
    "cookbook_type": None,
    "verbosity": 0,
    "retries": 0,
    "bare": False,
    "time": False,
    "force": False,
    "dry_run": False,
    "extra": [],
}


class MakeCommandArgs(TypedDict, total=False):
    directory: str
    cookbook: Path
    cookbook_name: str
    cookbook_type: str | None
    verbosity: int
    retries: int
    bare: bool
    time: bool
    force: bool
    dry_run: bool
    extra: list[str]
    target: str
    variables: list[str]


def runner_exit_success() -> mock.MagicMock:
    return mock.MagicMock(return_value=mock.MagicMock(returncode=0))


def runner_exit_failure() -> mock.MagicMock:
    return mock.MagicMock(return_value=mock.MagicMock(returncode=42))


def get_make_command(**kwargs: Unpack[MakeCommandArgs]) -> MakeCommand:
    if cookbook_name := kwargs.pop("cookbook_name"):
        kwargs["cookbook"] = TEST_DATA_ROOT.joinpath(cookbook_name)

    mock_args = mock.MagicMock()
    items = chain(DEFAULT_VALUES.items(), kwargs.items())
    for key, value in items:
        setattr(mock_args, key, value)

    return MakeCommand(mock_args)
