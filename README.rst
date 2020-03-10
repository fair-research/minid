.. image:: https://travis-ci.org/fair-research/minid.svg?branch=master
    :target: https://travis-ci.org/fair-research/minid

.. image:: https://coveralls.io/repos/github/fair-research/minid/badge.svg?branch=master
    :target: https://coveralls.io/github/fair-research/minid?branch=master

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


Requirements
------------

Minid Requires the following:

* Python 3.6 or higher


Installation
------------

The minid client and CLI is avaialble on PyPI. You can install it with the following command::
  
  $ pip install minid
  
Alternatively, you can download the source code and install using setup tools::

  $ git clone https://github.com/fair-research/minid
  
  $ python setup.py install

Usage
-----

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

Landing pages are accessible via the minid website: minid.bd2k.org/minid/landingpage/<identifier>. 

Scripting
---------

You can import the `MinidClient` for scripting::

    from minid import MinidClient
    client = MinidClient()
    client.login()
    client.register('foo.txt', title='My Foo File', locations=['http://example.com/foo.txt'])
    client.logout()

file manifest format
--------------------
Minids can only be assigned to a single file. In order to assign a minid to a collection of files we recommend using a `BDBag <https://github.com/ini-bdds/bdbag>`_ or the minid file manifest format. 

The minid file manifest format is a JSON-based format that enumerates a list of files as JSON objects that have the following attributes:

* length: The length of the file in bytes.

* filename: The filename (or path) relative to the manifest file.

* One or more (only one of each) of the following `algorithm:checksum` key-value pairs:
  
  * md5:<md5 hex value>
  
  * sha256:<sha256 hex value>
  
  * sha512:<sha512 hex value>

* url: the URL to the file.

The manifest may be used to create a minid for a collection of files or alternatively as input to the minid batch-register command. 

Below is a sample file manifest configuration file::

  [
      {
          "length":321,
          "filename":"file1.txt",
          "md5":"5bbf5a52328e7439ae6e719dfe712200",
          "sha256":"2c8b08da5ce60398e1f19af0e5dccc744df274b826abe585eaba68c525434806",
          "url" : "globus://ddb59aef-6d04-11e5-ba46-22000b92c6ec/share/godata/file1.txt"
      },
      {
          "length": 632860,
          "filename": "minid_v0.1_Nov_2015.pdf",
          "sha256": "cacc1abf711425d3c554277a5989df269cefaa906d27f1aaa72205d30224ed5f",
          "url" : "http://bd2k.ini.usc.edu/assets/all-hands-meeting/minid_v0.1_Nov_2015.pdf"
      }
  ]


More information
----------------

"`I'll take that to go: Big data bags and minimal identifiers for exchange of large, complex datasets <https://zenodo.org/record/820878>`_" explains the motivation for Minids and the related BDBag construct, provides details on design and implementation, and gives examples of use.

"`Reproducible big data science: A case study in continuous FAIRness <https://www.biorxiv.org/content/early/2018/02/27/268755>`_" presents a use case in which BDBags and Minids are used to capture a transcription factor binding site analysis.

More information about the project can be found at: `http://minid.bd2k.org/ <http://minid.bd2k.org/>`_
