.. image:: https://travis-ci.com/fair-research/minid.svg?branch=develop
    :target: https://travis-ci.com/fair-research/minid

.. image:: https://coveralls.io/repos/github/fair-research/minid/badge.svg?branch=develop
    :target: https://coveralls.io/github/fair-research/minid?branch=develop

.. image:: https://img.shields.io/pypi/v/minid.svg
    :target: https://pypi.python.org/pypi/minid

.. image:: https://img.shields.io/pypi/wheel/minid.svg
    :target: https://pypi.python.org/pypi/minid

.. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
    :alt: License
    :target: https://opensource.org/licenses/Apache-2.0

Minimal Viable Identifier Client
================================

A minid (Minimal Viable Identifier) is an identifier that is sufficiently simple to make creation and use trivial, while still having enough substance to make data easily findable, accessible, interoperable, and reusable (FAIR). 


See the `Read The Docs <https://minid.readthedocs.io/en/develop>`_ page for more info.

Usage
-----
Minid 2.0.0 requires python 3.6 or higher::

  $ pip install --pre minid

Minting identifiers is simple and easy::

    $ minid login
    $ minid register --test [--title <title>] <file_name> [--locations <loc1>..<locN>]
