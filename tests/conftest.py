import pathlib
from unittest import mock

import pytest

TESTS_ROOT = pathlib.Path(__file__).absolute().parent
TEST_MAKEFILE = TESTS_ROOT.joinpath("data", "mk.toml")


@pytest.fixture()
def mock_args():
    args = mock.MagicMock()
    args.target = "mock_target"
    args.makefile = TEST_MAKEFILE
    args.verbose = 0
    return args
