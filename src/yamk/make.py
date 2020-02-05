import os
import subprocess
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
            raise ValueError

        variables = self.vars.copy()
        self._update_variables(variables, recipe.get("vars", []))
        commands = recipe.get("commands", [])
        for command in commands:
            command = self._substitute_vars(command, variables)
            print(command)
            subprocess.run(command, shell=True)

    def _update_variables(self, variables, new_variables):
        for var_block in new_variables:
            for key, value in var_block.items():
                key = self._substitute_vars(key, variables)
                value = self._substitute_vars(value, variables)
                variables[key] = value

    def _substitute_vars(self, string, variables):
        return Template(string).substitute(**variables)
