from unittest import mock

import pytest

from yamk.lib.cli import parse_args


@mock.patch("sys.argv", ["yamk", "target"])
def test_parse_target() -> None:
    args = parse_args()
    assert args.target == "target"


@pytest.mark.parametrize(
    ("verbose", "expected_verbosity"), [("-v", 1), ("-vv", 2), ("-vvvvv", 5)]
)
def test_yamk_verbosity(verbose: str, expected_verbosity: int) -> None:
    with mock.patch("sys.argv", ["yamk", verbose, "target"]):
        args = parse_args()

    assert args.verbosity == expected_verbosity
