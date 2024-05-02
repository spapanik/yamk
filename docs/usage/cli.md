`yam` can be invoked by using the command `yam`, which is also aliased to `yamk`.
`yam` follows the GNU recommendations for command line interfaces, and offers:

#### -h/--help

show this help message and exit

#### -a/--assume dependency

assume that dependency is up to date (works only with phony ones)

#### -b/--bare

build only the target, without checking the dependencies

#### -c/--cookbook cookbook

the path to the cookbook (defaults to _./cookbook.toml_)

#### -d/--directory dir

the path to the directory that contains the cookbook

#### -f/--force

rebuild all dependencies and the target

#### -n/--dry-run

only print the commands to be executed

#### -r/--retry retries

retry commands for \<retries\> number of times

#### -s/--shell shell

the path to the shell used to execute the commands (defaults to _/bin/sh_)

#### -T/--time

print a timing report

#### -t/--cookbook-type {toml,json,yaml}

the type of the cookbook. defaults to file extension

#### -V/--version

print the version and exit

#### -v/--verbose

increase the level of verbosity

#### -x/--variable KEY=value

a list of variables to override the ones set in the cookbook, which should be in the form `<variable>=<value>`
