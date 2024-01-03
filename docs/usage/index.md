# Usage

`yam`'s behaviour is defined in a file, called a cookbook. The default name is
`cookbook.<extension>`, but if a different filename is required, it can be passed
using the `-c/--cookbook` flag. The supported extensions are:

- toml
- yml,yaml
- json

If the cookbook has a different extension, the type won't be automatically recognised,
but this can be configured by the `-t/--cookbook-type` flag.

## Recipes

A cookbook is a collection of recipes. A recipe has the following format:

``` toml title="cookbook.toml"
[target_name]
"<key_1>" = "<value_1>"
"<key_2>" = "<value_2>"
# ...
"<key_n>" = "<value_n>"
```

## Targets

There are two groups of mutually exclusive types of targets: File/phony targets and
static/regex targets. There are also two more target-like possible entries in the cookbook,
but they are not targets: Aliases and meta-targets.

### Meta-targets

A target starting with a single dollar sign is reserved by `yam` itself, for meta-targets.
To use a normal target that starts with a dollar sign, use one more dollar sign, than what
is needed, and `yam` will strip one of them and turn it into a normal target or an alias.
Currently the only meta-target is `$globals`, that has 3 valid keys:

- `vars`, which is the same as the key with the same name in targets, but weaker
- `shell`, to override the default shell used to execute the commands
- `version`, which is the minimum version of `yam` needed for the cookbook.

### Aliases

An alias has a single key, named `alias`, and the value of the key is the name of the
target it is an alias for.

### File targets

A file target is a target who doesn't have the `phony` key, or that the `phony` key is
specifically set to a false value. The path can be with its absolute path, or the path
relative to the cookbook. Absolute paths are **strongly** discouraged, as they tend to
make assumptions about the directory structure.

### Phony targets

A target that contains the `phony` key set to a true value, is a phony target. It
generally signifies a target that will not have a file as its output.

### Static targets

A static target is a target who doesn't have the `regex` key, or that the `regex` key is
specifically set to a false value. A static target will be called verbatim.

### Regex targets

A target that contains the `regex` key set to a true value, is a regex target. Regex targets
are weaker than static ones, which means that if you have the following targets in a cookbook:

``` toml title="cookbook.toml"
['echo_(?P<number>\d+)']
regex = true
commands = [
    "echo ${number}"
]

[echo_42]
regex = true
commands = [
    "echo The answer to life, the universe, and everything"
]
```

Then `yam echo_42` will result to `The answer to life, the universe, and everything`
and not `42`.

## Variables

A variable is defined in the key `vars`. The variables are parsed in order, so a variable,
once defined can be used later. An example of `vars`:

``` toml
[target_name.vars]
"[variable_options]var_1" = "<value_1>"
"[variable_options]var_2" = "<value_2>"
# ...
"[variable_options]var_n" = "<value_n>"
```

The options are completely optional, and they are comma separated.

A variable that resolves to a list or a dictionary will be treated as such. If it should be
treated as a string instead instead of "${variable}", the form "${variable:}" should be used.
If a variable is a part of a string, it will always be transformed into a string first. A
key can be passed to pick up a specific value from a list or a dictionary, for example,
"${list_var:0}" or "${dict_var:key}".

## Variable types

There are six types of variables: global, regex, implicit, local, environment and argument ones.
If a variable is being used within a command and it's not set, it will be treated as the empty
string. With an increasing strength order:

#### Global

A global variable is a variable specified in the *$global* meta-target. They are the least specific,
and therefore the weakest variables.

#### Implicit

The implicit variables are variables created by the target itself, implicitly. They are guarded against
overriding, as they start with a dot. This dot acts as a safeguard so they cannot mix with environment ones.
At the moment, the following three implicit variables exist:

- **.target**: the name of the target. In case of a file target, it's the absolute path to the file, regardless
  of they way it was defined.
- **.requirements**: the array of the requirements. All the file requirements are given as their absolute paths.
- **.extra**: an array of all the extra arguments passed to the yam command.

#### Regex

In the case of a regex target, any named group is a regex variable, which has the value of the matched text.

#### Local

A local variable is a variable specified by the `vars` key inside a target.

#### Environment

All the environment variables gathered at the beginning of the execution of `yam` are gathered into variables.

#### Argument

An argument variable is a variable defined with the --variable option when `yam` was invoked.

## Variable options

The only option at the moment is `weak` and `strong`.

#### Weak

`weak` can be used to make the variable be ignored if it's set by a weaker type

#### Strong

`strong` can be used to make the variable keep it's value against stronger types

## Commands

### Command options

There are two command options: *echo* and *allow_failures*. These commands can be used to customise the specific command,
as if the respective variable was set.
