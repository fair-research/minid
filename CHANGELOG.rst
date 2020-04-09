CHANGELOG
=========

2.0.0b3
-------

* Fixed Fixed possible missing directory for minid (`#54`_)

.. _#54: https://github.com/fair-research/minid/pull/54


2.0.0b2
-------

* Added a Read-The-Docs page (`#49`_)
* Switched badges to develop branch (`#51`_)
* Fixed file-not-found bug (`#52`_)

.. _#49: https://github.com/fair-research/minid/pull/49
.. _#51: https://github.com/fair-research/minid/pull/51
.. _#52: https://github.com/fair-research/minid/pull/52



2.0.0b1
-------

* Major overhaul of both Minid client/server (`#26`_)
* Switch resource server to https://identifiers.fair-research.org/
* Switch Auth mechanism to use Globus Auth
* Client now based around the Fair Identifiers Client for minting identifiers

.. _#26: https://github.com/fair-research/minid/pull/42

1.3.0
-----

* Fixed misleading error when user registers file without an email
* Update batch_register function to prefer recent minted identifier
* Do client swapping of "minid:" and "ark:/57799/" and vice-versa
