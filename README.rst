Globus Automate Client
======================

This SDK provides a CLI and a convenient Pythonic interface to the Globus
Automate suite of services.

Basic Usage
-----------

Install with these commands:

..  code-block:: shell

    python -m pip install --upgrade pip setuptools wheel
    python -m pip install globus-automate-client


You can then import Globus Automate client classes and other helpers from
``globus_automate_client``. For example:

.. code-block:: python

    from globus_automate_client import create_action_client

    ac = create_action_client("https://actions.globus.org/hello_world")

    # Launch an Action and check its results
    resp = ac.run({"echo_string": "Hello from SDK"})
    assert resp.data["status"] == "SUCCEEDED"
    print(resp.data)

You can also use the CLI interface to interact with Automate services. For
example:

.. code-block:: BASH

    globus-automate action introspect --action-url https://actions.globus.org/hello_world

Testing, Development, and Contributing
--------------------------------------

Go to the
`CONTRIBUTING <https://github.com/globus/globus-automate-client/blob/main/CONTRIBUTING.adoc>`_
guide for detail.

Links
-----
| Full Documentation: https://globus-automate-client.readthedocs.io
| Source Code: https://github.com/globus/globus-automate-client
| Release History + Changelog: https://github.com/globus/globus-automate-client/releases
