from __future__ import annotations

from functools import reduce
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from pathlib import Path

    from yamk.lib.types import Pathlike


class Function:
    name: str

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ARG002
        msg = f"{self.__class__.__name__} must be callable"
        raise NotImplementedError(msg)


class Glob(Function):
    name = "glob"

    def __call__(self, pattern: str) -> list[str]:
        return [path.as_posix() for path in self.base_dir.glob(pattern)]


class Sort(Function):
    name = "sort"

    def __call__(self, *args: Any) -> list[Any]:
        return sorted(*args)


class Exists(Function):
    name = "exists"

    def __call__(self, path: Pathlike | list[Pathlike]) -> bool | list[bool]:
        if isinstance(path, list):
            return [cast(bool, self(file)) for file in path]
        return self.base_dir.joinpath(path).exists()


class Name(Function):
    name = "name"

    def __call__(self, path: Pathlike | list[Pathlike]) -> str | list[str]:
        if isinstance(path, list):
            return [cast(str, self(file)) for file in path]
        return self.base_dir.joinpath(path).name


class Stem(Function):
    name = "stem"

    def __call__(self, path: Pathlike | list[Pathlike]) -> str | list[str]:
        if isinstance(path, list):
            return [cast(str, self(file)) for file in path]
        return self.base_dir.joinpath(path).stem


class Suffix(Function):
    name = "suffix"

    def __call__(self, path: Pathlike | list[Pathlike]) -> str | list[str]:
        if isinstance(path, list):
            return [cast(str, self(file)) for file in path]
        return self.base_dir.joinpath(path).suffix


class Parent(Function):
    name = "parent"

    def __call__(self, path: Pathlike | list[Pathlike]) -> str | list[str]:
        if isinstance(path, list):
            return [cast(str, self(file)) for file in path]
        return self.base_dir.joinpath(path).parent.as_posix()


class ChangeSuffix(Function):
    name = "change_suffix"

    def __call__(self, path: Pathlike | list[Pathlike], suffix: str) -> str | list[str]:
        if isinstance(path, list):
            return [cast(str, self(file, suffix)) for file in path]
        return self.base_dir.joinpath(path).with_suffix(suffix).as_posix()


class ChangeParent(Function):
    name = "change_parent"

    def __call__(
        self, path: Pathlike | list[Pathlike], parent: Pathlike
    ) -> str | list[str]:
        if isinstance(path, list):
            return [cast(str, self(file, parent)) for file in path]
        name = self.base_dir.joinpath(path).name
        return self.base_dir.joinpath(parent, name).as_posix()


class PWD(Function):
    name = "pwd"

    def __call__(self) -> str:
        return self.base_dir.as_posix()


class FilterOut(Function):
    name = "filter_out"

    def __call__(self, odd: Any, obj: list[Any]) -> list[Any]:
        return list(filter(lambda x: x != odd, obj))


class TernaryIf(Function):
    name = "ternary_if"

    def __call__(
        self, condition: bool, if_true: Any, if_false: Any  # noqa: FBT001
    ) -> Any:
        return if_true if condition else if_false


class Substitute(Function):
    name = "sub"

    def __call__(self, old: str, new: str, obj: list[str] | str) -> list[str] | str:
        if isinstance(obj, list):
            return [cast(str, self(old, new, string)) for string in obj]
        return obj.replace(old, new)


class Merge(Function):
    name = "merge"

    @staticmethod
    def _as_list(obj: Any | list[Any]) -> list[Any]:
        return obj if isinstance(obj, list) else [obj]

    def __call__(self, *args: Any | list[Any]) -> list[Any]:
        return reduce(lambda x, y: self._as_list(x) + self._as_list(y), args)


functions = {function.name: function for function in Function.__subclasses__()}
