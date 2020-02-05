import os
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
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=42))
    def test_make_builds_wrong_command_breaks(runner):
        args = mock.MagicMock()
        args.target = "failure"
        args.makefile = TESTS_ROOT.joinpath("data", "wrong_commands.toml")
        make_command = make.MakeCommand(args)
        with pytest.raises(SystemExit) as exc:
            make_command.make()
        assert exc.value.code == 42
        assert runner.call_count == 1

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=42))
    def test_make_builds_wrong_command_with_allowed_failure(runner):
        args = mock.MagicMock()
        args.target = "allowed_failure"
        args.makefile = TESTS_ROOT.joinpath("data", "wrong_commands.toml")
        make_command = make.MakeCommand(args)
        make_command.make()
        assert runner.call_count == 2

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=42))
    def test_make_builds_wrong_command_with_allowed_failure_in_command(runner):
        args = mock.MagicMock()
        args.target = "allowed_failure_in_command"
        args.makefile = TESTS_ROOT.joinpath("data", "wrong_commands.toml")
        make_command = make.MakeCommand(args)
        make_command.make()
        assert runner.call_count == 1

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_extra_vars(runner):
        args = mock.MagicMock()
        args.target = "phony"
        args.makefile = TESTS_ROOT.joinpath("data", "extra_vars.toml")
        make_command = make.MakeCommand(args)
        make_command.make()
        runner.assert_called_once_with("echo this/phony.txt", shell=True)

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_strong_var(runner):
        os.environ["FOO"] = "FOO"
        os.environ["BAR"] = "BAR"
        args = mock.MagicMock()
        args.target = "strong_var"
        args.makefile = TESTS_ROOT.joinpath("data", "extra_vars.toml")
        make_command = make.MakeCommand(args)
        make_command.make()
        runner.assert_called_once_with("echo foo BAR", shell=True)

    @staticmethod
    @mock.patch("yamk.make.print", new_callable=mock.MagicMock)
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_echo_in_recipe(runner, mock_print):
        args = mock.MagicMock()
        args.target = "echo"
        args.makefile = TESTS_ROOT.joinpath("data", "echo_command.toml")
        make_command = make.MakeCommand(args)
        make_command.make()
        mock_print.assert_called_once_with("ls")
        assert runner.call_count == 1

    @staticmethod
    @mock.patch("yamk.make.print", new_callable=mock.MagicMock)
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_echo_in_command(runner, mock_print):
        args = mock.MagicMock()
        args.target = "echo_in_command"
        args.makefile = TESTS_ROOT.joinpath("data", "echo_command.toml")
        make_command = make.MakeCommand(args)
        make_command.make()
        mock_print.assert_called_once_with("ls")
        assert runner.call_count == 1
