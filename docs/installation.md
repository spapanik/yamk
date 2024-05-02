# Installation

The easiest way is to use [pipx] to install `yamk`.

```console
$ pipx install yamk
```

This is the only officially supported way of installing it.

Alternatively, you can install it with [pip]:

```console
$ pip install --user yamk
```

The biggest issue with this approach is that you won't have an isolated
environment for `yam`, therefore you might run into dependency
conflicts, and so this is neither recommended nor supported.

[pip]: https://pip.pypa.io/en/stable/
[pipx]: https://pypa.github.io/pipx/
[pyenv]: https://github.com/pyenv/pyenv
