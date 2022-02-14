import pathlib
from unittest import mock

import pytest

TESTS_ROOT = pathlib.Path(__file__).absolute().parent
TEST_COOKBOOK = TESTS_ROOT.joinpath("data", "mk.toml")


@pytest.fixture()
def mock_args():
    args = mock.MagicMock()
    args.target = "mock_target"
    args.directory = "."
    args.cookbook = TEST_COOKBOOK
    args.verbose = 0
    args.force = False
    return args
