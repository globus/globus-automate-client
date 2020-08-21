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

.. autofunction:: globus_automate_client.action_client.create_action_client

Example
-------

.. code-block:: python

    from globus_automate_client.action_client import create_action_client

    ac = create_action_client("https://actions.globus.org/hello_world")

    # Launch an Action and check its results
    resp = ac.run({"echo_string": "Hello from SDK"})
    assert resp.data["status"] == "SUCCEEDED"
    print(resp.data)


Flows
^^^^^

.. autoclass:: globus_automate_client.flows_client.FlowsClient
   :members:
   :member-order: bysource

Helper
------

.. autofunction:: globus_automate_client.flows_client.create_flows_client

Example
-------

.. code-block:: python

    from globus_automate_client.flows_client import create_flows_client
    from globus_automate_client.token_management import CLIENT_ID

    fc = create_flows_client(CLIENT_ID)

    # Get a listing of runnable, deployed flows
    available_flows = fc.list_flows(["runnable_by"])
    for flow in available_flows.data["flows"]:
        print(flow)
