import os
from contextlib import suppress
from unittest import mock

import pytest

from yamk import make


def test_make_raises_on_missing_target(mock_args):
    mock_args.target = "missing_target"
    make_command = make.MakeCommand(mock_args)
    assert pytest.raises(ValueError, make_command.make)


def test_make_raises_on_missing_requirement(mock_args):
    mock_args.target = "missing_requirement"
    make_command = make.MakeCommand(mock_args)
    assert pytest.raises(ValueError, make_command.make)


@mock.patch("yamk.make.subprocess.run")
def test_make_builds_with_no_commands(runner, mock_args):
    mock_args.target = "phony"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 0


@mock.patch("yamk.make.print", new_callable=mock.MagicMock)
def test_make_verbosity(mock_print, mock_args):
    mock_args.target = "phony"
    mock_args.verbose = 4
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert mock_print.call_count == 8
    calls = [
        mock.call(mock_args),
        mock.call("=== all targets ==="),
        mock.call("- phony:"),
        mock.call("    timestamp: 9999-12-31 23:59:59.999999"),
        mock.call("    should_build: True"),
        mock.call("    requires: set()"),
        mock.call("    required_by: set()"),
        mock.call("=== target: phony ==="),
    ]
    assert mock_print.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_builds_with_two_commands(runner, mock_args):
    mock_args.target = "two_commands"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=42))
def test_make_builds_wrong_command_breaks(runner, mock_args):
    mock_args.target = "failure"
    make_command = make.MakeCommand(mock_args)
    error = pytest.raises(SystemExit, make_command.make)
    assert error
    assert error.value.code == 42
    assert runner.call_count == 1
    calls = [mock.call("false", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=42))
def test_make_allowed_failure(runner, mock_args):
    mock_args.target = "allowed_failure"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("false", **make_command.subprocess_kwargs),
        mock.call("ls", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=42))
def test_make_allowed_failure_in_command(runner, mock_args):
    mock_args.target = "allowed_failure_in_command"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("false", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_extra_vars(runner, mock_args):
    os.environ["prefix"] = ""
    os.environ["dir"] = "generic.d"
    mock_args.target = "variables"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [
        mock.call("echo /etc/service.d/service.conf", **make_command.subprocess_kwargs)
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.print", new_callable=mock.MagicMock)
@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_echo_in_recipe(runner, mock_print, mock_args):
    mock_args.target = "echo"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert mock_print.call_count == 1
    calls = [mock.call("ls -l")]
    assert mock_print.call_args_list == calls
    assert runner.call_count == 1
    calls = [mock.call("ls -l", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.print", new_callable=mock.MagicMock)
@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_echo_in_command(runner, mock_print, mock_args):
    mock_args.target = "echo_in_command"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert mock_print.call_count == 1
    calls = [mock.call("ls")]
    assert mock_print.call_args_list == calls
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_alias(runner, mock_args):
    mock_args.target = "alias"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_variable_in_name(runner, mock_args):
    mock_args.target = "call"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_regex_file_target(runner, mock_args):
    mock_args.target = "file_1024.txt"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls file_1024.txt", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_multiple_regex_targets(runner, mock_args):
    mock_args.target = "multiple_regex"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls file_42.txt", **make_command.subprocess_kwargs),
        mock.call("ls file_1024.txt", **make_command.subprocess_kwargs),
    ]
    assert sorted(runner.call_args_list) == sorted(calls)


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_requirements(runner, mock_args):
    mock_args.target = "requires"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
        mock.call("true", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_implicit_variables(runner, mock_args):
    mock_args.target = "implicit_vars"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo implicit_vars", **make_command.subprocess_kwargs),
        mock.call("echo / phony", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_phony_and_keep_ts_newer_requirement(runner, mock_args):
    mock_args.target = "keep_ts"
    make_command = make.MakeCommand(mock_args)
    make_command.phony_dir.mkdir(exist_ok=True)
    make_command.phony_dir.joinpath("keep_ts").touch()
    os.utime(make_command.phony_dir, times=(1, 3))
    os.utime(make_command.phony_dir.joinpath("keep_ts"), times=(1, 2))
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_phony_and_keep_ts_older_requirement(runner, mock_args):
    mock_args.target = "keep_ts"
    make_command = make.MakeCommand(mock_args)
    make_command.phony_dir.mkdir(exist_ok=True)
    make_command.phony_dir.joinpath("keep_ts").touch()
    os.utime(make_command.phony_dir, times=(2, 3))
    os.utime(make_command.phony_dir.joinpath("keep_ts"), times=(1, 5))
    make_command.make()
    assert runner.call_count == 0


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_phony_and_keep_ts_older_requirement_and_force(runner, mock_args):
    mock_args.target = "keep_ts"
    mock_args.force = True
    make_command = make.MakeCommand(mock_args)
    make_command.phony_dir.mkdir(exist_ok=True)
    make_command.phony_dir.joinpath("keep_ts").touch()
    os.utime(make_command.phony_dir, times=(2, 3))
    os.utime(make_command.phony_dir.joinpath("keep_ts"), times=(1, 5))
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_phony_and_keep_ts_missing_ts(runner, mock_args):
    mock_args.target = "keep_ts"
    make_command = make.MakeCommand(mock_args)
    make_command.phony_dir.mkdir(exist_ok=True)
    with suppress(FileNotFoundError):
        # python 3.8: add missing_ok
        make_command.phony_dir.joinpath("keep_ts").unlink()
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_dag_target(runner, mock_args):
    mock_args.target = "dag_target_1"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 5
    calls = [
        mock.call("echo dag_target_3", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_5", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_2", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_4", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_1", **make_command.subprocess_kwargs),
    ]
    assert sorted(runner.call_args_list) == sorted(calls)


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_exists_only_target_existing(runner, mock_args):
    mock_args.target = "exists_only"
    make_command = make.MakeCommand(mock_args)
    make_command.base_dir.joinpath(mock_args.target).touch()
    make_command.make()
    assert runner.call_count == 0


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_exists_only_target_missing(runner, mock_args):
    mock_args.target = "exists_only"
    make_command = make.MakeCommand(mock_args)
    with suppress(FileNotFoundError):
        # python 3.8: add missing_ok
        make_command.base_dir.joinpath(mock_args.target).unlink()
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_build_due_to_requirement(runner, mock_args):
    mock_args.target = "requires_build"
    make_command = make.MakeCommand(mock_args)
    with suppress(FileNotFoundError):
        # python 3.8: add missing_ok
        make_command.phony_dir.joinpath("keep_ts").unlink()
    make_command.base_dir.joinpath(mock_args.target).touch()
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_recursive_requirement(runner, mock_args):
    mock_args.target = "recursive_requirement"
    make_command = make.MakeCommand(mock_args)
    recursive_dir = make_command.base_dir.joinpath("dir")
    recursive_dir.mkdir(exist_ok=True)
    recursive_dir.joinpath("file_in_dir").touch()
    os.utime(recursive_dir, times=(1, 2))
    os.utime(recursive_dir.joinpath("file_in_dir"), times=(1, 4))
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_nested_requires(runner, mock_args):
    mock_args.target = "nested_requires"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo one", **make_command.subprocess_kwargs),
        mock.call("echo two", **make_command.subprocess_kwargs),
    ]
    assert sorted(runner.call_args_list) == sorted(calls)


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_sort_variable(runner, mock_args):
    mock_args.target = "sort_variable"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    path = make_command.base_dir.joinpath("mk.toml").as_posix()
    calls = [mock.call(f"echo {path}", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_sort_function(runner, mock_args):
    mock_args.target = "sort_function"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    path = make_command.base_dir.joinpath("mk.toml").as_posix()
    calls = [mock.call(f"echo {path}", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_pwd(runner, mock_args):
    mock_args.target = "pwd"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    path = make_command.base_dir.as_posix()
    calls = [mock.call(f"echo {path}", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_ternary_if_true(runner, mock_args):
    mock_args.target = "ternary_if_true"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 42", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_ternary_if_false(runner, mock_args):
    mock_args.target = "ternary_if_false"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 1024", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_ternary_if_function(runner, mock_args):
    mock_args.target = "ternary_if_function"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 42", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_substitution(runner, mock_args):
    mock_args.target = "substitute"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo the new version", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_merge(runner, mock_args):
    mock_args.target = "merge"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo one two three four", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.make.subprocess.run", return_value=mock.MagicMock(returncode=0))
def test_make_with_d_override(runner, mock_args):
    mock_args.target = ".d_override"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo tail", **make_command.subprocess_kwargs)]
    assert sorted(runner.call_args_list) == sorted(calls)
