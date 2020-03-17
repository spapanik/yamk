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

    def __call__(self, *args):
        return list(self.base_dir.glob(args[0]))


class Sort(Function):
    name = "sort"

    def __call__(self, *args):
        return sorted(*args)


class Exists(Function):
    name = "exists"

    def __call__(self, *args):
        return self.base_dir.joinpath(args[0]).exists()


class PWD(Function):
    name = "pwd"

    def __call__(self, *_args):
        return self.base_dir


class TernaryIf(Function):
    name = "ternary_if"

    def __call__(self, *args):
        return args[1] if args[0] else args[2]


functions = FunctionMeta.functions
