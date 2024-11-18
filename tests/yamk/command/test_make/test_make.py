import os
from unittest import mock

from yamk.command import make


@mock.patch("yamk.command.make.subprocess.run")
def test_make_builds_with_no_commands(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "phony"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 0


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
def test_make_with_existence_command(
    runner: mock.MagicMock, mock_args: mock.MagicMock
) -> None:
    mock_args.target = "existence_command"
    make_command = make.MakeCommand(mock_args)
    make_command.make()
    assert runner.call_count == 2
    assert runner.call_args_list == [
        mock.call(
            "sub", capture_output=True, text=True, **make_command.subprocess_kwargs
        ),
        mock.call("ls", **make_command.subprocess_kwargs),
    ]


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
