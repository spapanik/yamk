import itertools
import os
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
        makefile = args.makefile
        self.arg_vars = [
            {key: value}
            for key, value in map(
                lambda var: var.split("=", maxsplit=1), args.variables
            )
        ]
        self.base_dir = pathlib.Path(makefile).parent.absolute()
        self.phony_dir = self.base_dir.joinpath(".yamk")
        with open(makefile) as file:
            parsed_toml = tomlkit.parse(file.read())
        file_vars = parsed_toml.pop("$globals", {})
        self._parse_recipes(parsed_toml)
        self.vars = (
            lib.Variables(self.base_dir, **os.environ)
            .add_batch(self.arg_vars)
            .add_batch(file_vars.get("vars", []))
        )
        self.subprocess_kwargs = {"shell": True, "cwd": self.base_dir}

    def make(self):
        preprocessed = self._preprocess_target()
        for info in filter(
            lambda x: x["should_build"],
            sorted(preprocessed.values(), key=lambda x: x["priority"], reverse=True),
        ):
            self._make_target(info["recipe"])

    def _parse_recipes(self, parsed_toml):
        for target, raw_recipe in parsed_toml.items():
            if raw_recipe.get("alias"):
                self.aliases[target] = raw_recipe["alias"]
            recipe = lib.Recipe(target, raw_recipe, self.base_dir, self.arg_vars)

            if recipe.regex:
                self.regex_recipes[recipe.target] = recipe
            else:
                self.static_recipes[recipe.target] = recipe

    def _preprocess_target(self):
        recipe = self._extract_recipe(self.target)
        if recipe is None:
            raise ValueError(f"No recipe to build {self.target}")

        unprocessed = {self.target: {"recipe": recipe, "priority": 0}}
        preprocessed = {}
        while unprocessed:
            target, info = unprocessed.popitem()
            priority = info["priority"] + 1
            recipe = info["recipe"]
            preprocessed[target] = info
            for requirement in recipe.requires:
                recipe = self._extract_recipe(requirement)
                path = self._file_path(requirement)
                if requirement in preprocessed:
                    current_priority = preprocessed[requirement]["priority"]
                    preprocessed[requirement]["priority"] = max(
                        priority, current_priority
                    )
                elif recipe is not None:
                    unprocessed[requirement] = {
                        "recipe": recipe,
                        "priority": priority,
                    }
                elif path.exists():
                    preprocessed[requirement] = {"priority": priority}
                else:
                    raise ValueError(f"No recipe to build {requirement}")

        self._mark_unchanged(preprocessed)
        return preprocessed

    def _make_target(self, recipe):
        for command in recipe.commands:
            command, options = lib.extract_options(command)
            if recipe.echo or "echo" in options:
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

        return recipe.for_target(target, self.vars)

    def _mark_unchanged(self, preprocessed):
        for target, info in sorted(
            preprocessed.items(), key=lambda x: x[1]["priority"], reverse=True
        ):
            ts = self._infer_timestamp(target, info)
            info["timestamp"] = ts
            should_build = self._should_build(target, preprocessed)
            info["should_build"] = should_build

    def _phony_path(self, target):
        encoded_target = target.replace(".", ".46").replace("/", ".47")
        return self.phony_dir.joinpath(encoded_target)

    def _file_path(self, target):
        return self.base_dir.joinpath(target)

    def _should_build(self, target, preprocessed):
        info = preprocessed[target]
        recipe = info.get("recipe")
        if recipe is None:
            return False
        if recipe.phony:
            if not recipe.keep_ts:
                return True
            path = self._phony_path(target)
            if not path.exists():
                return True
        else:
            path = self._file_path(target)
            if not path.exists():
                return True
            if recipe.exists_only:
                return False

        if any(
            preprocessed[requirement]["should_build"] for requirement in recipe.requires
        ):
            return True

        ts = info["timestamp"]
        req_ts = max(
            preprocessed[requirement]["timestamp"] for requirement in recipe.requires
        )
        return req_ts > ts

    def _infer_timestamp(self, target, info):
        recipe = info.get("recipe")
        path = self._file_path(target)
        if recipe is None:
            return path.stat().st_mtime
        if recipe.phony:
            path = self._phony_path(target)
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
