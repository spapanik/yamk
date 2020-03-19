<p align="center">
<a href="https://travis-ci.org/spapanik/yamk"><img alt="Build" src="https://travis-ci.org/spapanik/yamk.svg?branch=master"></a>
<a href="https://coveralls.io/github/spapanik/yamk"><img alt="Coverage" src="https://coveralls.io/repos/github/spapanik/yamk/badge.svg?branch=master"></a>
<a href="https://github.com/spapanik/yamk/blob/master/LICENSE.txt"><img alt="License" src="https://img.shields.io/github/license/spapanik/yamk"></a>
<a href="https://pypi.org/project/yamk"><img alt="PyPI" src="https://img.shields.io/pypi/v/yamk"></a>
<a href="https://pepy.tech/project/yamk"><img alt="Downloads" src="https://pepy.tech/badge/yamk"></a>
<a href="https://github.com/psf/black"><img alt="Code style" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>


# yamk: yet another make

`yamk` offers an alternative tool to control the housekeeping tasks of a project, as well as the creation of executables and non-source files from source files.

## Installation

The easiest way is to use pip to install `yamk`.

```bash
pip install --user yamk
```

Please make sure that the correct directory is added to your path. This depends on the OS.

## CHANGELOG

Changelog is kept [here](https://github.com/spapanik/yamk/blob/master/CHANGELOG.md).

## Usage
`yamk`'s behaviour is defined in a toml file. The expected name is `make.toml`, but you can specify a different file if you want.

`yamk` can be invoked by using the command `yamk`, which is also aliased to `yam`. `yamk` follows the GNU recommendations for command line interfaces, and offers:
*  -h/--help              show this help message and exit
*  -V/--version           print the version and exit
*  -m/--makefile MAKEFILE the path to makefile (defaults to `./make.toml`)

## Terminology

* **Target**: A target is the file that needs to be created, or the task that should be done. The first type of targets is called a file target, and the second type, a phony target. A file target, is a file in the UNIX sense of what a file is.
* **Recipe**: A recipe is what tells `yamk` how to build a target, or do the task specified by the target.
* **Strength**: Whenever there is ambiguity in the variables or targets the strength of the variable or the target will be what will decide which will be executed.

## Recipes

A recipe has the following format:
```toml
[target_name]
<key_1> = <value_1>
<key_2> = <value_2>
...
<key_n> = <value_n>
```

## Targets

There are two groups of mutually exclusive types of targets: File/phony targets and static/regex targets. There are also two more cases, but they are not targets: Aliases and meta-targets.

### Meta-targets
A target starting with a single dollar sign is reserved by `yamk` itself, for meta-targets. If the target starts with more than one dollar sign, a single dollar sign is stripped, and it's a normal target or an alias. Currently the only meta-target is `$globals`, that has one valid key: `vars`. `vars` is the same as the key with the same name if static and regex targets, but weaker.

### Aliases
An alias has a single key, named `alias`, and the value of the key is the name of the target it aliases. 

### File targets
A file target is a target who doesn't have the `phony` key, or that the `phony` key is specifically set to a false value. The path can be with its absolute path, or the path relative to the makefile. Absolute paths are discouraged, as they limit the users ability to choose.

### Phony targets
A target that contains the `phony` key set to a true value, is a phony target.

### Static targets
A static target is a target who doesn't have the `regex` key, or that the `regex` key is specifically set to a false value.

### Regex targets
A target that contains the `regex` key set to a true value, is a regex target. A regex target is assumed to be a file target. In case the target matches a regex target, any name that was matched via a named grouped will be available as a variable. Regex targets are weaker than static ones.

## Keys

The following list contains all the valid keys. The list is in the form <key_name>: <value_type> (target types). A target type starting with a tilde(~) is an invalid target, and "any" means that this key is valid for all target types. Adding an invalid key is undefined behaviour that will most probably be ignored, or crash.

##### phony: boolean (~regex targets)
If set to true, it turns the target to a phony target.

##### regex: boolean (~phony targets)
If set to true, it turns the target to a regex target.

##### requires: array of strings (any)
An array of all the requirements for the target. The requirements that need to be built, are guaranteed to be built before the target, but there are no guarantees on the order that the requirements will be built.

##### commands: array of strings (any)
The commands to build the target.

##### vars: array of tables (any)
The variables specific to this target.

##### keep_ts: boolean (phony targets)
If set to true, this phony target will keep the timestamp when it was last built. In general, a phony target will be built every time, but a phony target with `keep_ts` set to true, will only be built if the kept timestamp is newer than the timestamp of the requirements.

##### exists_only: boolean (file targets)
If set to true, this file will be built only if it doesn't exist. The check for the existence is happening before any make command is run and there is a de-duplication step, but some care should be taken into account if it's created as a side-effect of another target.

##### recursive: boolean (file targets)
This makes sense only for directories. In this case, if it's set to true, the timestamp of the directory is taken to be the maximum of all the timestamps of all files, at any depth, inside it.

##### echo: boolean (any)
By default, the commands are not echoed before they are run. If set to true, they do.

##### allow_failures: boolean (any)
By default, a failing command will halt the execution of the makefile. This will allow `yamk` to try and recover from the error. Allow_failures doesn't guarantee that the execution will resume, because the nature of the failure may not allow that.

## Variables

A variable is defined in the key `vars`. The variables are parsed in order, so a variable, once defined can be used later. An example of `vars`:

```toml
[target_name]
vars = [
    {"[variable_options]var_1": <value_1>},
    {"[variable_options]var_2": <value_2>},
    ...
    {"[variable_options]var_n": <value_n>},
]
```

The options are completely optional, and they are comma separated.

A variable that resolves to a list or a dictionary will be treated as such. If it should be treated as a string instead instead of "${variable}", the form "${variable:}" should be used. If a variable is a part of a string, it will always be transformed into a string first. A key can be passed to pick up a specific value from a list or a dictionary, for example, "${list_var:0}" or "${dict_var:key}".

### Variable types

There are six types of variables: environment variables, argument, global, local, regex and implicit ones. With an increasing strength order:

##### Environment
All the environment variables gathered at the beginning of the execution of `yamk` are gathered into variables. They are the weakest variables.

##### Global
A global variable is a variable specified in the `$global` meta-target.

##### Local
A local variable is a variable specified by the `vars` key inside a target.

##### Regex
In the case of a regex target, any named group is a regex variable, which has the value of the matched text.

##### Argument
An argument variable is a variable defined with the --variable option when `yamk` was invoked.

##### Implicit
The implicit variables are variables created by the target itself, implicitly. They are guarded against overriding, as they start with a dot. This dot acts as a safeguard so they cannot mix with environment and regex ones. At the moment, the following two implicit variables exist:
* `.target`: the name of the target. In case of a file target, it's the absolute path to the file, regardless of they way it was defined.
* `.requirements`: the array of the requirements. All the file requirements are given as their absolute paths.
All the implicit variables, they are specific to the target that it's being built, i.e. if the file target is specified as a regular expression, the absolute path to the specific file, not the regex path.

### Variable options

The only option at the moment is `weak`.

##### Weak
Weak can be used to make the variable keep its value if it's not unset

## Commands

### Command options

There are two command options: `echo` and `allow_failures`. These commands can be used to customise the specific command, as if the respective variable was set.
