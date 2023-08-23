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

.. _cli_command_table:

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


Converting YAML to JSON
-----------------------

In the Globus Automate Client, users were allowed to use YAML files to define
their flows.
However, the Flows service only accepts JSON data, and YAML was being converted
to JSON by the client.

Unfortunately, the YAML language specification contains ambiguities, and
different parsers may treat identical documents differently.
``globus-cli`` and ``globus-sdk`` do not support YAML parsing, but it is possible
to convert YAML to JSON using a variety of tools.
This approach ensures that Globus provided software operates consistently, and
allows users to continue using YAML or to move off of it, as they prefer.

In this section, we will cover two popular tools for converting YAML to JSON,
yq (written in Go) and remarshal (written in Python). We will also cover
one python library, ``pyyaml``, which can be used to load YAML data and pass it
to the ``globus-sdk``.
Various other tools provide similar functionality in other languages, and there
are alternative parsers available in python.

yq
~~

The `yq <https://mikefarah.gitbook.io/yq/>`_ tool is a CLI utility similar to the
popular ``jq`` command.
It provides a wide variety of commands for manipulating and extracting data
from YAML documents.

Installation
++++++++++++

``yq`` is distributed for multiple platforms as a binary as well as Homebrew
and Snapcraft.
For these latter two, use:

.. code-block:: bash

    # macOS, brew
    brew install yq

    # ubuntu-based linux, snap
    snap install yq

To get a ``yq`` binary directly, or to use the docker based distribution,
follow
`yq's installation instructions <https://github.com/mikefarah/yq/#install>`_.

Usage
+++++

In order to convert a flow from YAML to JSON using ``yq``, all that is needed
is a command which loads the YAML document and then outputs it as JSON.

.. code-block:: bash

    yq -o=json foo.yaml > foo.json

remarshal
~~~~~~~~~

The `remarshal <https://github.com/remarshal-project/remarshal>`_ project
provides a wide range of commands for converting data between different
formats, including YAML and JSON.

These commands exist for the sole purpose of converting data between formats,
and are therefore a perfect fit for our use-case.

Installation
++++++++++++

As ``remarshal`` is a python CLI, installation should be performed with
``pipx``, as with the ``globus-cli``.

First `follow the pipx installation documentation
<https://pypa.github.io/pipx/installation/>`_ to ensure you have ``pipx``
installed.

Next, run the install command:

.. code-block:: bash

    pipx install remarshal

Usage
+++++

Of the many commands provided by ``remarshal``, the one we want is simply
``yaml2json``. After installing, all that is needed is to run:

.. code-block:: bash

    yaml2json foo.yaml foo.json

pyyaml
~~~~~~

Unlike the previous two tools, ``pyyaml`` is a python library, not a CLI.

If you have a YAML flow definition and want to use it with the ``globus-sdk``,
you must parse it from YAML yourself and proivde it as a dictionary.

Installation
++++++++++++

``pyyaml`` can be installed with ``pip install pyyaml``.

Usage
+++++

``pyyaml`` provides the ``yaml`` package.
To parse a YAML file, ``foo.yaml``, into a python data structure, import it and
use the ``load`` function::

    import yaml

    with open("foo.yaml") as fp:
        data = yaml.load(fp)

    # a check may be a wise precaution, as YAML documents can contain lists or
    # other non-dict data
    if not isinstance(data, dict):
        raise ValueError(
            f"YAML document 'foo.yaml' contained unexpected type {type(data)}"
        )

    print(data)


Updating Command Line Usages
----------------------------

The :ref:`table above <cli_command_table>` shows the mapping between the old
``globus-automate`` CLI commands and the new ``globus-cli`` commands.

This section provides more detailed guidance for converting commands between
the two, for commands and usages where the mapping is non-obvious.

Required Options vs Positional Arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general, the ``globus-cli`` uses positional arguments for all required
data, whereas the ``globus-automate`` CLI used required options in some cases.

The conversion is typically straightforward, requiring first that you read the
``globus-cli`` helptext and then order arguments appropriately if necessary.

For example, ``globus-automate flow deploy`` has been replaced with
``globus flows create``. Starting from an original command like so:

.. code-block:: bash

    $ globus-automate flow deploy --description bar --title foo --definition foo.json

The first step is to determine which CLI options are required and in what
order. Run ``globus flows create --help`` to see the help text:

.. code-block:: bash

    $ globus flows create --help
    Usage: globus flows create [OPTIONS] TITLE DEFINITION

      Create a new flow.


    # more text follows
    ...

With this information, we can see that ``TITLE`` is the first positional
argument and ``DEFINITION`` is the second. ``--description`` is still an
option.

The final command is therefore:

.. code-block:: bash

    globus flows create foo foo.json --description bar

Pagination Options
~~~~~~~~~~~~~~~~~~

A number of ``globus-automate`` commands provide options for paging through
data, typically ``--marker`` and ``--per-page``.
In ``globus-cli``, these options are replaced with a single option ``--limit``,
which controls the total number of results returned.

Under ``globus-automate``, users had precise control over pagination, while
under ``globus-cli`` all pagination is implicitly handled for the user.

The two implementations trade off between simplicity for users vs fine-grained
control, and are not fully translatable.
For users, simply note that ``--marker`` and ``-per-page`` are no longer
available as options, but that users relying on these options should now have
their use-cases covered by the implicit pagination of the ``globus-cli``
commands.

``--flow-scope``
~~~~~~~~~~~~~~~~

Under the ``globus-automate`` CLI several commands took a ``--flow-scope``
option to control internal behaviors.

This option is no longer needed, as the ``globus-cli`` will automatically
handle the cases which this option covered.

``run-log --watch``
~~~~~~~~~~~~~~~~~~~

``globus-automate flow run-log --watch`` allowed a user to tail logs from the
service by polling.

``globus flows run show-logs`` does not support this behavior.

``run-resume`` Options
~~~~~~~~~~~~~~~~~~~~~~

``globus-automate flow run-resume`` accepted two options which are not present
in the ``globus-cli``.

One option is ``--watch``, which is identical to the ``run-status --watch``
flag.
See the documentation below on ``run-status --watch`` for details on how to
achieve the same result with ``globus flows run show``.
``globus flows run resume`` does not provide any built-in behavior for polling.

``globus-automate flow run-resume`` also supported an option,
``--query-for-inactive-reason/--no-query-for-inactive-reason``.
This behavior is now built into ``globus flows run resume`` and users do not
need to explicitly specify how to handle inactive runs.

``run-status --watch``
~~~~~~~~~~~~~~~~~~~~~~

The ``globus-automate flow run-status --watch`` flag polled on the run until
it completed.
This same behavior can be achieved by running ``globus flows run show`` in a
loop.

For example, it can be scripted like so:

.. code-block:: bash

    #!/bin/bash

    RUN_ID="$1"
    echo "Poll until '$RUN_ID' terminates"

    NUM_TRIES=10
    until [ "$NUM_TRIES" -eq 0 ]; do
      status="$(globus flows run show "$RUN_ID" --jmespath "status" --format unix)"
      case "$status" in
        SUCCEEDED)
          echo "succeeded"
          exit 0
          ;;
        FAILED)
          echo "failed"
          exit 1
          ;;
        *)
          NUM_TRIES=$((NUM_TRIES - 1))
          sleep 30
          ;;
      esac
    done

    echo "Run '$RUN_ID' did not terminate after 10 tries"
    exit 3

``globus-automate flow run --watch``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This ``--watch`` flag is another instance of the same behavior described above.
Users needing to poll on run status can use ``globus flows run show`` as in the
preceding example.


.. [*] ``scopes`` is an instance attribute of ``SpecificFlowClient``, so usage is
    slightly different from a method, but the information provided is the same.

.. _globus-sdk: https://globus-sdk-python.readthedocs.io/en/stable/

.. _globus-cli: https://docs.globus.org/cli/
