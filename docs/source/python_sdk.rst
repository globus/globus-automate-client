.. module:: globus_automate_client

Python SDK
==========

The Globus Automate Client package also provides a Python client for
interfacing with and invoking Globus Actions and Flows. Below, we provide
information on helper functions available for creating authenticated Action and
Flow clients as well as documentation on the methods available to those clients.

Actions
^^^^^^^

.. autoclass:: globus_automate_client.action_client.ActionClient
    :members:
    :member-order: bysource

Helper
------

.. autofunction:: globus_automate_client.create_action_client


Flows
^^^^^

.. autoclass:: globus_automate_client.flows_client.FlowsClient
   :members:
   :member-order: bysource

Helper
------

.. autofunction:: globus_automate_client.create_flows_client

Examples
^^^^^^^^

SDK Helpers
-----------

If you're running the SDK locally in a secure location, you will probably want
to use the provided convenience functions, ``create_action_client`` and
``create_flows_client``. These functions share functionality with the
``globus-automate`` CLI to handle loading and storing Globus Auth
tokens on the local filesystem and trigger interactive logins when additional
consents are required to interact with Actions or Flows:

.. literalinclude:: code_snippets/create_action_client.py
  :language: python
  :emphasize-lines: 4

The ``create_flows_client`` helper requires a Globus Auth client ID instead of
an Action URL on instantiation. Feel free to use the client ID associated with
this package:

.. literalinclude:: code_snippets/create_flows_client.py
  :language: python
  :emphasize-lines: 2,6

SDK - The Hard Way
------------------

There are plenty of scenarios in which the helper functions above should *NOT*
be used, included in those are:

- The SDK is being run on a platform without access to the local filesystem (or
  it is preferable not to write to the local filesystem).
- You do not want to (or cannot) trigger interactive logins during execution.
- The SDK is being used as part of another service or in a pipeline

In this case, you'll need to create the clients using the ``new_client``
classmethod attached to each client. When creating an ActionClient, you'll need
to create and supply the appropriate GlobusAuthorizer_ for the action.

When creating a FlowsClient, you'll need to create a GlobusAuthorizer_ that
gives access to the MANAGE_FLOWS_SCOPE. This authorizer will be used to manage
interactions against the Flows service, such as creating a new Flow, updating an
existing Flow, or deleting an old Flow. Additionally, you'll need to create a
callback that accepts three keyword-arguments, ``flow_url``, ``flow_scope`` and
``client_id`` and returns a GlobusAuthorizer_ that will be used to provide
access to specific Flows. This authorizer allows the SDK to run operations
against the Flow, such as running a Flow and checking an execution's status.

The example below shows an example defining the callback used to create a
GlobusAuthorizer_ by pulling tokens from environment variables.

.. literalinclude:: code_snippets/premade_authorizers.py
  :language: python
  :emphasize-lines: 14,38


.. _GlobusAuthorizer: https://globus-sdk-python.readthedocs.io/en/stable/authorization.html#globus_sdk.authorizers.base.GlobusAuthorizer
