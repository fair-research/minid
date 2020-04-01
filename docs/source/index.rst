.. Minid documentation master file, created by
   sphinx-quickstart on Tue Mar 10 11:47:48 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Minid (Minimal Viable Identifier)
=================================


A minid (Minimal Viable Identifier) is an identifier that is sufficiently
simple to make creation and use trivial, while still having enough substance
to make data easily findable, accessible, interoperable, and reusable (FAIR).


Requirements
------------

Minid 2.0.0 Requires Python 3.6 or higher.

Installation
------------

Minid Client 2.0.0 is avaialble on PyPI. You can install it with the following command::

  $ pip install --pre minid


You can also install the `legacy Minid 1.3.0 version <https://github.com/fair-research/minid/tree/1.3.0>`_ with::

  $ pip install minid==1.3.0

Alternatively, you can download the source code and install using setup tools::

  $ git clone https://github.com/fair-research/minid
  $ python setup.py install


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   identifiers
   scripting
   remote_file_manifests
   glossary


Quick Start
-----------


The CLI supports the following simple operations (Note: the `--test` flag creates names in a test namespace that is removed periodically; remove that flag to create production minids.):

* Login with Globus::

    $ minid login

* Create a new identifier::

    $ minid register --test [--title <title>] <file_name> [--locations <loc1>..<locN>]

* Retrieve metadata about a file::

    $ minid check <file_name>

* Retrieve metadata about an identifier::

    $ minid check <identifier>

* Update metadata about an identifier::

    $ minid update [--test] [--title <title>] [--locations <loc1> <loc2>] <identifier>

* Logout to clear credentials::

    $ minid logout

*  View all minid options::

    $ minid -h

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
