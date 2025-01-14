from yamk.command.make import MakeCommand
from yamk.lib.cli import parse_args


def main() -> None:
    args = parse_args()
    MakeCommand(args).make()
