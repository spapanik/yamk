import pathlib

from yamk import functions

PATH = pathlib.Path(__file__)


def test_glob():
    assert PATH.as_posix() in list(functions.Glob(PATH.parent)("*"))


def test_sort():
    assert functions.Sort(PATH)([3, 1, 2]) == [1, 2, 3]
