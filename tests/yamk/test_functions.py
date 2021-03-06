import pathlib

import pytest

from yamk import functions

PATH = pathlib.Path(__file__)
BASE_DIR = PATH.parent


def test_glob():
    assert PATH.as_posix() in list(functions.Glob(BASE_DIR)("*"))


def test_sort():
    assert functions.Sort(BASE_DIR)([3, 1, 2]) == [1, 2, 3]


@pytest.mark.parametrize(
    ["path", "exists"],
    [
        [PATH, True],
        ["random_name.extension", False],
        [[PATH, "random.rnd"], [True, False]],
    ],
)
def test_exists(path, exists):
    assert functions.Exists(BASE_DIR)(path) == exists


@pytest.mark.parametrize(
    ["path", "stem"],
    [
        ["make.toml", "make"],
        ["path/random_name.extension", "random_name"],
        [["make.toml", "path/to/file.txt"], ["make", "file"]],
    ],
)
def test_stem(path, stem):
    assert functions.Stem(BASE_DIR)(path) == stem


@pytest.mark.parametrize(
    ["path", "suffix"],
    [
        ["make.toml", ".toml"],
        ["path/random_name.extension", ".extension"],
        [["make.toml", "path/to/file.txt"], [".toml", ".txt"]],
    ],
)
def test_suffix(path, suffix):
    assert functions.Suffix(BASE_DIR)(path) == suffix


@pytest.mark.parametrize(
    ["path", "name"],
    [
        ["make.toml", "make.toml"],
        ["path/random_name.extension", "random_name.extension"],
        [["make.toml", "path/to/file.txt"], ["make.toml", "file.txt"]],
    ],
)
def test_name(path, name):
    assert functions.Name(BASE_DIR)(path) == name


@pytest.mark.parametrize(
    ["path", "new_parent", "new_path"],
    [
        ["make.toml", "/etc", "/etc/make.toml"],
        [
            "path/random_name.extension",
            "dir/",
            BASE_DIR.joinpath("dir", "random_name.extension").as_posix(),
        ],
        [
            ["make.toml", "path/to/file.txt"],
            "",
            [
                BASE_DIR.joinpath("make.toml").as_posix(),
                BASE_DIR.joinpath("file.txt").as_posix(),
            ],
        ],
    ],
)
def test_change_parent(path, new_parent, new_path):
    assert functions.ChangeParent(BASE_DIR)(path, new_parent) == new_path


@pytest.mark.parametrize(
    ["path", "new_suffix", "new_path"],
    [
        ["make.toml", ".py", BASE_DIR.joinpath("make.py").as_posix()],
        ["make.toml", "", BASE_DIR.joinpath("make").as_posix()],
        [
            "path/random_name.extension",
            ".cpp",
            BASE_DIR.joinpath("path/random_name.cpp").as_posix(),
        ],
        [
            ["make.toml", "path/to/file.txt"],
            ".o",
            [
                BASE_DIR.joinpath("make.o").as_posix(),
                BASE_DIR.joinpath("path/to/file.o").as_posix(),
            ],
        ],
    ],
)
def test_change_suffix(path, new_suffix, new_path):
    assert functions.ChangeSuffix(BASE_DIR)(path, new_suffix) == new_path


@pytest.mark.parametrize(
    ["path", "parent"],
    [
        ["make.toml", BASE_DIR.as_posix()],
        ["random_name.extension", BASE_DIR.as_posix()],
        ["directory/", BASE_DIR.as_posix()],
        [["file.txt", "dir/"], [BASE_DIR.as_posix(), BASE_DIR.as_posix()]],
    ],
)
def test_parent(path, parent):
    assert functions.Parent(BASE_DIR)(path) == parent


def test_pwd():
    assert functions.PWD(BASE_DIR)() == BASE_DIR.as_posix()


@pytest.mark.parametrize(
    ["condition", "true_value", "false_value", "expected"],
    [[True, 42, 1024, 42], [False, 42, 1024, 1024]],
)
def test_ternary_if(condition, true_value, false_value, expected):
    assert functions.TernaryIf(BASE_DIR)(condition, true_value, false_value) == expected


@pytest.mark.parametrize(
    ["odd", "obj", "expected"], [[1, [42, 1024], [42, 1024]], [1024, [42, 1024], [42]]]
)
def test_filter_out(odd, obj, expected):
    assert functions.FilterOut(BASE_DIR)(odd, obj) == expected


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
    assert functions.Substitute(BASE_DIR)(old, new, obj) == expected


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
    assert functions.Merge(BASE_DIR)(*arguments) == expected
