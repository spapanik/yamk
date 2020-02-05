from unittest import mock

import pytest

from yamk import make

from tests.settings import TESTS_ROOT


class TestMakeCommand:
    @staticmethod
    @mock.patch("yamk.make.open", new_callable=mock.mock_open, read_data="")
    def test_make_raises_on_missing_target(_mock_obj):
        args = mock.MagicMock()
        args.target = "phony"
        make_command = make.MakeCommand(args)
        with pytest.raises(ValueError):
            make_command.make()

    @staticmethod
    @mock.patch("yamk.make.subprocess.run")
    def test_make_builds_with_no_commands(runner):
        args = mock.MagicMock()
        args.target = "phony"
        args.makefile = TESTS_ROOT.joinpath("data", "empty_phony.toml")
        make_command = make.MakeCommand(args)
        make_command.make()
        runner.assert_not_called()

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_builds_with_two_commands(runner):
        args = mock.MagicMock()
        args.target = "phony"
        args.makefile = TESTS_ROOT.joinpath("data", "two_commands.toml")
        make_command = make.MakeCommand(args)
        make_command.make()
        assert runner.call_count == 2

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_extra_vars(runner):
        args = mock.MagicMock()
        args.target = "phony"
        args.makefile = TESTS_ROOT.joinpath("data", "extra_vars.toml")
        make_command = make.MakeCommand(args)
        make_command.make()
        runner.assert_called_once_with("echo this/phony.txt", shell=True)
