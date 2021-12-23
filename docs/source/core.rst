=====================
yam: yet another make
=====================

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

``yam``'s behaviour is defined in a toml file, called a cookbook. The default name is `make.toml``,
but you can specify a different file if you want. Specifying a name ``<name.toml>`` will also parse all the ``.toml``
files in the directory named ``<name.toml>.d``.

``yam`` can be invoked by using the command ``yam``, which is also
aliased to ``yamk``. ``yam`` follows the GNU recommendations for command
line interfaces.
