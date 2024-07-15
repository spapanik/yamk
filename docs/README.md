# yam: yet another make

[![tests][test_badge]][test_url]
[![license][licence_badge]][licence_url]
[![pypi][pypi_badge]][pypi_url]
[![downloads][pepy_badge]][pepy_url]
[![code style: black][black_badge]][black_url]
[![build automation: yam][yam_badge]][yam_url]
[![Lint: ruff][ruff_badge]][ruff_url]

`yam` offers an alternative tool to control the housekeeping tasks of a project,
as well as the creation of executables and non-source files from source files. It's
inspired from `GNU make`, but offers more flexibility with regular expressions
and phony targets.

## Features

### Phony timestamps

Makefiles are nowadays used more and more often to execute phony targets as with
interpreted languages, there is no compiled file as output. The prerequisites are
often other phony targets, which can add unnecessary rebuilds. `yam` can keep the
track if there is a need to rebuild the phony target, and avoid them.

### Regex recipes

`GNU make` targets can only have only a single % in a pattern. This is rather restrictive,
especially in web development. `yam` allows a prerequisite or a target to be a regex,
allowing much more flexibility.

### Variety of configuration files

`yam` allows a multiple file types to configure it, to fit your needs: `toml`, `yaml`,
and `json` files are all welcome here.

### Local overrides

We realise that the modern development is a team sport, and that developers need the
freedom to configure something that isn't optimal for their environment. Following the
great UNIX tradition, everything in a cookbook can be locally overridden by files with
the same extension inside a directory named `<cookbook_filename>.d/`.

## Links

-   [Documentation]
-   [Changelog]

[test_badge]: https://github.com/spapanik/yamk/actions/workflows/tests.yml/badge.svg
[test_url]: https://github.com/spapanik/yamk/actions/workflows/tests.yml
[licence_badge]: https://img.shields.io/pypi/l/yamk
[licence_url]: https://github.com/spapanik/yamk/blob/main/docs/LICENSE.md
[pypi_badge]: https://img.shields.io/pypi/v/yamk
[pypi_url]: https://pypi.org/project/yamk
[pepy_badge]: https://pepy.tech/badge/yamk
[pepy_url]: https://pepy.tech/project/yamk
[black_badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black_url]: https://github.com/psf/black
[yam_badge]: https://img.shields.io/badge/build%20automation-yamk-success
[yam_url]: https://github.com/spapanik/yamk
[ruff_badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
[ruff_url]: https://github.com/charliermarsh/ruff
[Documentation]: https://yamk.readthedocs.io/en/stable/
[Changelog]: https://github.com/spapanik/yamk/blob/main/docs/CHANGELOG.md
[Project Euler]: https://projecteuler.net/
[leetcode]: https://leetcode.com/
[topcoder]: https://www.topcoder.com/
