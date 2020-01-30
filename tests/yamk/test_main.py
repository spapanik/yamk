from unittest import mock

from yamk import main


@mock.patch("sys.argv", ["yamk"])
def test_main():
    assert main.main() is None
