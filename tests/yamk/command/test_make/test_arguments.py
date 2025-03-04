import os
from unittest import mock

from tests.helpers import get_make_command, runner_exit_success

COOKBOOK = "arguments.yaml"


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_dry_run(
    runner: mock.MagicMock,
    capsys: mock.MagicMock,  # upgrade: pytest: check for isatty
) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="echo", dry_run=True)
    make_command.make()
    assert runner.call_count == 0

    expected_out_lines = (
        "🔧 Running `echo 'echo'`",
        "✅ `echo 'echo'` run successfully!",
    )
    captured = capsys.readouterr()
    assert captured.out == os.linesep.join(expected_out_lines) + os.linesep
    assert captured.err == ""


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_verbosity(
    runner: mock.MagicMock,
    capsys: mock.MagicMock,  # upgrade: pytest: check for isatty
) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="echo", verbosity=4)
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 'echo'", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls

    expected_out_lines = (
        "=== all targets ===",
        "- echo:",
        "    timestamp: end of time",
        "    should_build: True",
        "    requires: []",
        "    required_by: set()",
        "=== target: echo ===",
        "🔧 Running `echo 'echo'`",
        "✅ `echo 'echo'` run successfully!",
    )
    captured = capsys.readouterr()
    assert captured.out == os.linesep.join(expected_out_lines) + os.linesep
    assert captured.err == ""


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_echo_in_recipe(
    runner: mock.MagicMock,
    capsys: mock.MagicMock,  # upgrade: pytest: check for isatty
) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="echo")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 'echo'", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls

    expected_out_lines = (
        "🔧 Running `echo 'echo'`",
        "✅ `echo 'echo'` run successfully!",
    )
    captured = capsys.readouterr()
    assert captured.out == os.linesep.join(expected_out_lines) + os.linesep
    assert captured.err == ""


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_echo_in_command(
    runner: mock.MagicMock,
    capsys: mock.MagicMock,  # upgrade: pytest: check for isatty
) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="echo_in_command")
    make_command.make()
    assert runner.call_count == 1
    calls = [mock.call("echo 'echo_in_command'", **make_command.subprocess_kwargs)]
    assert runner.call_args_list == calls

    expected_out_lines = (
        "🔧 Running `echo 'echo_in_command'`",
        "✅ `echo 'echo_in_command'` run successfully!",
    )
    captured = capsys.readouterr()
    assert captured.out == os.linesep.join(expected_out_lines) + os.linesep
    assert captured.err == ""
