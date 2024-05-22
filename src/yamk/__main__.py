from yamk.command.make import MakeCommand
from yamk.lib.parser import parse_args


def main() -> None:
    args = parse_args()
    MakeCommand(args).make()
