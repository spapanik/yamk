from unittest import mock

from yamk.lib.parser import parse_args


@mock.patch("sys.argv", ["yamk", "phony"])
def test_parse_args() -> None:
    args = parse_args()
    assert args.target == "phony"
