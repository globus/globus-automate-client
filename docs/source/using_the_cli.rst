Using the CLI
=============

For many, the primary way of interacting with Globus automation services will be
via the CLI.

Configuration
-------------

It is recommended to install ``globus-automate`` command line completion to
support use and discovery of the available commands and options. Currently only
the ``bash``, ``fish``, and ``zsh`` shells are supported.

.. code-block:: BASH

    globus-automate --install-completion

.. note::

    For users of ``zsh``, make sure the ``zsh`` completion system is correctly
    initialized by running ``compinit`` near the end of your ``.zshrc`` file.

General Usage
-------------

Each command support a ``--verbose`` option which can be used to see the
underlying HTTP request information for what each command is doing. This can be
useful for reusing tokens, debugging purposes, or for getting more familiar with
the Globus Automate services' APIs.

Each command also supports a ``--help`` option which provides concise
information on the command and documents its expected inputs.

In almost all cases, the output from each command will be in JSON format. The
CLI will format the output to try to improve readability, however, you may
wish to filter the output using pipes and other command line tools such as
``grep`` or ``jq``.

Many of the commands involve specifying JSON formatted input. Anywhere a command
makes use of JSON, it can be specified in one of two ways:

- Directly on the commmand line
    Typically by using single quote characters surrounding the content to protect it
    from interpretation by the shell:

    .. code-block:: BASH

        --option '{"property": "Value"}'

    where ``--option`` is the option requiring a JSON formatted parameter.

- In a file
    Place the JSON object in a file and refer to the file instead:

    .. code-block:: BASH

        --option /path/to/your/input_file.json

    where ``--option`` is the option requiring a JSON formatted parameter.

Commands which can run or monitor an action or run support a ``--watch``
flag which can be used to stream updates on an activity's execution state.

Many operations require a principal ID to delegate access. This value represents
a single Globus user identity or a Globus Group. The format for a principal is
the user ID or Group ID, prefixed with ``urn:globus:auth:identity:`` if it is a
user, or ``urn:globus:groups:id:`` if it is a Group.

Using the CLI with Actions
--------------------------

In Globus automation services, *actions* represent a single unit of work. Actions
are created by invoking *action providers*. The CLI provides a means of interacting
with action providers to create and manage actions, however in many cases, the
fine grain nature of the actions means they are not often interacted with
directly.

To interact with an action, you must know the URL for the action provider
that created (or will create) it. This URL is specified using the
``--action-url`` option to the ``action`` subcommands.

Wherever an ``--action-url`` option is present, the ``--action-scope`` option
may also be provided. The *scope string* is the Globus Auth scope registered for
interacting with this action provider. This *scope string* is published as part
of the action provider's description (see
:ref:`Introspection`) and the CLI will automatically retrieve
this value when it is not specified by the user. In some cases, even retrieving
the *scope string* may require authentication, and in these cases, introspecting
the action provider is not possible  without providing the
``--action-scope`` option.

All of the action providers operated by the Globus team are described in the
`hosted action providers`_ documentation, which includes their URL and
tips on using the CLI for interactions with these action providers directly.
As these action providers are publicly viewable, there is no need to provide
the  ``--action-scope`` option when working with them from the CLI -- the CLI
will look up the *scope string* automatically.

As an example, we will work through the operations on the ``Hello World Action
Provider`` at the URL ``https://actions.globus.org/hello_world``.


..  _Introspection:

Introspection
^^^^^^^^^^^^^

The first step to learning more about an action provider is using the
introspect operation to get a description of the action provider:

.. code-block:: BASH

    globus-automate action introspect --action-url https://actions.globus.org/hello_world

.. raw:: html

    <details>
    <summary>Command Output</summary>

.. code-block:: JSON

    {
        "admin_contact": "support@globus.org",
        "administered_by": [],
        "api_version": "1.0",
        "description": null,
        "event_types": null,
        "globus_auth_scope": "https://auth.globus.org/scopes/actions.globus.org/hello_world",
        "input_schema": {
            "additionalProperties": false,
            "properties": {
            "echo_string": {
                "type": "string"
            },
            "required_dependent_scope": {
                "type": "string"
            },
            "sleep_time": {
                "type": "integer"
            }
            },
            "type": "object"
        },
        "keywords": null,
        "log_supported": false,
        "maximum_deadline": "P30D",
        "runnable_by": [
            "all_authenticated_users"
        ],
        "subtitle": "An action responding Hello to an input value",
        "synchronous": false,
        "title": "Hello World",
        "types": [
            "ACTION"
        ],
        "visible_to": [
            "public"
        ]
    }

.. raw:: html

    </details>

From this introspection response we can see that the *scope string* for
this action provider is the value of the ``globus_auth_scope`` field,
``https://auth.globus.org/scopes/actions.globus.org/hello_world``. We
can also see that the ``admin_contact`` is Globus.

For information on what this action provider does, it is useful to examine
the ``title``, ``subtitle``, and ``description`` fields. We can also see that
the action provider is ``visible_to`` *public*, meaning that anyone can make
unauthenticated requests to the introspection endpoint. Similarly, it is
``runnable_by`` *all_authenticated_users*, meaning that any user with valid
Globus Auth credentials may use this action provider to create actions.

The most important information for our next step is the ``input_schema`` element
as it provides a description of the input we need to form for running an action
on this action provider. The ``input_schema`` element is in `JSON Schema
<https://json-schema.org/>`_ format. This schema defines three properties:
``echo_string``, ``sleep_time``, and ``required_dependent_scope``. We will use
this information in the next section on running an action.

Running
^^^^^^^

The first step to prepare for running an action is to create a file containing
the input to the action. We'll call the file ``hello_input.json`` and it
contains the following:

.. code-block:: JSON

  {
    "echo_string": "Welcome to Globus Automate!",
    "sleep_time": 60
  }

This input conforms to the ``input_schema`` from the :ref:`Introspection` call,
and  specifies that we will have the action echo a message back to us and that it
will "sleep" for 60 seconds until the action is complete. We'll use this sleep
time to demonstrate monitoring the state of an action below.

With our input in place, run the action using the following command:

.. code-block:: BASH

    globus-automate action run --action-url https://actions.globus.org/hello_world --body hello_input.json

.. note::

    If this is your first time running the ``Hello World Action Provider`` you
    will see text and a prompt appear on your terminal window. Follow the
    instructions to authenticate to Globus Auth to run this action. This will
    only appear on the first time you interact with an action provider.


The resulting output will look like:

.. code-block:: JSON

    {
        "action_id": "CBOXB3fUdKrO",
        "completion_time": null,
        "creator_id": "urn:globus:auth:identity:06a24bef-940e-418a-97bc-48229c64cc99",
        "details": {
            "Hello": "World",
            "hello": "Welcome to Globus Automate!"
        },
        "display_status": "ACTIVE",
        "label": null,
        "manage_by": [
            "urn:globus:auth:identity:6f8c1345-33c6-4235-86c6-90fbadbf4d35",
            "urn:globus:auth:identity:06a24bef-940e-418a-97bc-48229c64cc99"
        ],
        "monitor_by": [
            "urn:globus:auth:identity:6f8c1345-33c6-4235-86c6-90fbadbf4d35",
            "urn:globus:auth:identity:06a24bef-940e-418a-97bc-48229c64cc99"
        ],
        "release_after": null,
        "start_time": "2021-04-29 23:21:47.763653+00:00",
        "status": "ACTIVE"
    }


This output is referred to as an ``Action Status`` document and all output from
working with actions will follow this format.

The ``action_id`` is an identifier associated with this action provider
invocation and is used to track this action's lifecycle.

The ``status`` value of ``ACTIVE`` indicates that the action is in the process
of executing. The possible values for ``status`` are:

- ``ACTIVE``
    The action is running and making progress towards completion.
- ``INACTIVE``
    The action has not yet completed and it is not making
    progress.  Commonly, some intervention is necessary to help it continue to
    make progress.
- ``SUCCEEDED``
    The action is complete and the completion was considered to be normal.
- ``FAILED``
    The action has stopped running due to some error condition. It cannot make
    progress towards a successful completion.

Each action can be provided a ``label`` to help identity the purpose for which
it was run.

The ``details`` field format is specific to every action provider and is the
output or result of running the action. It will often contain information about
why an action has reached the state it is in.

The ``release_after`` field is an ISO8601 format time duration value that
indicates how long after completion the action provider will retain a record
of the action's execution. Until then, the record will persist and can be looked
up.

``monitor_by`` represents delegated read-only access to the action's execution
state, meaning that principals in an action's ``monitor_by`` field will be able
to retrieve the action's execution state (see :ref:`Retrieving Status`).
Principals may be either a Globus Auth user or a Globus Auth group. The format
for a Globus Auth user is ``urn:globus:auth:identity:<UUID>`` and for a Globus
Auth group is ``urn:globus:groups:id:<UUID>``.

``manage_by`` represents delegated write access to the action's execution state,
meaning that principals in an action's ``manage_by`` field will have the ability
to change the alter the state it is in (see :ref:`Canceling and Releasing`).
Principals may be either a Globus Auth user or a Globus Auth group. The format
for a Globus Auth user is ``urn:globus:auth:identity:<UUID>`` and for a Globus
Auth group is ``urn:globus:groups:id:<UUID>``.

Since the action has already been run, we cannot change any of these fields. If
we wanted to run another action with updated values for any of the fields, we
would pass those as command line options. For information on how to use the
options, run the command with ``--help``:

.. code-block:: BASH

    globus-automate action run --help

.. admonition:: Tip
    :class: tip

    You can specify each of the ``--monitor-by`` and ``--manage-by`` flags
    multiple times to provide multiple principals with read or write access on
    the action.


..  _Retrieving Status:

Retrieving Status
^^^^^^^^^^^^^^^^^

Once an action has been run, the user who initiated the action or anyone in
the action's ``monitor_by`` field can monitor or retrieve its status as follows:

.. code-block:: BASH

    globus-automate action status --action-url https://actions.globus.org/hello_world <action_id>

where the ``action_id`` is the value returned from the ``action run`` command
from above. The output will be an Action Status document. When the action is
completed, the ``completion_time`` field will be present indicating when the
action reached its final state. You can continue requesting the action's status
as long as the action exists on the action provider.

In out example, we asked the action to "sleep" for 60 seconds. Therefore, the
action will remain in an ``ACTIVE`` state until 60 seconds have passed, at which
point the status should be ``SUCCEEDED``.


..  _Canceling and Releasing:

Canceling and Releasing
^^^^^^^^^^^^^^^^^^^^^^^

An action which is running, but which is no longer needed, may be canceled (or
released) by the user who initiated the action execution or anyone in the
action's ``manage_by`` field using a command of the form:

.. code-block:: BASH

    globus-automate action cancel --action-url https://actions.globus.org/hello_world <action_id>

The cancel operation is considered to be an advisory request from the user.
actions may not be cancelled immediately, or they may not be canceled at all. A
request to cancel an action which has reached a final state of either
``SUCCEEDED`` or ``FAILED`` will result in an error return.

To remove an action's state from the action provider, the user who initiated
the action execution or anyone in the action's ``manage_by`` field can use the
release subcommand:

.. code-block:: BASH

    globus-automate action release --action-url https://actions.globus.org/hello_world <action_id>

Release may only be performed on actions which have reached a final state. If
the action is in either the ``ACTIVE`` or ``INACTIVE`` state, the release will
fail.

Once released, the action state is forever removed from the action provider
and all attempts to access it will fail. Action providers use the
``maximum_deadline`` field to advertise how long they will keep a record of an
action after it reaches a completed state. The time at which this will happen is
equal to the ``completion_time`` plus the ``release_after`` values in the Action
Status document.

Using the CLI with Flows
------------------------

As described in the `Flows overview`_, a *flow* combines actions and
other operations into a more complex operation. When a flow is invoked, it
creates a *run* and the run's interface is very much like an action's; it
has ``run``, ``status``, ``cancel`` and ``release`` operations defined. Because
of this similarity, we sometimes refer to runs as actions in the
documentation, CLI and SDK.

The CLI contains commands for creating, defining, and managing flow definitions
and commands for running, monitoring, and managing flow runs (also known as
*actions*).

.. note::
   This section does not provide details on writing flows. That is covered
   in greater detail in the `Authoring Flows`_ documentation.

Finding and Displaying Flows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When a flow is deployed to Automate, the creator can specify which identities
the flow should be visible to and which identities the flow should be runnable
by. As the names suggest, users in a flow's ``visible_to`` field will be able to
query the service to view a flow's definition and metadata. Users in a flow's
``runnable_by`` field will be able to run an instance of the flow.

The following command will list the flows you have created:

.. code-block:: BASH

    globus-automate flow list

To view flows which are visible or runnable by you as well, run the following
command:

.. code-block:: BASH

    globus-automate flow list --role created_by --role visible_to --role runnable_by

This outputs a list of flows, where the description of each flow carries the
same fields as the output from ``globus-automate action introspect`` described
above. This emphasizes again the similarity between flows and actions. The
``title`` and ``description`` fields may be helpful in determining what a flow
does and what its purpose is. Like actions, the ``input_schema`` may define what
is required of the input when running the flow. However, not all flows are
required to define an ``input_schema`` as a convenience to flow authors who may
not be familiar with creating JSON Schema specifications. Importantly, each
entry in the list of flows will also contain a value for ``id`` which we refer
to as the "flow id" and denote as ``flow_id`` below. This value will be used for
further interacting with a particular flow.

To display information about a single flow you may use:

.. code-block:: BASH

    globus-automate flow display <flow_id>

Or, to visualize the flow:

.. code-block:: BASH

    globus-automate flow display <flow_id> --format image

When focusing on one flow, it is also useful to notice the field ``definition``.
This is the actual encoding of the flow as it was created and deployed by the
flow's author. Looking at this value may give further information about how the
flow works. This can be useful both to determine if a flow performs the function
you desire, but also as a method to see how other flows have been defined if you
are interested in creating new flows.

Executing and Monitoring Flows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Execution and monitoring of flows follows the same pattern as actions: the
run/status/cancel/release pattern is the same.

When initiating a flow run, you can delegate access to the flow instance to
other Globus Auth identities. By providing the ``monitor-by`` option, you can
delegate read-only access to other users or groups, allowing them to retrieve
it execution state. By providing the ``manage-by`` option, you delegate write
access to other users or groups, allowing them to alter its execution state. In
the example below, we show how to run an instance of a flow and delegate monitor
access to a Globus Group:

.. code-block:: BASH

    globus-automate flow run <flow_id> --flow-input input.json \
        --monitor-by urn:globus:groups:id:00000000-0000-0000-0000-000000000000

.. note::

    If no ``manage_by`` or ``monitor_by`` values are specified, only the
    identity instantiating the flow run is allowed to monitor or manage a flow's
    running state.

This acts like ``globus-automate action run`` with the flow id rather than the
``action_url`` specifying the "name" of the action to be run. The output, like
for actions, will be an action status document including an ``action_id`` which
is used in the following commands:

.. code-block:: BASH

    globus-automate flow action-status --flow-id <flow_id> <action_id>

.. code-block:: BASH

    globus-automate flow action-cancel --flow-id <flow_id> <action_id>

.. code-block:: BASH

    globus-automate flow action-release --flow-id <flow_id> <action_id>

For each of these, the ``details`` provides information about the most recent,
potentially final, state executed by the flow. However, as the flow may execute
many states, it is useful to be able to see what states have been executed and
what their input and output have been. This can be seen via the "log" of the
flow execution as follows:

.. code-block:: BASH

    globus-automate flow action-log --flow-id <flow_id> <action_id>

The log may have a large number of entries. You can request more entries be
returned using the option ``-limit N`` where ``N`` is the number of log entries
to return. The default value is 10.

Creating and managing Flows
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Many users will only ever use flows created by others, so they may not
necessarily need to understand how to create flows including the commands
listed in this section. For those that have created a flow, the first step is
to deploy a flow as follows:

.. code-block:: BASH

    globus-automate flow deploy --title <title> \
        --definition <flow definition JSON> --input-schema <Input schema JSON> \
        --visible-to <urn of user or group which can see this flow> \
        --runnable-by <urn of user or group which can run this flow> \
        --administered-by <urn of user or group who can maintain this flow>

When deployed this way, only the identity that deployed the flow will be able to
view the flow and only they will be able to run an instance of the flow. When
deploying, it's possible to specify who should be able to see and run the flow.
Using the ``visible_to`` flag, you can indicate which Globus identities can view
the deployed flow, or set it to ``public``, which creates a flow viewable by
anyone. Using the ``runnable_by`` flag, you can indicate which Globus identities
can run an instance of the deployed flow, or set a value of
``all_authenticated_users`` which allows any authenticated user to run an
instance of the flow.

Below, we demonstrate how to deploy a flow that is ``visible_to`` a single
Globus group and ``runnable_by`` any authenticated user:

.. code-block:: BASH

    globus-automate flow deploy --title <title> \
        --definition <flow definition JSON> \
        --input-schema <Input schema JSON> \
        --visible-to urn:globus:groups:id:00000000-0000-0000-0000-000000000000 \
        --runnable-by all_authenticated_users

Once deployed, the output will be the flow description as displayed by the
``flow display`` command above. These command line options provide the values
for the similarly named fields in the flow description. Of these, only ``title``
and ``definition`` are required. To aid users in using your flow, we highly
recommend the use of ``input-schema`` as it provides them both a form of
documentation and assurance at run-time that the input they provide is correct
for executing the flow. By providing a value or values to ``administered-by``
you grant rights to others for updating or eventually removing the flow you have
deployed. Commands for updating and removing flows are as follows.

.. code-block:: BASH

    globus-automate flow update --title <title> \
        --definition <flow definition JSON>  --input-schema <Input schema JSON> \
        --visible-to <urn of user or group which can see this flow> \
        --runnable-by <urn of user or group which can run this flow> \
        --administered-by <urn of user or group who can maintain this flow> \
        <flow_id>

This will update any of the fields or description of the flow, including the
flow definition itself. Note the ``flow_id`` field is present at the end of the
command line.

Deleting a flow is done via:

.. code-block:: BASH

    globus-automate flow delete <flow_id>

Care should be taken when issuing this command. There is no further prompting to
ensure the flow should really be deleted. After deletion, no record of the flow
definition or its execution history (i.e. the ``flow action-*`` commands) is
maintained.

The bulk of the effort in creating flows is in authoring their definition which
is covered in the `Authoring Flows`_ documentation.

..  _Flows overview: https://docs.globus.org/api/flows/overview/#flows
..  _Authoring Flows: https://docs.globus.org/api/flows/authoring-flows/
..  _hosted action providers: https://docs.globus.org/api/flows/hosted-action-providers/
