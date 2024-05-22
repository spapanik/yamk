from unittest import mock

from yamk import __main__


@mock.patch("sys.argv", ["yamk", "phony"])
def test_parse_args() -> None:
    args = __main__.parse_args()
    assert args.target == "phony"


@mock.patch("sys.argv", ["yamk", "phony"])
@mock.patch("yamk.__main__.MakeCommand")
def test_main(mock_make: mock.MagicMock) -> None:
    __main__.main()
    assert mock_make.call_count == 1
    assert mock_make().make.call_count == 1
