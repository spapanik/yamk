import argparse

from yamk import __version__


def parse_args():
    parser = argparse.ArgumentParser(
        prog="yamk", description="Yet another make command",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Print the version and exit",
    )

    return parser.parse_args()


def main():
    parse_args()
