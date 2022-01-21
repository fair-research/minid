CHANGELOG
=========

2.0.1
-----

* General fixes and updates to docs and README

2.0.0
-----

Minid 2.0.0 is a substantial upgrade including a full switch to Globus Auth,
use of a new resource server, and an overhaul of the internal SDK and CLI. Highlights
are shown below, but more information can be found in the beta releases and in git.

* Major overhaul of both Minid client/server (`#26`_)
* Switch resource server to https://identifiers.fair-research.org/
* Switch Auth mechanism to use Globus Auth
* Client now based around the Fair Identifiers Client for minting identifiers
* Switched CLI from a custom ArgumentParser implementation to Click (`#70`_)


2.0.0b8
-------

* Unpin Globus SDK (Now handled by fair-identifiers-client)
* Bump requirements for fair-identifiers-client (support globus-sdk v3) (`#80`_)

.. _#80: https://github.com/fair-research/minid/pull/80


2.0.0b7
-------

* Pin Globus SDK version 2
* Pin tzlocal version 2


2.0.0b6
-------

* Changed Batch Register behavior (`#77`_)
   * batch register now creates new minids each time by default
   * added new ``update_if_changed`` option
   * Fixed batch register re-using minids from another namespace

.. _#77: https://github.com/fair-research/minid/pull/77


2.0.0b5
-------

* Switched CLI from a custom ArgumentParser implementation to Click (`#70`_)
* Locations field is now specified as a comma-delimited list (`#70`_)

.. _#70: https://github.com/fair-research/minid/pull/70


2.0.0b4
-------

* Improved performance of batch processing (`#67`_)

.. _#67: https://github.com/fair-research/minid/pull/67


2.0.0b3
-------

* Fixed Fixed possible missing directory for minid (`#54`_)
* Added this changelog (`#55`_)
* Removed EZID link from Minid check command (`#60`_)
* Added new fields to Minid check command (`#60`_)

  * Added Created Date
  * Added Updated Date
  * Added Replaced By reference to remote Minid
  * Added Replaces reference to remote Minid
  * Added Active Minid Status Indicator
  * Size now displays units instead of bytes
  * Minid style now displayed instead of hld:// or ark://
  * Fixed newer style titles not displaying

* (Re)Added Tombstoning features (`#61`_)
* Added feature to clear Location and reference Minids by passing "None" (`#61`_)
* Fixed Unexpected Error if user declines consent on login (`#64`_)
* Added Main development feature to run the CLI without installing (`#62`_)


.. _#54: https://github.com/fair-research/minid/pull/54
.. _#55: https://github.com/fair-research/minid/pull/55
.. _#60: https://github.com/fair-research/minid/pull/60
.. _#61: https://github.com/fair-research/minid/pull/61
.. _#62: https://github.com/fair-research/minid/pull/62
.. _#64: https://github.com/fair-research/minid/pull/64


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
