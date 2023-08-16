Migration to globus-sdk and globus-cli
======================================

The Globus Automate Client has been deprecated.
All functionality is now available in `globus-sdk`_ and
`globus-cli`_.

This document covers how usages and commands from Globus Automate Client can be
converted to use the new tools.

Translation Tables
------------------

These tables provide summary information on how commands can be translated.

CLI Translation
~~~~~~~~~~~~~~~

In several cases, multiple commands translate to one command or one command translates to one
command.

In particular, the ``globus-automate`` CLI has a number of redundancies and
aliases, which are replaced with singular commands in `globus-cli`_.

Additionally, several commands from the ``globus-automate`` CLI are mapped to
"N/A", meaning they have no new equivalents.
These commands refer to fully deprecated functionality or functionality which
is now provided in a completely different way -- for example,
``globus-automate flow lint`` provided logic which is now incorporated into the
Globus Flows service as part of *flow* creation.

+-------------------------------------------+--------------------------------------+
| Old Command(s)                            | New Command(s)                       |
+===========================================+======================================+
| ``globus-automate queues``                | N/A                                  |
+-------------------------------------------+--------------------------------------+
| ``globus-automate action``                | N/A                                  |
+-------------------------------------------+--------------------------------------+
| ``globus-automate session``               | ``globus login``                     |
|                                           |                                      |
|                                           | ``globus logout``                    |
|                                           |                                      |
|                                           | ``globus whoami``                    |
|                                           |                                      |
|                                           | ``globus session``                   |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow action-cancel``    | ``globus flows run cancel``          |
|                                           |                                      |
| ``globus-automate flow run-cancel``       |                                      |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow action-enumerate`` | ``globus flows run list``            |
|                                           |                                      |
| ``globus-automate flow action-list``      |                                      |
|                                           |                                      |
| ``globus-automate flow run-enumerate``    |                                      |
|                                           |                                      |
| ``globus-automate flow run-list``         |                                      |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow action-log``       | ``globus flows run show-logs``       |
|                                           |                                      |
| ``globus-automate flow run-log``          |                                      |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow action-release``   | ``globus flows run delete``          |
|                                           |                                      |
| ``globus-automate flow run-release``      |                                      |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow action-resume``    | ``globus flows run resume``          |
|                                           |                                      |
| ``globus-automate flow run-resume``       |                                      |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow action-status``    | ``globus flows run show``            |
|                                           |                                      |
| ``globus-automate flow run-status``       |                                      |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow action-update``    | ``globus flows run update``          |
|                                           |                                      |
| ``globus-automate flow run-update``       |                                      |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow batch-run-update`` | N/A                                  |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow delete``           | ``globus flows delete``              |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow deploy``           | ``globus flows create``              |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow display``          | N/A                                  |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow get``              | ``globus flows show``                |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow lint``             | N/A                                  |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow list``             | ``globus flows list``                |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow run``              | ``globus flows start``               |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow run-definition``   | ``globus flows run show-definition`` |
+-------------------------------------------+--------------------------------------+
| ``globus-automate flow update``           | ``globus flows update``              |
+-------------------------------------------+--------------------------------------+

SDK Translation
~~~~~~~~~~~~~~~

The Globus Automate Client's functionality as a python library is primarily
provided by the following four components, which map onto different components
in the Globus SDK:

+-------------------------------------------+--------------------------------------+
| ``globus_automate_client`` Component      | ``globus_sdk`` Component             |
+===========================================+======================================+
| ``ActionClient``                          | N/A                                  |
+-------------------------------------------+--------------------------------------+
| ``FlowsClient``                           | ``FlowsClient``                      |
|                                           |                                      |
|                                           | ``SpecificFlowClient``               |
+-------------------------------------------+--------------------------------------+
| ``create_action_client``                  | N/A                                  |
+-------------------------------------------+--------------------------------------+
| ``create_flows_client``                   | ``tokenstorage``                     |
|                                           |                                      |
|                                           | ``NativeAppAuthClient`` or           |
|                                           | ``ConfidentialAppAuthClient``        |
|                                           |                                      |
|                                           | ``FlowsClient`` or                   |
|                                           | ``SpecificFlowClient``               |
+-------------------------------------------+--------------------------------------+

The ``ActionClient`` is effectively removed, and the ``FlowsClient`` is split
in two.

The ``create_flow_client`` helper has no singular replacement. Instead, users
should expect to write a small block of code to correctly authenticate pass the
resulting authorizer to the matching client class. See `the globus-sdk example
usage <https://gist.github.com/sirosen/c7dd9fd00a41b7a4fc6b1c79d84d2eaf>`_ for
an example of how to do this.

In addition to the high-level component mapping, it's valuable to enumerate the
mapping of methods for the ``FlowsClient``.

+-----------------------------------------------+--------------------------------------+
| ``globus_automate_client.FlowsClient`` Method | ``globus_sdk`` Method                |
+===============================================+======================================+
| ``deploy_flow``                               | ``FlowsClient.create_flow``          |
+-----------------------------------------------+--------------------------------------+
| ``update_flow``                               | ``FlowsClient.update_flow``          |
+-----------------------------------------------+--------------------------------------+
| ``get_flow``                                  | ``FlowsClient.get_flow``             |
+-----------------------------------------------+--------------------------------------+
| ``list_flows``                                | ``FlowsClient.list_flows``           |
+-----------------------------------------------+--------------------------------------+
| ``delete_flow``                               | ``FlowsClient.delete_flow``          |
+-----------------------------------------------+--------------------------------------+
| ``flow_action_status``                        | ``FlowsClient.get_run``              |
+-----------------------------------------------+--------------------------------------+
| ``get_flow_definition_for_run``               | ``FlowsClient.get_run_definition``   |
+-----------------------------------------------+--------------------------------------+
| ``flow_action_release``                       | ``FlowsClient.delete_run``           |
+-----------------------------------------------+--------------------------------------+
| ``flow_action_cancel``                        | ``FlowsClient.cancel_run``           |
+-----------------------------------------------+--------------------------------------+
| ``enumerate_runs``                            | ``FlowsClient.list_runs``            |
|                                               |                                      |
| ``enumerate_actions``                         |                                      |
|                                               |                                      |
| ``list_flow_actions``                         |                                      |
|                                               |                                      |
| ``list_flow_runs``                            |                                      |
+-----------------------------------------------+--------------------------------------+
| ``flow_action_update``                        | ``FlowsClient.update_run``           |
+-----------------------------------------------+--------------------------------------+
| ``update_runs``                               | N/A                                  |
+-----------------------------------------------+--------------------------------------+
| ``flow_action_log``                           | ``FlowsClient.get_run_logs``         |
+-----------------------------------------------+--------------------------------------+
| ``scope_for_flow``                            | ``SpecificFlowClient.scopes`` [*]_   |
+-----------------------------------------------+--------------------------------------+
| ``flow_action_resume``                        | ``SpecificFlowClient.resume_run``    |
+-----------------------------------------------+--------------------------------------+
| ``run_flow``                                  | ``SpecificFlowClient.run_flow``      |
+-----------------------------------------------+--------------------------------------+


.. [*] ``scopes`` is an instance attribute of ``SpecificFlowClient``, so usage is
    slightly different from a method, but the information provided is the same.

.. _globus-sdk: https://globus-sdk-python.readthedocs.io/en/stable/

.. _globus-cli: https://docs.globus.org/cli/
