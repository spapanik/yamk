from __future__ import annotations

from pathlib import Path

import pytest

from yamk import functions
from yamk.types import Pathlike

PATH = Path(__file__)
BASE_DIR = PATH.parent


def test_function_callable() -> None:
    class NotCallableFunction(functions.Function):
        pass

    with pytest.raises(NotImplementedError):
        NotCallableFunction(BASE_DIR)()


def test_glob() -> None:
    assert PATH.as_posix() in list(functions.Glob(BASE_DIR)("*"))


def test_sort() -> None:
    assert functions.Sort(BASE_DIR)([3, 1, 2]) == [1, 2, 3]


@pytest.mark.parametrize(
    ("path", "exists"),
    [
        (PATH, True),
        ("random_name.extension", False),
        ([PATH, "random.rnd"], [True, False]),
    ],
)
def test_exists(path: Pathlike, exists: bool) -> None:
    assert functions.Exists(BASE_DIR)(path) == exists


@pytest.mark.parametrize(
    ("path", "stem"),
    [
        ("make.toml", "make"),
        ("path/random_name.extension", "random_name"),
        (["make.toml", "path/to/file.txt"], ["make", "file"]),
    ],
)
def test_stem(path: Pathlike | list[Pathlike], stem: str | list[str]) -> None:
    assert functions.Stem(BASE_DIR)(path) == stem


@pytest.mark.parametrize(
    ("path", "suffix"),
    [
        ("make.toml", ".toml"),
        ("path/random_name.extension", ".extension"),
        (["make.toml", "path/to/file.txt"], [".toml", ".txt"]),
    ],
)
def test_suffix(path: Pathlike | list[Pathlike], suffix: str | list[str]) -> None:
    assert functions.Suffix(BASE_DIR)(path) == suffix


@pytest.mark.parametrize(
    ("path", "name"),
    [
        ("make.toml", "make.toml"),
        ("path/random_name.extension", "random_name.extension"),
        (["make.toml", "path/to/file.txt"], ["make.toml", "file.txt"]),
    ],
)
def test_name(path: Pathlike | list[Pathlike], name: str | list[str]) -> None:
    assert functions.Name(BASE_DIR)(path) == name


@pytest.mark.parametrize(
    ("path", "new_parent", "new_path"),
    [
        ("make.toml", "/etc", "/etc/make.toml"),
        (
            "path/random_name.extension",
            "dir/",
            BASE_DIR.joinpath("dir", "random_name.extension").as_posix(),
        ),
        (
            ["make.toml", "path/to/file.txt"],
            "",
            [
                BASE_DIR.joinpath("make.toml").as_posix(),
                BASE_DIR.joinpath("file.txt").as_posix(),
            ],
        ),
    ],
)
def test_change_parent(
    path: Pathlike | list[Pathlike], new_parent: str, new_path: str | list[str]
) -> None:
    assert functions.ChangeParent(BASE_DIR)(path, new_parent) == new_path


@pytest.mark.parametrize(
    ("path", "new_suffix", "new_path"),
    [
        ("make.toml", ".py", BASE_DIR.joinpath("make.py").as_posix()),
        ("make.toml", "", BASE_DIR.joinpath("make").as_posix()),
        (
            "path/random_name.extension",
            ".cpp",
            BASE_DIR.joinpath("path/random_name.cpp").as_posix(),
        ),
        (
            ["make.toml", "path/to/file.txt"],
            ".o",
            [
                BASE_DIR.joinpath("make.o").as_posix(),
                BASE_DIR.joinpath("path/to/file.o").as_posix(),
            ],
        ),
    ],
)
def test_change_suffix(
    path: Pathlike | list[Pathlike], new_suffix: str, new_path: str | list[str]
) -> None:
    assert functions.ChangeSuffix(BASE_DIR)(path, new_suffix) == new_path


@pytest.mark.parametrize(
    ("path", "parent"),
    [
        ("make.toml", BASE_DIR.as_posix()),
        ("random_name.extension", BASE_DIR.as_posix()),
        ("directory/", BASE_DIR.as_posix()),
        (["file.txt", "dir/"], [BASE_DIR.as_posix(), BASE_DIR.as_posix()]),
    ],
)
def test_parent(path: Pathlike | list[Pathlike], parent: str | list[str]) -> None:
    assert functions.Parent(BASE_DIR)(path) == parent


def test_pwd() -> None:
    assert functions.PWD(BASE_DIR)() == BASE_DIR.as_posix()


@pytest.mark.parametrize(
    ("condition", "true_value", "false_value", "expected"),
    [(True, 42, 1024, 42), (False, 42, 1024, 1024)],
)
def test_ternary_if(
    condition: bool, true_value: int, false_value: int, expected: int
) -> None:
    assert functions.TernaryIf(BASE_DIR)(condition, true_value, false_value) == expected


@pytest.mark.parametrize(
    ("odd", "obj", "expected"), [(1, [42, 1024], [42, 1024]), (1024, [42, 1024], [42])]
)
def test_filter_out(odd: int, obj: list[int], expected: list[int]) -> None:
    assert functions.FilterOut(BASE_DIR)(odd, obj) == expected


@pytest.mark.parametrize(
    ("old", "new", "obj", "expected"),
    [
        ("old", "new", "old string", "new string"),
        (
            "old",
            "new",
            ["old string", "another old string", "constant"],
            ["new string", "another new string", "constant"],
        ),
    ],
)
def test_substitute(
    old: str, new: str, obj: str | list[str], expected: str | list[str]
) -> None:
    assert functions.Substitute(BASE_DIR)(old, new, obj) == expected


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        ([0, 1, 2], [0, 1, 2]),
        ([0, [1, 2]], [0, 1, 2]),
        ([[0], [1, 2]], [0, 1, 2]),
        ([0, [1], 2], [0, 1, 2]),
        ([[0], 1, [2]], [0, 1, 2]),
    ],
)
def test_merge(arguments: list[int | list[int]], expected: list[int]) -> None:
    assert functions.Merge(BASE_DIR)(*arguments) == expected
