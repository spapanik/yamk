import pathlib

import pytest

from yamk import functions

PATH = pathlib.Path(__file__)


def test_glob():
    assert PATH.as_posix() in list(functions.Glob(PATH.parent)("*"))


def test_sort():
    assert functions.Sort(PATH)([3, 1, 2]) == [1, 2, 3]


@pytest.mark.parametrize(
    ["path", "exists"],
    [
        [PATH, True],
        ["random_name.extension", False],
        [[PATH, "random.rnd"], [True, False]],
    ],
)
def test_exists(path, exists):
    assert functions.Exists(PATH)(path) == exists


@pytest.mark.parametrize(
    ["path", "stem"],
    [
        ["make.toml", "make"],
        ["path/random_name.extension", "random_name"],
        [["make.toml", "path/to/file.txt"], ["make", "file"]],
    ],
)
def test_stem(path, stem):
    assert functions.Stem(PATH)(path) == stem


@pytest.mark.parametrize(
    ["path", "parent"],
    [
        ["make.toml", PATH],
        ["random_name.extension", PATH],
        ["directory/", PATH],
        [["file.txt", "dir/"], [PATH, PATH]],
    ],
)
def test_parent(path, parent):
    assert functions.Parent(PATH)(path) == parent


def test_pwd():
    assert functions.PWD(PATH)() == PATH.as_posix()


@pytest.mark.parametrize(
    ["condition", "true_value", "false_value", "expected"],
    [[True, 42, 1024, 42], [False, 42, 1024, 1024]],
)
def test_ternary_if(condition, true_value, false_value, expected):
    assert functions.TernaryIf(PATH)(condition, true_value, false_value) == expected


@pytest.mark.parametrize(
    ["old", "new", "obj", "expected"],
    [
        ["old", "new", "old string", "new string"],
        [
            "old",
            "new",
            ["old string", "another old string", "constant"],
            ["new string", "another new string", "constant"],
        ],
    ],
)
def test_substitute(old, new, obj, expected):
    assert functions.Substitute(PATH)(old, new, obj) == expected


@pytest.mark.parametrize(
    ["arguments", "expected"],
    [
        [[0, 1, 2], [0, 1, 2]],
        [[0, [1, 2]], [0, 1, 2]],
        [[[0], [1, 2]], [0, 1, 2]],
        [[0, [1], 2], [0, 1, 2]],
        [[[0], 1, [2]], [0, 1, 2]],
    ],
)
def test_merge(arguments, expected):
    assert functions.Merge(PATH)(*arguments) == expected
