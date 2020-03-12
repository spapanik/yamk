import re
import shlex

VAR = re.compile(r"(?P<dollars>\$+){(?P<variable>[a-zA-Z0-9_.]+(:[a-zA-Z0-9_.]+)?)}")
OPTIONS = re.compile(r"\[(?P<options>.*?)\](?P<string>.*)")
FUNCTION = re.compile(r"\$\(\((?P<name>\w+) +(?P<args>.+)\)\)")


class Recipe:
    def __init__(self, target, raw_recipe, base_dir, arg_vars):
        self._specified = False
        self.base_dir = base_dir
        self.vars: Variables
        self.arg_vars = arg_vars
        self.phony = raw_recipe.get("phony", False)
        self.requires = raw_recipe.get("requires", [])
        self.variable_list = raw_recipe.get("vars", [])
        self.commands = raw_recipe.get("commands", [])
        self.echo = raw_recipe.get("echo", False)
        self.regex = raw_recipe.get("regex", False)
        self.allow_failures = raw_recipe.get("allow_failures", False)
        self.target = self._target(target)
        if self.phony:
            self.keep_ts = raw_recipe.get("keep_ts", False)
            self.exists_only = False
            self.recursive = False
        else:
            self.keep_ts = False
            self.exists_only = raw_recipe.get("exists_only", False)
            self.recursive = raw_recipe.get("recursive", False)

    def __str__(self):
        if self._specified:
            return f"Specified recipe for {self.target}"
        return f"Generic recipe for {self.target}"

    def specify(self, target, globs):
        if self._specified:
            return
        self._specified = True
        if self.regex:
            groups = re.fullmatch(self.target, target).groupdict()
            self.target = target
        else:
            groups = {}
        self._update_variables(globs, groups)
        self._update_requirements()
        self._update_commands()

    def _update_variables(self, globs, groups):
        extra_vars = [groups, *self.arg_vars, {".target": self.target}]
        self.vars = globs.add_batch(self.variable_list).add_batch(extra_vars)

    def _update_requirements(self):
        parser = Parser(self.vars, self.base_dir)
        self.requires = parser.evaluate(self.requires)

    def _update_commands(self):
        extra_vars = [{".requirements": self.requires}]
        self.vars = self.vars.add_batch(extra_vars)
        parser = Parser(self.vars, self.base_dir)
        self.commands = parser.evaluate(self.commands)

    def _target(self, target):
        if not self.phony:
            target = self.base_dir.joinpath(target).as_posix()
        if self.regex:
            target = re.compile(target)
        return target


class Variables(dict):
    def __init__(self, base_dir, **kwargs):
        super().__init__(**kwargs)
        self.base_dir = base_dir

    def add_batch(self, batch):
        new_vars = self.__class__(self.base_dir, **self)
        for var_block in batch:
            parser = Parser(new_vars, self.base_dir)
            for key, value in var_block.items():
                key = parser.evaluate(key)
                key, options = extract_options(key)
                if "weak" in options:
                    continue
                value = parser.evaluate(value)
                new_vars[key] = value
        return new_vars


class FunctionMeta(type):
    functions = {}

    def __new__(mcs, name, bases, class_dict):
        x = super().__new__(mcs, name, bases, class_dict)
        if getattr(x, "name", None) is not None:
            mcs.functions[x.name] = x
        return x

    @classmethod
    def get(mcs, item):
        return mcs.functions[item]


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


class Parser:
    def __init__(self, variables, base_dir):
        self.vars = variables
        self.base_dir = base_dir

    @staticmethod
    def _stringify(value):
        if isinstance(value, list):
            return " ".join(map(str, value))
        return str(value)

    def expand_function(self, name, args):
        args = shlex.split(args)
        for i, arg in enumerate(args):
            args[i] = self.evaluate(arg, literal_eval=True)
        function = FunctionMeta.get(name)(self.base_dir)
        return function(*args)

    def repl(self, matchobj):
        dollars = matchobj.group("dollars")
        variable = matchobj.group("variable")
        if len(dollars) % 2:
            key = None
            if ":" in variable:
                variable, key = variable.split(":")
            value = self.vars[variable]
            if key is None:
                return self._stringify(value)
            if isinstance(value, list):
                key = int(key)
            return self._stringify(value[key])
        return f"{'$'*(len(dollars)//2)}{{{variable}}}"

    def substitute(self, string, literal_eval):
        function = re.fullmatch(FUNCTION, string)
        if function is not None:
            return self.expand_function(**function.groupdict())

        if (
            literal_eval
            and string.startswith("$")
            and not string.startswith("$$")
            and re.fullmatch(VAR, string)
        ):
            match = re.fullmatch(VAR, string)
            return self.vars[match.group("variable")]
        return re.sub(VAR, self.repl, string)

    def evaluate(self, obj, literal_eval=False):
        if isinstance(obj, str):
            return self.substitute(obj, literal_eval)
        if isinstance(obj, list):
            return [self.evaluate(string, literal_eval) for string in obj]
        if isinstance(obj, dict):
            return {
                self.evaluate(key, literal_eval): self.evaluate(value, literal_eval)
                for key, value in obj.items()
            }
        raise TypeError(f"{obj.__class__.__name__} is not supported for evaluation")


def extract_options(string):
    match = re.fullmatch(OPTIONS, string)
    if match is None:
        return string.strip(), set()

    options = match.group("options")
    string = match.group("string")
    return (
        string,
        set(map(lambda s: s.strip(), options.split(","))),
    )
