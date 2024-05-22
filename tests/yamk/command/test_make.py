import os
from unittest import mock

import pytest

from yamk.command import make


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def requirement_ext(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "requirement_ext"
    mock_args.variables = ["EXT_VARIABLE=echo"]
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls -l", **make_command.subprocess_kwargs),
        mock.call("echo 'echo'", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_requires_from_env(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "requirement_ext"
    os.environ["EXT_VARIABLE"] = "echo"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls -l", **make_command.subprocess_kwargs),
        mock.call("echo 'echo'", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_requires_from_local(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "requirement_local"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls -l", **make_command.subprocess_kwargs),
        mock.call("echo 'echo'", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_requires_from_regex(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "regex_requirement_echo"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls -l", **make_command.subprocess_kwargs),
        mock.call("echo 'echo'", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_requires_from_global(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "requirement"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls -l", **make_command.subprocess_kwargs),
        mock.call("echo 'echo'", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


def test_make_raises_on_missing_target(mock_args: mock.MagicMock) -> None:
    mock_args.target = "missing_target"
    make_command = make.MakeCommand(mock_args)
    with pytest.raises(ValueError):
        make_command.make()


def test_make_raises_on_missing_requirement(mock_args: mock.MagicMock) -> None:
    mock_args.target = "missing_requirement"
    make_command = make.MakeCommand(mock_args)
    with pytest.raises(ValueError):
        make_command.make()


@mock.patch("yamk.command.make.subprocess.run")
def test_make_builds_with_no_commands(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "phony"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 0


@mock.patch("yamk.command.make.print", new_callable=mock.MagicMock)
def test_make_dry_run(mock_print: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "phony_requirement"
    mock_args.dry_run = True
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert mock_print.call_count == 2
    calls = [
        mock.call("🔧 Running `\x1b[1mls\x1b[0m`"),
        mock.call("✅ `\x1b[1mls\x1b[0m` run successfully!"),
    ]
    assert mock_print.call_args_list == calls


@mock.patch("yamk.command.make.print", new_callable=mock.MagicMock)
def test_make_verbosity(mock_print: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "phony"
    mock_args.verbosity = 4
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert mock_print.call_count == 7
    calls = [
        mock.call("=== all targets ==="),
        mock.call("- phony:"),
        mock.call("    timestamp: end of time"),
        mock.call("    should_build: True"),
        mock.call("    requires: []"),
        mock.call("    required_by: set()"),
        mock.call("=== target: phony ==="),
    ]
    assert mock_print.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_builds_with_two_commands(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "two_commands"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=42)
)
def test_make_builds_wrong_command_breaks(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "failure"
    make_command = make.MakeCommand(mock_args)
    with pytest.raises(SystemExit) as exc_info:
        make_command.make()
    assert exc_info.value.code == 42
    assert runner.call_count == 1
    calls = [mock.call("false", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=42)
)
def test_make_allowed_failure(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "allowed_failure"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("false", **make_command.subprocess_kwargs),
        mock.call("ls", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=42)
)
def test_make_allowed_failure_in_command(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "allowed_failure_in_command"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("false", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_extra_vars(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    os.environ["prefix"] = ""  # noqa: SIM112
    os.environ["dir"] = "/home/user/.config/generic.d"  # noqa: SIM112
    mock_args.target = "variables"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [
        mock.call(
            "echo /home/user/.config/generic.d/service.d/service.conf",
            **make_command.subprocess_kwargs,
        )
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.print", new_callable=mock.MagicMock)
@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_echo_in_recipe(
    runner: mock.MagicMock, mock_print: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "echo"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert mock_print.call_count == 2
    calls = [
        mock.call("🔧 Running `\x1b[1mls -l\x1b[0m`"),
        mock.call("✅ `\x1b[1mls -l\x1b[0m` run successfully!"),
    ]
    assert mock_print.call_args_list == calls
    assert runner.call_count == 1
    calls = [mock.call("ls -l", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.print", new_callable=mock.MagicMock)
@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_echo_in_command(
    runner: mock.MagicMock, mock_print: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "echo_in_command"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert mock_print.call_count == 2
    calls = [
        mock.call("🔧 Running `\x1b[1mls\x1b[0m`"),
        mock.call("✅ `\x1b[1mls\x1b[0m` run successfully!"),
    ]
    assert mock_print.call_args_list == calls
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_alias(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "alias"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_variable_in_name(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "call"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_regex_file_target(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "file_1024.txt"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls file_1024.txt", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_regex_strength(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "echo_42"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [
        mock.call(
            "echo 'The answer to life, the universe, and everything'",
            **make_command.subprocess_kwargs,
        )
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_variable_strength_argument_vs_env(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    os.environ["VARIABLE"] = "env"
    mock_args.target = "variable_strength"
    mock_args.variables = ["VARIABLE=argument"]
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo argument", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_variable_strength_env_vs_local(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    os.environ["VARIABLE"] = "env"
    mock_args.target = "variable_strength"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo env", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_variable_strength_local_vs_regex(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "variable_strength_1024"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 42", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_variable_strength_regex_vs_global(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "variable_strength_1024_v2"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 1024", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_multiple_regex_targets(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "multiple_regex"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls file_42.txt", **make_command.subprocess_kwargs),
        mock.call("ls file_1024.txt", **make_command.subprocess_kwargs),
    ]
    assert sorted(runner.call_args_list) == sorted(calls)


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_requirements(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "requires"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
        mock.call("true", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_implicit_variables(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "implicit_vars"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo implicit_vars", **make_command.subprocess_kwargs),
        mock.call("echo / phony", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_duplicate_requirements_warning(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "duplicate_requirement"
    make_command = make.MakeCommand(mock_args)
    with pytest.warns(RuntimeWarning):
        make_command.make()
    assert runner.call_count == 1
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_phony_and_keep_ts_newer_requirement(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
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


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_phony_and_keep_ts_older_requirement(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "keep_ts"
    make_command = make.MakeCommand(mock_args)
    make_command.phony_dir.mkdir(exist_ok=True)
    make_command.phony_dir.joinpath("keep_ts").touch()
    os.utime(make_command.phony_dir, times=(2, 3))
    os.utime(make_command.phony_dir.joinpath("keep_ts"), times=(1, 5))
    make_command.make()
    assert runner.call_count == 0


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_phony_and_keep_ts_older_requirement_and_force(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
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


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_phony_and_keep_ts_missing_ts(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "keep_ts"
    make_command = make.MakeCommand(mock_args)
    make_command.phony_dir.mkdir(exist_ok=True)
    make_command.phony_dir.joinpath("keep_ts").unlink(missing_ok=True)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_dag_target(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "dag_target_1"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 5
    calls = [
        mock.call("echo dag_target_5", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_2", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_3", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_4", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_1", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_dag_target_no_c3(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "dag_target_no_c3_1"
    make_command = make.MakeCommand(mock_args)
    with pytest.warns(RuntimeWarning):
        make_command.make()
    assert runner.call_count == 5
    calls = [
        mock.call("echo dag_target_no_c3_1", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_no_c3_2", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_no_c3_3", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_no_c3_4", **make_command.subprocess_kwargs),
        mock.call("echo dag_target_no_c3_5", **make_command.subprocess_kwargs),
    ]
    assert sorted(runner.call_args_list) == sorted(calls)


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_exists_only_target_existing(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "exists_only"
    make_command = make.MakeCommand(mock_args)
    make_command.base_dir.joinpath(mock_args.target).touch()
    make_command.make()
    assert runner.call_count == 0


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_exists_only_target_missing(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "exists_only"
    make_command = make.MakeCommand(mock_args)
    make_command.base_dir.joinpath(mock_args.target).unlink(missing_ok=True)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_build_due_to_requirement(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "requires_build"
    make_command = make.MakeCommand(mock_args)
    make_command.phony_dir.joinpath("keep_ts").unlink(missing_ok=True)
    make_command.base_dir.joinpath(mock_args.target).touch()
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_recursive_requirement(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
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


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_nested_requires(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "nested_requires"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo one", **make_command.subprocess_kwargs),
        mock.call("echo two", **make_command.subprocess_kwargs),
    ]
    assert sorted(runner.call_args_list) == sorted(calls)


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_sort_variable(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "sort_variable"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    path = make_command.base_dir.joinpath("mk.toml").as_posix()
    calls = [mock.call(f"echo {path}", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_sort_function(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "sort_function"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    path = make_command.base_dir.joinpath("mk.toml").as_posix()
    calls = [mock.call(f"echo {path}", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_pwd(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "pwd"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    path = make_command.base_dir.as_posix()
    calls = [mock.call(f"echo {path}", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_ternary_if_true(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "ternary_if_true"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 42", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_ternary_if_false(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "ternary_if_false"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 1024", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_ternary_if_function(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "ternary_if_function"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 42", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_substitution(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "substitute"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo the new version", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_merge(runner: mock.MagicMock, mock_args: mock.MagicMock) -> None:
    mock_args.target = "merge"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo one two three four", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_d_override(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = ".d_override"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo tail", **make_command.subprocess_kwargs)]
    assert sorted(runner.call_args_list) == sorted(calls)


@mock.patch(
    "yamk.command.make.subprocess.run", return_value=mock.MagicMock(returncode=0)
)
def test_make_with_d_override_vars(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = ".d_override_vars"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 3
    calls = [
        mock.call("echo 3 4", **make_command.subprocess_kwargs),
        mock.call(
            "echo {'x': 'a', 'y': '2', 'z': 'final'}", **make_command.subprocess_kwargs
        ),
        mock.call("echo 3", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls
