

Identifiers
===========

Minids can be created in two different namespaces:

* minid -- Production minids are permanent and will last forever
* minid.test -- Test Minids are temporary and are encouraged for prototyping

Although the Identifiers Service can define many namespaces, Minid will likely
only use the two to keep things simple.


Minids vs Handles
-----------------

You may see Minids in a few different formats. Minid currently uses the ``hdl://``
provider in order to mint the identifier, but the same identifier can also be
written as a ``minid:`` for simplicity. The two below are equivalent:

* minid.test:1HK1DTv1wPt3a
* hdl:20.500.12633/1HK1DTv1wPt3a

The Minid Client understands both::

  $ minid check hdl:20.500.12633/1HK1DTv1wPt3a
  $ minid check minid.test:1HK1DTv1wPt3a


Minids by Checksums
-------------------

Minid will automatically checksum any files registered with the CLI::

  $ minid register --test foo.txt

If you have the file, but lost the identifier, you can check the file instead::

  $ minid check foo.txt


