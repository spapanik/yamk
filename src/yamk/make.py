import os
import re
import subprocess
import sys
from string import Template

import toml


class MakeCommand:
    def __init__(self, args):
        self.target = args.target
        self.makefile = args.makefile
        with open(self.makefile) as file:
            self.recipes = toml.load(file)
        self.globals = self.recipes.get("$globals", {})
        self.vars = dict(**os.environ)
        self._update_variables(self.vars, self.globals.get("vars", []))

    def make(self):
        try:
            recipe = self.recipes[self.target]
        except KeyError:
            raise ValueError(f"No recipe for {self.target}")

        variables = self.vars.copy()
        self._update_variables(variables, recipe.get("vars", []))
        commands = recipe.get("commands", [])
        for command in commands:
            command = self._substitute_vars(command, variables)
            command, options = self._parse_string(command)
            if recipe.get("echo") or options.get("echo"):
                print(command)
            result = subprocess.run(command, shell=True)
            if (
                result.returncode
                and not recipe.get("allow_failures")
                and not options.get("allow_failures")
            ):
                sys.exit(result.returncode)

    @staticmethod
    def _parse_string(string):
        match = re.match(r"\[.*?\]", string)
        if match is None:
            return string.strip(), {}

        end = match.end()
        options = string[1 : end - 1]
        string = string[end:]
        return (
            string.strip(),
            dict.fromkeys(map(lambda s: s.strip(), options.split(",")), True),
        )

    def _update_variables(self, variables, new_variables):
        for var_block in new_variables:
            for key, value in var_block.items():
                key = self._substitute_vars(key, variables)
                key, options = self._parse_string(key)
                if key in os.environ and not options.get("strong"):
                    continue
                value = self._substitute_vars(value, variables)
                variables[key] = value

    @staticmethod
    def _substitute_vars(string, variables):
        return Template(string).substitute(**variables)
