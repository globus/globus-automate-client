Migration to globus-sdk and globus-cli
======================================

The Globus Automate Client has been deprecated.
All functionality is now available in `globus-sdk`_ and
`globus-cli`_.

This document covers how usages and commands from Globus Automate Client can be
converted to use the new tools.

Translation Tables
==================

These tables provide summary information on how commands can be translated.

CLI Translation
---------------

In several cases, multiple commands translate to one command or one command translates to one
command.

In particular, the `globus-automate` CLI has several redundancies, all of which are explained as
aliases of one another.
This explanation is used in a few cases where the commands have very slightly different behavior but
are functionally aliases.

+-------------------------------------------+--------------------------------------+---------------------------+
| Old Command(s)                            | New Command(s)                       | Explanation               |
+===========================================+======================================+===========================+
| ``globus-automate queues``                | N/A                                  | No longer supported.      |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate action``                | N/A                                  | No longer supported.      |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate session``               | ``globus login``                     |                           |
|                                           | ``globus logout``                    |                           |
|                                           | ``globus whoami``                    |                           |
|                                           | ``globus session``                   |                           |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow action-cancel``    | ``globus flows run cancel``          | The ``globus-automate``   |
| ``globus-automate flow run-cancel``       |                                      | commands were aliases of  |
|                                           |                                      | one another. There is     |
|                                           |                                      | now only one command.     |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow action-enumerate`` | ``globus flows run list``            | The ``globus-automate``   |
| ``globus-automate flow action-list``      |                                      | commands were aliases of  |
| ``globus-automate flow run-enumerate``    |                                      | one another. There is     |
| ``globus-automate flow run-list``         |                                      | now only one command.     |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow action-log``       | ``globus flows run show-logs``       | The ``globus-automate``   |
| ``globus-automate flow run-log``          |                                      | commands were aliases of  |
|                                           |                                      | one another. There is     |
|                                           |                                      | now only one command.     |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow action-release``   | ``globus flows run delete``          | The ``globus-automate``   |
| ``globus-automate flow run-release``      |                                      | commands were aliases of  |
|                                           |                                      | one another. There is     |
|                                           |                                      | now only one command.     |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow action-resume``    | ``globus flows run resume``          | The ``globus-automate``   |
| ``globus-automate flow run-resume``       |                                      | commands were aliases of  |
|                                           |                                      | one another. There is     |
|                                           |                                      | now only one command.     |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow action-status``    | ``globus flows run show``            | The ``globus-automate``   |
| ``globus-automate flow run-status``       |                                      | commands were aliases of  |
|                                           |                                      | one another. There is     |
|                                           |                                      | now only one command.     |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow action-update``    | ``globus flows run update``          | The ``globus-automate``   |
| ``globus-automate flow run-update``       |                                      | commands were aliases of  |
|                                           |                                      | one another. There is     |
|                                           |                                      | now only one command.     |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow batch-run-update`` | N/A                                  | No longer supported.      |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow delete``           | ``globus flows delete``              |                           |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow deploy``           | ``globus flows create``              |                           |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow display``          | N/A                                  | No longer supported.      |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow get``              | ``globus flows show``                |                           |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow lint``             | N/A                                  | No longer supported.      |
|                                           |                                      | Validation is now the     |
|                                           |                                      | responsibility of the     |
|                                           |                                      | service.                  |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow list``             | ``globus flows list``                |                           |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow run``              | ``globus flows start``               |                           |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow run-definition``   | ``globus flows run show-definition`` |                           |
+-------------------------------------------+--------------------------------------+---------------------------+
| ``globus-automate flow update``           | ``globus flows update``              |                           |
+-------------------------------------------+--------------------------------------+---------------------------+


.. _globus-sdk: https://globus-sdk-python.readthedocs.io/en/stable/

.. _globus-cli: https://docs.globus.org/cli/
