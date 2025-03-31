from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from yamk.lib.type_defs import Comparable, Pathlike

S = TypeVar("S")
T = TypeVar("T")


class Function:
    name: str

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # type: ignore[explicit-any]  # noqa: ANN401
        raise NotImplementedError


class Glob(Function):
    name = "glob"

    def __call__(self, pattern: str) -> list[str]:
        return [path.as_posix() for path in self.base_dir.glob(pattern)]


class Sort(Function, Generic[T]):
    name = "sort"

    def __call__(self, args: Iterable[Comparable]) -> list[Comparable]:
        return sorted(args)


class Exists(Function):
    name = "exists"

    def __call__(self, path: Pathlike | list[Pathlike]) -> bool | list[bool]:
        if isinstance(path, list):
            return [cast("bool", self(file)) for file in path]
        return self.base_dir.joinpath(path).exists()


class Name(Function):
    name = "name"

    def __call__(self, path: Pathlike | list[Pathlike]) -> str | list[str]:
        if isinstance(path, list):
            return [cast("str", self(file)) for file in path]
        return self.base_dir.joinpath(path).name


class Stem(Function):
    name = "stem"

    def __call__(self, path: Pathlike | list[Pathlike]) -> str | list[str]:
        if isinstance(path, list):
            return [cast("str", self(file)) for file in path]
        return self.base_dir.joinpath(path).stem


class Suffix(Function):
    name = "suffix"

    def __call__(self, path: Pathlike | list[Pathlike]) -> str | list[str]:
        if isinstance(path, list):
            return [cast("str", self(file)) for file in path]
        return self.base_dir.joinpath(path).suffix


class Parent(Function):
    name = "parent"

    def __call__(self, path: Pathlike | list[Pathlike]) -> str | list[str]:
        if isinstance(path, list):
            return [cast("str", self(file)) for file in path]
        return self.base_dir.joinpath(path).parent.as_posix()


class ChangeSuffix(Function):
    name = "change_suffix"

    def __call__(self, path: Pathlike | list[Pathlike], suffix: str) -> str | list[str]:
        if isinstance(path, list):
            return [cast("str", self(file, suffix)) for file in path]
        return self.base_dir.joinpath(path).with_suffix(suffix).as_posix()


class ChangeParent(Function):
    name = "change_parent"

    def __call__(
        self, path: Pathlike | list[Pathlike], parent: Pathlike
    ) -> str | list[str]:
        if isinstance(path, list):
            return [cast("str", self(file, parent)) for file in path]
        name = self.base_dir.joinpath(path).name
        return self.base_dir.joinpath(parent, name).as_posix()


class PWD(Function):
    name = "pwd"

    def __call__(self) -> str:
        return self.base_dir.as_posix()


class FilterOut(Function):
    name = "filter_out"

    def __call__(self, odd: T, obj: list[T]) -> list[T]:
        return list(filter(lambda x: x != odd, obj))


class TernaryIf(Function):
    name = "ternary_if"

    def __call__(
        self,
        condition: bool,  # noqa: FBT001
        if_true: S,
        if_false: T,
    ) -> S | T:
        return if_true if condition else if_false


class Substitute(Function):
    name = "sub"

    def __call__(self, old: str, new: str, obj: list[str] | str) -> list[str] | str:
        if isinstance(obj, list):
            return [cast("str", self(old, new, string)) for string in obj]
        return obj.replace(old, new)


class Merge(Function):
    name = "merge"

    @staticmethod
    def _as_list(obj: T | list[T]) -> list[T]:
        return obj if isinstance(obj, list) else [obj]

    def _concat(self, x: T | list[T], y: T | list[T]) -> list[T]:
        return self._as_list(x) + self._as_list(y)

    def __call__(self, *args: T | list[T]) -> list[T]:
        return reduce(self._concat, args)  # type: ignore[arg-type]


functions = {function.name: function for function in Function.__subclasses__()}
