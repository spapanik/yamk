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
        return self.base_dir.glob(args[0])


class Sort(Function):
    name = "sort"

    def __call__(self, *args):
        return sorted(*args)


functions = FunctionMeta.functions
