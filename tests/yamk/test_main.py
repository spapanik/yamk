from unittest import mock

from yamk.__main__ import main


@mock.patch("sys.argv", ["yamk", "phony"])
@mock.patch("yamk.__main__.MakeCommand")
def test_main(mock_make: mock.MagicMock) -> None:
    main()
    assert mock_make.call_count == 1
    assert mock_make().make.call_count == 1
