=====================
yam: yet another make
=====================

.. image:: https://github.com/spapanik/yamk/actions/workflows/build.yml/badge.svg
  :alt: Build
  :target: https://github.com/spapanik/yamk/actions/workflows/build.yml
.. image:: https://img.shields.io/lgtm/alerts/g/spapanik/yamk.svg
  :alt: Total alerts
  :target: https://lgtm.com/projects/g/spapanik/yamk/alerts/
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
  :alt: Code style
  :target: https://github.com/psf/black

``yam`` offers an alternative tool to control the housekeeping tasks of
a project, as well as the creation of executables and non-source files
from source files.

In a nutshell
-------------

Installation
^^^^^^^^^^^^

The easiest way is to use pip to install ``yam``.

.. code:: console

   $ pip install --user yamk

Please make sure that the correct directory is added to your path. This
depends on the OS.

Usage
^^^^^

``yam``'s behaviour is defined in a toml file, called a cookbook. The default name is ``make.toml``,
but you can specify a different file if you want. Specifying a name ``<name.toml>`` will also parse all the ``.toml``
files in the directory named ``<name.toml>.d``.

``yam`` can be invoked by using the command ``yam``, which is also
aliased to ``yamk``. ``yam`` follows the GNU recommendations for command
line interfaces.

Links
-----

- `Documentation`_
- `Changelog`_


.. _Changelog: https://github.com/spapanik/yamk/blob/main/CHANGELOG.rst
.. _Documentation: https://yamk.readthedocs.io/en/latest/
