import os
from unittest import mock

import pytest

from tests.helpers import get_make_command, runner_exit_failure, runner_exit_success

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


@mock.patch("yamk.command.make.print_reports")
@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_make_print_timing_report(
    runner: mock.MagicMock, print_reports: mock.MagicMock
) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="echo", print_timing_report=True
    )
    make_command.make()
    assert runner.call_count == 1
    assert print_reports.call_count == 1


@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_failure)
def test_make_echo_failed_command(
    runner: mock.MagicMock,
    capsys: mock.MagicMock,  # upgrade: pytest: check for isatty
) -> None:
    make_command = get_make_command(cookbook_name=COOKBOOK, target="echo")
    with pytest.raises(SystemExit) as exc_info:
        make_command.make()
    assert exc_info.value.code == 42
    assert runner.call_count == 1

    expected_out_lines = (
        "🔧 Running `echo 'echo'`",
        "❌ `echo 'echo'` failed with exit code 42",
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


@mock.patch("yamk.command.make.print_reports", new=mock.MagicMock())
@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_success)
def test_timing_report_success_flag(runner: mock.MagicMock) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="echo", print_timing_report=True
    )
    make_command.make()
    assert runner.call_count == 1
    assert len(make_command.reports) == 1
    assert make_command.reports[0].success is True


@mock.patch("yamk.command.make.print_reports", new=mock.MagicMock())
@mock.patch("yamk.command.make.subprocess.run", new_callable=runner_exit_failure)
def test_timing_report_failure_flag(runner: mock.MagicMock) -> None:
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="echo", print_timing_report=True
    )
    with pytest.raises(SystemExit) as exc_info:
        make_command.make()
    assert exc_info.value.code == 42
    assert runner.call_count == 1
    assert len(make_command.reports) == 1
    assert make_command.reports[0].success is False


@mock.patch("yamk.command.make.print_reports", new=mock.MagicMock())
@mock.patch("yamk.command.make.sleep", new=mock.MagicMock())
@mock.patch("yamk.command.make.subprocess.run")
def test_timing_report_retry_then_success(
    runner: mock.MagicMock,
) -> None:
    runner.side_effect = [
        mock.MagicMock(returncode=1),
        mock.MagicMock(returncode=0),
    ]
    make_command = get_make_command(
        cookbook_name=COOKBOOK, target="echo", print_timing_report=True, retries=1
    )
    make_command.make()
    assert runner.call_count == 2
    assert len(make_command.reports) == 1
    assert make_command.reports[0].success is True
    assert make_command.reports[0].retries == 1


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
