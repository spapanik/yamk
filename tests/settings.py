import pathlib

TESTS_ROOT = pathlib.Path(__file__).absolute().parent
TEST_MAKEFILE = TESTS_ROOT.joinpath("data", "mk.toml")
