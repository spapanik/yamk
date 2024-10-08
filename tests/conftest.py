import pathlib
from unittest import mock

import pytest

TESTS_ROOT = pathlib.Path(__file__).absolute().parent
TEST_COOKBOOK = TESTS_ROOT.joinpath("data", "mk.toml")


@pytest.fixture
def mock_args() -> mock.MagicMock:
    args = mock.MagicMock()
    args.target = "mock_target"
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
