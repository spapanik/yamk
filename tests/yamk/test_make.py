import os
from unittest import mock

import pytest

from yamk import make

from tests.settings import TEST_MAKEFILE


class TestMakeCommand:
    @staticmethod
    def test_make_raises_on_missing_target():
        args = mock.MagicMock()
        args.target = "missing_target"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        with pytest.raises(ValueError):
            make_command.make()

    @staticmethod
    def test_make_raises_on_missing_requirement():
        args = mock.MagicMock()
        args.target = "missing_requirement"
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
            "echo /path/to/local/conf/local.service.d/service.conf",
            shell=True,
            cwd=TEST_MAKEFILE.parent,
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
        runner.assert_called_once_with("echo 42", shell=True, cwd=TEST_MAKEFILE.parent)

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_with_requirements(runner):
        args = mock.MagicMock()
        args.target = "requires"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.make()
        assert runner.call_count == 2
        calls = [
            mock.call("ls", shell=True, cwd=TEST_MAKEFILE.parent),
            mock.call("true", shell=True, cwd=TEST_MAKEFILE.parent),
        ]
        runner.assert_has_calls(calls)

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_with_implicit_variables(runner):
        args = mock.MagicMock()
        args.target = "implicit_vars"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.make()
        assert runner.call_count == 2
        calls = [
            mock.call("echo implicit_vars", shell=True, cwd=TEST_MAKEFILE.parent),
            mock.call("echo / phony", shell=True, cwd=TEST_MAKEFILE.parent),
        ]
        runner.assert_has_calls(calls)

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_with_phony_and_keep_ts_newer_requirement(runner):
        args = mock.MagicMock()
        args.target = "keep_ts"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.phony_dir.mkdir(exist_ok=True)
        make_command.phony_dir.joinpath("keep_ts").touch()
        os.utime(make_command.phony_dir, times=(1, 3))
        os.utime(make_command.phony_dir.joinpath("keep_ts"), times=(1, 2))
        make_command.make()
        runner.assert_called_once_with("ls", shell=True, cwd=TEST_MAKEFILE.parent)

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_with_phony_and_keep_ts_older_requirement(runner):
        args = mock.MagicMock()
        args.target = "keep_ts"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.phony_dir.mkdir(exist_ok=True)
        make_command.phony_dir.joinpath("keep_ts").touch()
        os.utime(make_command.phony_dir, times=(2, 3))
        os.utime(make_command.phony_dir.joinpath("keep_ts"), times=(1, 5))
        make_command.make()
        runner.assert_not_called()

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_with_phony_and_keep_ts_missing_ts(runner):
        args = mock.MagicMock()
        args.target = "keep_ts"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.phony_dir.mkdir(exist_ok=True)
        make_command.phony_dir.joinpath("keep_ts").unlink(missing_ok=True)
        make_command.make()
        runner.assert_called_once_with("ls", shell=True, cwd=TEST_MAKEFILE.parent)

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_with_dag_target(runner):
        args = mock.MagicMock()
        args.target = "dag_target"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.make()
        runner.assert_called_once_with("ls", shell=True, cwd=TEST_MAKEFILE.parent)

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_with_exists_only_target_existing(runner):
        args = mock.MagicMock()
        args.target = "exists_only"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.base_dir.joinpath(args.target).touch()
        make_command.make()
        runner.assert_not_called()

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_with_exists_only_target_missing(runner):
        args = mock.MagicMock()
        args.target = "exists_only"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.base_dir.joinpath(args.target).unlink(missing_ok=True)
        make_command.make()
        runner.assert_called_once_with("ls", shell=True, cwd=TEST_MAKEFILE.parent)

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_build_due_to_requirement(runner):
        args = mock.MagicMock()
        args.target = "requires_build"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        make_command.phony_dir.joinpath("keep_ts").unlink(missing_ok=True)
        make_command.base_dir.joinpath(args.target).touch()
        make_command.make()
        assert runner.call_count == 2
        calls = [
            mock.call("ls", shell=True, cwd=TEST_MAKEFILE.parent),
            mock.call("echo 42", shell=True, cwd=TEST_MAKEFILE.parent),
        ]
        runner.assert_has_calls(calls)

    @staticmethod
    @mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
    def test_make_with_recursive_requirement(runner):
        args = mock.MagicMock()
        args.target = "recursive_requirement"
        args.makefile = TEST_MAKEFILE
        make_command = make.MakeCommand(args)
        recursive_dir = make_command.base_dir.joinpath("dir")
        recursive_dir.mkdir(exist_ok=True)
        recursive_dir.joinpath("file_in_dir").touch()
        os.utime(recursive_dir, times=(1, 2))
        os.utime(recursive_dir.joinpath("file_in_dir"), times=(1, 4))
        make_command.make()
        runner.assert_called_once_with("ls", shell=True, cwd=TEST_MAKEFILE.parent)
