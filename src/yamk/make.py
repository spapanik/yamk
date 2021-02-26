import itertools
import pathlib
import re
import subprocess
import sys

import tomlkit

from yamk import lib


class MakeCommand:
    def __init__(self, args):
        self.verbosity = args.verbose
        if self.verbosity:
            if self.verbosity > 1:
                print(args)
            sys.tracebacklimit = 9999
        self.regex_recipes = {}
        self.static_recipes = {}
        self.aliases = {}
        self.target = args.target
        self.force_make = args.force
        makefile = pathlib.Path(args.directory).joinpath(args.makefile).absolute()
        self.base_dir = makefile.parent
        self.phony_dir = self.base_dir.joinpath(".yamk")
        self.arg_vars = [
            {key: value}
            for key, value in map(
                lambda var: var.split("=", maxsplit=1), args.variables
            )
        ]
        with open(makefile) as file:
            parsed_toml = tomlkit.parse(file.read())
        self.globals = parsed_toml.pop("$globals", {})
        self._parse_recipes(parsed_toml)
        self.subprocess_kwargs = {
            "shell": True,
            "cwd": self.base_dir,
            "executable": self.globals.get("shell") or args.shell,
        }

    def make(self):
        dag = self._preprocess_target()
        for node in filter(lambda x: x.should_build, dag):
            self._make_target(node.recipe)

    def _parse_recipes(self, parsed_toml):
        for target, raw_recipe in parsed_toml.items():
            recipe = lib.Recipe(
                target,
                raw_recipe,
                self.base_dir,
                {"file_vars": self.globals.get("vars", []), "arg_vars": self.arg_vars},
            )

            if recipe.alias:
                self.aliases[recipe.target] = recipe.alias
            elif recipe.regex:
                self.regex_recipes[recipe.target] = recipe
            else:
                self.static_recipes[recipe.target] = recipe

    def _preprocess_target(self):
        recipe = self._extract_recipe(self.target)
        if recipe is None:
            raise ValueError(f"No recipe to build {self.target}")

        root = lib.Node(recipe)
        unprocessed = {root.target: root}
        dag = lib.DAG(root)
        while unprocessed:
            target, target_node = unprocessed.popitem()
            dag.add_node(target_node)
            target_recipe = target_node.recipe
            for index, raw_requirement in enumerate(target_recipe.requires):
                recipe = self._extract_recipe(raw_requirement)
                if recipe is None:
                    requirement_path = self._file_path(raw_requirement)
                    requirement = requirement_path.as_posix()
                    if not requirement_path.exists():
                        raise ValueError(f"No recipe to build {requirement}")
                else:
                    requirement = recipe.target
                target_recipe.requires[index] = requirement

                if requirement in dag:
                    node = dag[requirement]
                elif requirement in unprocessed:
                    node = unprocessed[requirement]
                elif recipe is None:
                    node = lib.Node(target=requirement)
                    dag.add_node(node)
                else:
                    node = lib.Node(recipe)
                    unprocessed[requirement] = node
                target_node.add_requirement(node)

        dag.sort()
        self._mark_unchanged(dag)
        if self.verbosity > 3:
            print("=== all targets ===")
            for node in dag:
                print(f"- {node.target}:")
                print(f"    timestamp: {lib.timestamp_to_dt(node.timestamp)}")
                print(f"    should_build: {node.should_build}")
                print(f"    requires: {node.requires}")
                print(f"    required_by: {node.required_by}")
        return dag

    def _make_target(self, recipe):
        if self.verbosity > 1:
            print(f"=== target: {recipe.target} ===")

        for command in recipe.commands:
            command, options = lib.extract_options(command)
            if recipe.echo or "echo" in options or self.verbosity > 2:
                print(command)
            result = subprocess.run(command, **self.subprocess_kwargs)
            if (
                result.returncode
                and not recipe.allow_failures
                and "allow_failures" not in options
            ):
                sys.exit(result.returncode)
        if recipe.phony and recipe.keep_ts:
            path = self._phony_path(recipe.target)
            self.phony_dir.mkdir(exist_ok=True)
            path.touch()

    def _extract_recipe(self, target):
        if target in self.aliases:
            target = self.aliases[target]

        absolute_path_target = self.base_dir.joinpath(target).as_posix()
        if target in self.static_recipes:
            recipe = self.static_recipes[target]
        elif absolute_path_target in self.static_recipes:
            recipe = self.static_recipes[absolute_path_target]
        else:
            for regex, recipe in self.regex_recipes.items():  # noqa: B007
                if re.fullmatch(regex, target) or re.fullmatch(
                    regex, absolute_path_target
                ):
                    break
            else:
                return None

        return recipe.for_target(target)

    def _mark_unchanged(self, dag):
        for node in dag:
            node.timestamp = self._infer_timestamp(node)
            node.should_build = self._should_build(node)

    def _phony_path(self, target):
        encoded_target = target.replace(".", ".46").replace("/", ".47")
        return self.phony_dir.joinpath(encoded_target)

    def _file_path(self, target):
        return self.base_dir.joinpath(target)

    def _should_build(self, node):
        recipe = node.recipe
        if recipe is None:
            return False
        if self.force_make:
            return True
        if recipe.phony:
            if not recipe.keep_ts:
                return True
            path = self._phony_path(node.target)
            if not path.exists():
                return True
        else:
            path = self._file_path(node.target)
            if not path.exists():
                return True
            if recipe.exists_only:
                return False

        if any(child.should_build for child in node.requires):
            return True

        ts = node.timestamp
        req_ts = max(child.timestamp for child in node.requires)
        return req_ts > ts

    def _infer_timestamp(self, node):
        recipe = node.recipe
        path = self._file_path(node.target)
        if recipe is None:
            return path.stat().st_mtime
        if recipe.phony:
            path = self._phony_path(node.target)
            if recipe.keep_ts and path.exists():
                return path.stat().st_mtime
            return float("inf")
        if path.exists():
            if recipe.recursive:
                descendants = itertools.chain([path], path.rglob("*"))
                return max(p.stat().st_mtime for p in descendants)
            if recipe.exists_only:
                return 0
            return path.stat().st_mtime
        return float("inf")
