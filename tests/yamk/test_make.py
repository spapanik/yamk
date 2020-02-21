import os
from unittest import mock

import pytest

from yamk import make

from tests.settings import TEST_MAKEFILE


class TestMakeCommand:
    @staticmethod
    @mock.patch("yamk.make.open", new_callable=mock.mock_open, read_data="")
    def test_make_raises_on_missing_target(_mock_obj):
        args = mock.MagicMock()
        args.target = "missing_target"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        with pytest.raises(ValueError):
            make_command.make()

    @staticmethod
    @mock.patch("yamk.make.subprocess.run")
    def test_make_builds_with_no_commands(runner):
        args = mock.MagicMock()
        args.target = "phony"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.make()
        runner.assert_not_called()

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_builds_with_two_commands(runner):
        args = mock.MagicMock()
        args.target = "two_commands"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.make()
        assert runner.call_count == 2

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=42))
    def test_make_builds_wrong_command_breaks(runner):
        args = mock.MagicMock()
        args.target = "failure"
        args.makefile = TEST_MAKEFILE
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
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.make()
        assert runner.call_count == 2

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=42))
    def test_make_builds_wrong_command_with_allowed_failure_in_command(runner):
        args = mock.MagicMock()
        args.target = "allowed_failure_in_command"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.make()
        assert runner.call_count == 1

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_extra_vars(runner):
        os.environ["filename"] = "service.conf"
        os.environ["conf_dir"] = "service.d"
        args = mock.MagicMock()
        args.target = "variables"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.make()
        runner.assert_called_once_with(
            "echo /path/to/local/conf/local.service.d/service.conf", shell=True
        )

    @staticmethod
    @mock.patch("yamk.make.print", new_callable=mock.MagicMock)
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_echo_in_recipe(runner, mock_print):
        args = mock.MagicMock()
        args.target = "echo"
        args.makefile = TEST_MAKEFILE
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
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.make()
        mock_print.assert_called_once_with("ls")
        assert runner.call_count == 1

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_alias(runner):
        args = mock.MagicMock()
        args.target = "alias"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.make()
        assert runner.call_count == 2

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_regex_target(runner):
        args = mock.MagicMock()
        args.target = "regex_42"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.make()
        runner.assert_called_once_with("echo 42", shell=True)
