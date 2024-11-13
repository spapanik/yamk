import pathlib
from itertools import chain
from typing import Any
from unittest import mock

import pytest

from yamk.command.make import MakeCommand

TEST_DATA_ROOT = pathlib.Path(__file__).resolve().parent.joinpath("data")
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


def runner_exit_success() -> mock.MagicMock:
    return mock.MagicMock(return_value=mock.MagicMock(returncode=0))


def get_make_command(**kwargs: Any) -> MakeCommand:
    if cookbook_name := kwargs.pop("cookbook_name"):
        kwargs["cookbook"] = TEST_DATA_ROOT.joinpath(cookbook_name)

    mock_args = mock.MagicMock()
    items = chain(DEFAULT_VALUES.items(), kwargs.items())
    for key, value in items:
        setattr(mock_args, key, value)

    return MakeCommand(mock_args)


@pytest.fixture
def mock_args() -> mock.MagicMock:
    args = mock.MagicMock()
    args.directory = "."
    args.cookbook = TEST_COOKBOOK
    args.cookbook_type = None
    args.verbosity = 0
    args.bare = False
    args.time = False
    args.force = False
    args.dry_run = False
    args.extra = []
    return args
