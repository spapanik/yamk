import os
import pathlib
import re
import subprocess
import sys

import toml

from yamk import lib


class Recipe:
    def __init__(self, target, raw_recipe):
        self.target = target
        self.phony = raw_recipe.get("phony", False)
        self.requires = raw_recipe.get("requires", [])
        self.vars = raw_recipe.get("vars", [])
        self.commands = raw_recipe.get("commands", [])
        self.echo = raw_recipe.get("echo", False)
        self.regex = raw_recipe.get("regex", False)
        self.allow_failures = raw_recipe.get("allow_failures", False)
        if self.phony:
            self.keep_ts = raw_recipe.get("keep_ts", False)
            self.exists_only = False
            self.recursive = False
        else:
            self.keep_ts = False
            self.exists_only = raw_recipe.get("exists_only", False)
            self.recursive = raw_recipe.get("recursive", False)


class MakeCommand:
    def __init__(self, args):
        self.regex_recipes = {}
        self.static_recipes = {}
        self.target = args.target
        self.makefile = args.makefile
        self.phony_dir = pathlib.Path(self.makefile).parent.joinpath(".yamk")
        with open(self.makefile) as file:
            parsed_toml = toml.load(file)
        self.globals = parsed_toml.pop("$globals", {})
        self._parse_recipes(parsed_toml)
        self.vars = lib.Variables(**os.environ).add_batch(self.globals.get("vars", []))

    def make(self):
        preprocessed = self._preprocess_target()
        for target, info in filter(
            lambda x: x[1]["should_build"],
            sorted(preprocessed.items(), key=lambda x: x[1]["priority"], reverse=True),
        ):
            self._make_target(target, info["recipe"])

    def _parse_recipes(self, parsed_toml):
        for target, raw_recipe in parsed_toml.items():
            if raw_recipe.get("regex"):
                compiled_target = re.compile(target)
                self.regex_recipes[compiled_target] = Recipe(
                    compiled_target, raw_recipe
                )
            else:
                self.static_recipes[target] = Recipe(target, raw_recipe)

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
                path = pathlib.Path(requirement)
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

    def _make_target(self, target, recipe):
        variables = self.vars.add_batch(recipe.vars)
        commands = recipe.commands
        for command in commands:
            command = lib.substitute_vars(command, variables)
            command, options = lib.extract_options(command)
            if recipe.echo or "echo" in options:
                print(command)
            result = subprocess.run(command, shell=True)
            if not result.returncode and recipe.phony and recipe.keep_ts:
                path = self._phony_path(target)
                path.touch()
            if (
                result.returncode
                and not recipe.allow_failures
                and "allow_failures" not in options
            ):
                sys.exit(result.returncode)
        if recipe.phony and recipe.keep_ts:
            path = self._phony_path(target)
            self.phony_dir.mkdir(exist_ok=True)
            path.touch()
            print(path)

    def _extract_recipe(self, target):
        try:
            return self.static_recipes[target]
        except KeyError:
            for regex, recipe in self.regex_recipes.items():
                if re.fullmatch(regex, target):
                    return recipe
            return None

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
            path = pathlib.Path(target)
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
        path = pathlib.Path(target)
        if recipe is None:
            return path.stat().st_mtime
        if recipe.phony:
            path = self._phony_path(target)
            if recipe.keep_ts and path.exists():
                return path.stat().st_mtime
            return float("inf")
        if recipe.exists_only:
            return 0
        if path.exists():
            if recipe.recursive:
                return max(p.stat().st_mtime for p in path)
            return path.stat().st_mtime
        return float("inf")
