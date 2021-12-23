.. raw:: html

    <p style="text-align:center">
        <a href="https://github.com/spapanik/yamk/actions/workflows/build.yml">
            <img alt="Build" src="https://github.com/spapanik/yamk/actions/workflows/build.yml/badge.svg">
        </a>
        <a href="https://lgtm.com/projects/g/spapanik/yamk/alerts/">
            <img alt="Total alerts" src="https://img.shields.io/lgtm/alerts/g/spapanik/yamk.svg">
        </a>
        <a href="https://github.com/spapanik/yamk/blob/main/LICENSE.txt">
            <img alt="License" src="https://img.shields.io/github/license/spapanik/yamk">
        </a>
        <a href="https://pypi.org/project/yamk">
            <img alt="PyPI" src="https://img.shields.io/pypi/v/yamk">
        </a>
        <a href="https://pepy.tech/project/yamk">
            <img alt="Downloads" src="https://pepy.tech/badge/yamk">
        </a>
        <a href="https://github.com/psf/black">
            <img alt="Code style" src="https://img.shields.io/badge/code%20style-black-000000.svg">
        </a>
    </p>

======================
yamk: yet another make
======================

``yamk`` offers an alternative tool to control the housekeeping tasks of
a project, as well as the creation of executables and non-source files
from source files.

In a nutshell
-------------

Installation
~~~~~~~~~~~~

The easiest way is to use pip to install ``yamk``.

.. code:: console

   $ pip install --user yamk

Please make sure that the correct directory is added to your path. This
depends on the OS.

Usage
~~~~~

``yam``'s behaviour is defined in a toml file, called a cookbook. The default name is `make.toml``,
but you can specify a different file if you want. Specifying a name ``<name.toml>`` will also parse all the ``.toml``
files in the directory named ``<name.toml>.d``.

``yam`` can be invoked by using the command ``yam``, which is also
aliased to ``yamk``. ``yam`` follows the GNU recommendations for command
line interfaces.

Links
-----

- `Changelog`_
- `Documentation`_


.. _Changelog: https://github.com/spapanik/yamk/blob/main/CHANGELOG.rst
.. _Documentation: https://yamk.readthedocs.io/en/latest/
