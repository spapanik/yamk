import os
from unittest import mock

from tests.conftest import get_make_command, runner_exit_success

COOKBOOK = "should_build.yaml"


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_phony_and_keep_ts_newer_requirement(runner: mock.MagicMock) -> None:
    target = "keep_ts"
    make_command = get_make_command(cookbook_name=COOKBOOK, target=target)
    make_command.phony_dir.mkdir(exist_ok=True)
    make_command.phony_dir.joinpath(target).touch()
    os.utime(make_command.phony_dir, times=(1, 3))
    os.utime(make_command.phony_dir.joinpath(target), times=(1, 2))
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_phony_and_keep_ts_older_requirement(runner: mock.MagicMock) -> None:
    target = "keep_ts"
    make_command = get_make_command(cookbook_name=COOKBOOK, target=target)
    make_command.phony_dir.mkdir(exist_ok=True)
    make_command.phony_dir.joinpath(target).touch()
    os.utime(make_command.phony_dir, times=(2, 3))
    os.utime(make_command.phony_dir.joinpath(target), times=(1, 5))
    make_command.make()
    assert runner.call_count == 0


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_phony_and_keep_ts_older_requirement_and_force(
    runner: mock.MagicMock,
) -> None:
    target = "keep_ts"
    make_command = get_make_command(cookbook_name=COOKBOOK, target=target, force=True)
    make_command.phony_dir.mkdir(exist_ok=True)
    make_command.phony_dir.joinpath(target).touch()
    os.utime(make_command.phony_dir, times=(2, 3))
    os.utime(make_command.phony_dir.joinpath(target), times=(1, 5))
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_phony_and_keep_ts_missing_ts(runner: mock.MagicMock) -> None:
    target = "keep_ts"
    make_command = get_make_command(cookbook_name=COOKBOOK, target=target)
    make_command.phony_dir.mkdir(exist_ok=True)
    make_command.phony_dir.joinpath(target).unlink(missing_ok=True)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_exists_only_target_existing(runner: mock.MagicMock) -> None:
    target = "exists_only"
    make_command = get_make_command(cookbook_name=COOKBOOK, target=target)
    make_command = get_make_command(cookbook_name=COOKBOOK, target=target)
    make_command.base_dir.joinpath(target).touch()
    make_command.make()
    assert runner.call_count == 0


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_existence_command(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="existence_command")
    make_command.make()
    assert runner.call_count == 2
    assert runner.call_args_list == [
        mock.call(
            "sub", capture_output=True, text=True, **make_command.subprocess_kwargs
        ),
        mock.call("ls", **make_command.subprocess_kwargs),
    ]


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_exists_only_target_missing(runner: mock.MagicMock) -> None:
    target = "exists_only"
    make_command = get_make_command(cookbook_name=COOKBOOK, target=target)
    make_command.base_dir.joinpath(target).unlink(missing_ok=True)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_build_due_to_requirement(runner: mock.MagicMock) -> None:
    target = "requires_build"
    make_command = get_make_command(cookbook_name=COOKBOOK, target=target)
    make_command.phony_dir.joinpath("keep_ts").unlink(missing_ok=True)
    make_command.base_dir.joinpath(target).touch()
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("ls", **make_command.subprocess_kwargs),
        mock.call("echo 42", **make_command.subprocess_kwargs),
    ]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_with_recursive_requirement(runner: mock.MagicMock) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="recursive_requirement"
    )
    recursive_dir = make_command.base_dir.joinpath("dir")
    recursive_dir.mkdir(exist_ok=True)
    recursive_dir.joinpath("file_in_dir").touch()
    os.utime(recursive_dir, times=(1, 2))
    os.utime(recursive_dir.joinpath("file_in_dir"), times=(1, 4))
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("ls", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_nested_requires(runner: mock.MagicMock) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="nested_requires")
    make_command.make()
    assert runner.call_count == 2
    calls = [
        mock.call("echo one", **make_command.subprocess_kwargs),
        mock.call("echo two", **make_command.subprocess_kwargs),
    ]
    assert sorted(runner.call_args_list) == sorted(calls)
