from unittest import mock

import pytest

from yamk import make


class TestMakeCommand:
    @staticmethod
    def test_make_raises_on_missing_target():
        args = mock.MagicMock()
        args.targets = ["phony"]
        make_command = make.MakeCommand(args)
        make_command.recipes = {}
        with pytest.raises(ValueError):
            make_command.make()

    @staticmethod
    @mock.patch("yamk.make.subprocess.run")
    def test_make_builds_with_no_commands(runner):
        args = mock.MagicMock()
        args.targets = ["phony"]
        make_command = make.MakeCommand(args)
        make_command.recipes = {"phony": {}}
        make_command.make()
        runner.assert_not_called()

    @staticmethod
    @mock.patch("yamk.make.subprocess.run")
    def test_make_builds_with_one_command(runner):
        args = mock.MagicMock()
        args.targets = ["phony"]
        make_command = make.MakeCommand(args)
        make_command.recipes = {"phony": {"commands": ["echo foo"]}}
        make_command.make()
        runner.assert_called_once()
