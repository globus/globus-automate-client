.. _quick_start:

Quick Start
===========

Installation
------------

The Globus Automate CLI and SDK contains both a command-line tool
``globus-automate`` and a client library for interacting with actions and flows.
It requires `Python <https://www.python.org/>`_ 3.6+. If a supported version of
Python is not already installed on your system, see this `Python installation guide
<https://docs.python-guide.org/starting/installation/>`_.

For new users and users who want to primarily use the CLI interface into
*Globus Flows*, we highly recommend installing the package using pipx_:

.. code-block:: bash

    pipx install globus-automate-client

For users interested in programmatic access to *Globus Flows*, the SDK
interface will be required. Simply install the ``globus-automate-client``
library using your choice of package manager. For example, if using the `pip
package manager <https://pypi.python.org/pypi/pip>`_:

.. code-block:: bash

    pip install globus-automate-client

Basic Usage
-----------

Once installed, run the CLI with the help flag to receive a summary of its
functionality:

.. code-block:: bash

    globus-automate --help


Or, if programmatic access to the *Flows* service is required, simply import the
SDK in a Python script:

.. code-block:: python

    import globus_automate_client
    help(globus_automate_client)

.. note::
    Most operations available on the CLI are also available in the SDK. For
    users getting familiar with the *Flows* service, we recommend starting off
    with the CLI interface.


Authentication
--------------

All CLI and SDK operations invoking Globus automation services require
authentication.

When using the SDK, all operations require that authentication be provided in
the form of `Globus Authorizers
<https://globus-sdk-python.readthedocs.io/en/stable/authorization.html>`_.


Upon first interaction with any Globus automation service via the CLI, a
text prompt will appear directing the user to a web URL where they can proceed
through an authentication process using Globus Auth to consent to the service
they are using the CLI to interact with. This typically only needs to be done
the first time a particular service is invoked. Subsequently, the cached
authentication information will be used. Authentication information is
cached in the file ``~/.globus_automate_tokens.json``. It is recommended that
this file be protected. The file is in ``json`` format with section names based
on the ``scope`` and it may be edited to remove particular scopes if done with
care.

If re-authentication or re-consent is needed, the entire authentication cache
may be deleted with the following command:

.. code-block:: bash

    globus-automate session logout

Or, to invalidate the authentication cache's contents first and then remove it:

.. code-block:: bash

    globus-automate session revoke

.. note::
    These commands will remove locally cached authentication data for all Globus
    Automate services.

.. _pipx: https://pipxproject.github.io/pipx/installation/
