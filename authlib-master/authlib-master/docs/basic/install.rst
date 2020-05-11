.. _install:

Installation of Authlib
=======================

.. meta::
    :description: How to install Authlib with pip, source code, etc.

This part of the documentation covers the installation of Authlib, just
like any other software package needs to be installed first.


$ pip install Authlib
---------------------


Installing Authlib is simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install Authlib

It will also install the dependencies:

- cryptography

.. note::
    You may enter problems when installing cryptography, check its official
    document at https://cryptography.io/en/latest/installation/

.. versionchanged:: v0.12

    "requests" is an optional dependency since v0.12. If you want to use
    Authlib client, you have to install "requests" by yourself. Or, you can
    install Authlib with::

    $ pip install Authlib[client]

Get the Source Code
-------------------

Authlib is actively developed on GitHub, where the code is
`always available <https://github.com/lepture/authlib>`_.

You can either clone the public repository::

    $ git clone git://github.com/lepture/authlib.git

Download the `tarball <https://github.com/lepture/authlib/tarball/master>`_::

    $ curl -OL https://github.com/lepture/authlib/tarball/master

Or, download the `zipball <https://github.com/lepture/authlib/zipball/master>`_::

    $ curl -OL https://github.com/lepture/authlib/zipball/master


Once you have a copy of the source, you can embed it in your Python package,
or install it into your site-packages easily::

    $ cd authlib
    $ pip install .
