from unittest import mock

from yamk import main


@mock.patch("sys.argv", ["yamk", "phony"])
def test_parse_args():
    args = main.parse_args()
    assert args.target == "phony"


@mock.patch("sys.argv", ["yamk", "phony"])
@mock.patch("yamk.main.MakeCommand")
def test_main(mock_make):
    main.main()
    mock_make.assert_called()
    mock_make().make.assert_called()
