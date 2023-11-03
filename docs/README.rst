=====================
yam: yet another make
=====================

.. image:: https://github.com/spapanik/yamk/actions/workflows/tests.yml/badge.svg
  :alt: Tests
  :target: https://github.com/spapanik/yamk/actions/workflows/tests.yml
.. image:: https://img.shields.io/github/license/spapanik/yamk
  :alt: License
  :target: https://github.com/spapanik/yamk/blob/main/LICENSE.txt
.. image:: https://img.shields.io/pypi/v/yamk
  :alt: PyPI
  :target: https://pypi.org/project/yamk
.. image:: https://pepy.tech/badge/yamk
  :alt: Downloads
  :target: https://pepy.tech/project/yamk
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
  :alt: code style: black
  :target: https://github.com/psf/black
.. image:: https://img.shields.io/badge/build%20automation-yamk-success
  :alt: build automation: yam
  :target: https://github.com/spapanik/yamk
.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
  :alt: Lint: ruff
  :target: https://github.com/charliermarsh/ruff

``yam`` offers an alternative tool to control the housekeeping tasks of
a project, as well as the creation of executables and non-source files
from source files.

In a nutshell
-------------

Installation
^^^^^^^^^^^^

The easiest way is to use `pipx`_ to install ``yam``.

.. code:: console

   $ pipx install yamk

Usage
^^^^^

``yam``'s behaviour is defined in a toml file, called a cookbook. The default name is ``make.toml``,
but you can specify a different file if you want. Specifying a name ``<name.toml>`` will also parse all the ``.toml``
files in the directory named ``<name.toml>.d``.

``yam`` can be invoked by using the command ``yam``, which is also aliased to ``yamk``. ``yam`` follows
the GNU recommendations for command line interfaces.

Links
-----

- `Documentation`_
- `Changelog`_


.. _Changelog: https://github.com/spapanik/yamk/blob/main/docs/CHANGELOG.rst
.. _Documentation: https://yamk.readthedocs.io/en/stable/
.. _pipx: https://pypa.github.io/pipx/
