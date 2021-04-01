.. _quick_start:

Quick Start
===========

Installation
^^^^^^^^^^^^

The Globus Automate CLI and SDK contains both a command-line tool
``globus-automate`` and a client library for interacting with Actions and Flows.
It requires `Python <https://www.python.org/>`_ 3.6+. If a supported version of
Python is not already installed on your system, see this `Python installation guide
<http://docs.python-guide.org/en/latest/starting/installation/>`_.

The simplest way to install the Globus Automate CLI and SDK and its dependencies
is by using the ``pip`` package manager (https://pypi.python.org/pypi/pip),
which is included in most Python installations:

.. code-block:: bash

    pip install globus-automate-client

Basic Usage
^^^^^^^^^^^

Once installed, run the CLI with the help flag to receive a summary of its
functionality:

.. code-block:: bash

    globus-automate --help


Or, if programmatic access to the Flows service is required, simply import the
SDK in a Python script:

.. code-block:: python

    import globus_automate_client
    help(globus_automate_client)

.. note::
    Most operations available on the CLI interface are also available in the
    SDK. We recommend for users getting familiar with the Automate service to start
    off with the CLI interface.

Use of the CLI and SDK to invoke any services requires authentication. Upon
first interaction with any Action Provider or the Flows Service via the CLI, a
text prompt will appear directing the user to a web URL where that can proceed
through an authentication process using Globus Auth to consent to the service
they are using the CLI to interact with. This typically only needs to be done
once, the first time a particular service is invoked. Subsequently, the cached
authentication information will be used. Authentication information is
cached in the file ``~/.globus_automate_tokens.json``.

It is recommended that this file be protected. If re-authentication or
re-consent is needed, the file may be deleted. This will remove
consents to **all** Action Providers and the Flows service. The file
is in ``json`` format with section names based on the ``scope``. It may be
edited to remove particular scopes if done with care.
