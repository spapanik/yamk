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
