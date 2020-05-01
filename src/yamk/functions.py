from functools import reduce


class FunctionMeta(type):
    functions = {}

    def __new__(mcs, name, bases, class_dict):
        x = super().__new__(mcs, name, bases, class_dict)
        if getattr(x, "name", None) is not None:
            mcs.functions[x.name] = x
        return x


class Function(metaclass=FunctionMeta):
    def __init__(self, base_dir):
        self.base_dir = base_dir


class Glob(Function):
    name = "glob"

    def __call__(self, pattern):
        return [path.as_posix() for path in self.base_dir.glob(pattern)]


class Sort(Function):
    name = "sort"

    def __call__(self, *args):
        return sorted(*args)


class Exists(Function):
    name = "exists"

    def __call__(self, path):
        if isinstance(path, list):
            return [self(file) for file in path]
        return self.base_dir.joinpath(path).exists()


class Stem(Function):
    name = "stem"

    def __call__(self, path):
        if isinstance(path, list):
            return [self(file) for file in path]
        return self.base_dir.joinpath(path).stem


class Parent(Function):
    name = "parent"

    def __call__(self, path):
        if isinstance(path, list):
            return [self(file) for file in path]
        return self.base_dir.joinpath(path).parent


class PWD(Function):
    name = "pwd"

    def __call__(self):
        return self.base_dir.as_posix()


class TernaryIf(Function):
    name = "ternary_if"

    def __call__(self, condition, if_true, if_false):
        return if_true if condition else if_false


class Substitute(Function):
    name = "sub"

    def __call__(self, old, new, obj):
        if isinstance(obj, list):
            return [self(old, new, string) for string in obj]
        return obj.replace(old, new)


class Merge(Function):
    name = "merge"

    @staticmethod
    def _as_list(obj):
        return obj if isinstance(obj, list) else [obj]

    def __call__(self, *args):
        return reduce(lambda x, y: self._as_list(x) + self._as_list(y), args)


functions = FunctionMeta.functions
