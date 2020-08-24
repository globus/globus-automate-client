Using the CLI and Flows
=======================

The main way to interact with the Globus Automate system is via the command line tool, ``globus-automate``. In the :ref:`quick_start` section, installation and initial use of the CLI tool were introduced. Here, we provide further examples of using the tool for working with Actions and Flows which use the sub-commands ``globus-automate action`` and ``globus-automate flow`` respectively. In each case, and for all commands, invoking the command name followed by the option ``--help`` will provide additional information in the CLI. In many of the examples below, we do not include all possible options to help users become familiar with the common usage patterns. We encourage you to use the help command to learn more about the capability of the tool and the Automate platform itself.

Tips on using the CLI tool
--------------------------

1. The ``globus-automate`` command supports command line completion on a variety of shells. We recommend installing command line completion as many of the commands require a number of options many of which are similar. For the bash shell, command line completion can be setup by adding the following to your ``.bashrc``:

   .. code-block:: BASH

       command -v globus-automate >/dev/null 2>&1 && eval "$(globus-automate --show-completion)"

   For users of zsh, make sure the zsh completion system is correctly initialized
   by calling ``compinit`` near the end of your ``.zshrc`` file. After running the
   following command, restart your shell and globus-automate will complete commands
   and options for you:

   .. code-block:: ZSH

       globus-automate --install-completion

2. Many of the commands involve specifying JSON formatted information. Anywhere an option makes use of JSON, it can be specified in one of two ways:

   1.  Directly on the command line, typically by using single quote characters surrounding the content to protect it from interpretation by the shell as in ``--example-option '{"property": "Value"}'`` where ``--example-option`` is the option on the tool requiring a JSON formatted parameter.

   2.  By placing the JSON information in a file and naming the file as in ``--example-option input_file.json``.

   In most cases, use of a file is easier and more flexible. The tool will automatically detect whether the content is formatted JSON or if it specifies the name of a file.

3. In almost all cases, the output from each command will be in JSON format. The tool will format the output to try to improve readability. However, you may wish to filter the output using pipes and further command line tools such as ``grep`` or ``jq``. When errors occur, a Python traceback is printed, with the content of the Automate API error in the exception message.

Working with Actions
--------------------

As Actions are the most basic unit of work, the CLI provides a means of accessing each of the Actions operations, however in many cases, the fine grain nature of the Actions means they are not often used directly. All of the operations on Actions start with a "base URL", specified using the ``--action-url <base_url>`` option to the action commands. Typically, the base URL will be provided by the operator of the Action to inform users how to interact with the Action. Where ever an ``--action-url`` option is present, an ``--action-scope <scope string>`` may also be used. The *scope string* is the Globus Auth scope registered for interacting with this Action. The scope is published as part of the Action's description (see introspection below), and the ``globus-automate`` tool will automatically retrieve this value when it is not specified by the user. In some cases, even retrieving this descriptive information may require authentication, and in these cases, retrieving the description is not possible without providing the ``--action-scope`` option.

All of the Actions operated by the Globus team, are described in the section :ref:`globus_action_providers` including their base URL and tips on using the CLI for interactions with these Actions directly. As these Actions are publicly viewable, there is no need to provide an ``action-scope`` when working with them from the CLI. As an example, we will work through the operations on the simple *Hello World* Action which has the base URL ``https://actions.globus.org/hello_world``.

Introspection
^^^^^^^^^^^^^

The first step is to learn more about an Action using the introspect operation to get a description:

.. code-block:: BASH

    globus-automate action introspect --action-url https://actions.globus.org/hello_world

The output is a description of the Action. We provide a subset of the complete result below:

.. code-block:: JSON

   {
    "admin_contact": "support@globus.org",
    "title": "Hello World",
    "subtitle": "An Action responding Hello to an input value",
    "visible_to": [
        "public"
    ],
    "runnable_by": [
        "all_authenticated_users"
    ],
    "input_schema": {
        "additionalProperties": false,
        "properties": {
            "echo_string": {
                "type": "string"
            },
            "sleep_time": {
                "type": "integer"
            }
        },
        "type": "object"
    }
    }

The first three elements ``admin_contact``, ``title`` and ``subtitle`` provide descriptive and contact information related to the Action. The next two properties, ``visible_to`` and ``runnable_by``, define the identities which are allowed to see this introspection output, and then execute the action respectively. In this example, as in all the Globus operated Actions, the special values ``public`` and ``all_authenticated_users`` as described in :ref:`auth` are used allowing all users to see and make use of the Action.

The most important information for our next step is the ``input_schema`` element as it provides a description of the input we need to form for running the Action. The ``input_schema`` element is in `JSON Schema <https://https://json-schema.org/>`_ format. This schema defines two properties: ``echo_string`` and ``sleep_time`` which we will use in the next section to form the input for running the Action.

Running
^^^^^^^

The first step to prepare for running the Action is to create a file containing the input we want to provide when we run the Action. We'll call the file ``hello_input.json`` and will contain the following:

.. code-block:: JSON

  {
    "echo_string": "<Your Name Here>",
    "sleep_time": 60
  }

This input conforms to the ``input_schema`` from the introspect call, and specifies that we will have the Action echo our name back to us and that it will "sleep" for 60 seconds until the Action is complete. We'll use this sleep time to demonstrate monitoring the state of an Action below.

We can run the action using the following command:

.. code-block:: BASH

    globus-automate action run --action-url https://actions.globus.org/hello_world --body hello_input.json

If the command is formatted properly, the resulting output will look like the following:

.. code-block:: JSON

  {
    "action_id": "<An id>",
    "status": "ACTIVE"
    "creator_id": "<your globus id>",
    "details": {
        "Hello": "World",
        "hello": "<Your Name Here>"
    },
    "release_after": 2592000,
    "start_time": "<current_time>"
  }

The output from this command is referred to as an "Action Status" document, and as you will see, this format is the result of all operations for working with Actions.
The ``action_id`` is an identifier associated with this execution of the Action and will be used later.

The ``status`` value of ``ACTIVE`` indicates that the Action is still considered to be executing. The possible values for ``status`` are:

*  ``ACTIVE``: The Action is still running and making progress towards completion.

*  ``INACTIVE``: The Action has not yet completed, but it is not making progress. Commonly, some intervention is necessary to help it continue to make progress. The ``details`` may provide additional information on what is necessary for it to continue.

*  ``SUCCEEDED``: The Action is complete, and the completion was considered to be normal or desirable.

*  ``FAILED``: The Action has stopped running due to some error condition. It cannot make progress towards a successful completion.

Because we specified a ``sleep_time`` value of 60 in our example input, the Action will remain in this state for 60 seconds. The ``details`` portion will be specific to every Action and is the output or result of running the Action. This Action always includes the value ``"Hello": "World"`` and the property ``hello`` with the value passed in the ``echo_string``.  The ``release_after`` value provides the number of seconds, after the Action has completed, that the result from the Action will automatically be removed. Until that amount of time has elapsed after the Action completes, we can continue to retrieve the result of the Action as we show in the next section.

Retrieving Status
^^^^^^^^^^^^^^^^^

Once an Action has been run, we can monitor or retrieve its status as follows:

.. code-block:: BASH

    globus-automate action status --action-url https://actions.globus.org/hello_world <action_id>

where the ``action_id`` is the value returned from the ``action run`` command from above. The output will be an Action status, similar to the output from the ``action run``. If at least 60 seconds have passed since the Action was started in our example, the ``status`` field will have the value ``SUCCEEDED``. When it is done, a ``completion_time`` field will be present indicating when the Action reached its final state. The request for status may be repeated as often as you wish until the Action's status has been "released" as described below.


Canceling and Releasing
^^^^^^^^^^^^^^^^^^^^^^^

An Action which is running, but which is no longer needed may be canceled using a command of the form:

.. code-block:: BASH

    globus-automate action cancel --action-url https://actions.globus.org/hello_world <action_id>

The cancel operation is considered to be an advisory request from the user. Actions may not be cancelled immediately, or they may not be canceled at all. A request to cancel an Action which has reached a final state of either ``SUCCEEDED`` or ``FAILED`` will result in an error return.

To free the state of an Action, the release command is used in what is now a predictable form:

.. code-block:: BASH

    globus-automate action release --action-url https://actions.globus.org/hello_world <action_id>

Release may only be performed on Actions which have reached a final state. If the Action is either in the ``ACTIVE`` or ``INACTIVE`` state, the release request will fail. After the release is requested, all subsequent operations involving the same value for the ``action_id`` will fail due to an unknown value for ``action_id``. Eventually, all Actions will be removed even if the release request is not made. The time at which this will happen is equal to the ``completion_time`` plus the ``release_after`` values in the Action status return values.

Working with Flows
------------------

As described in the section on :ref:`flows_concept`, a Flow is a combination of Actions and other operations forming a more complex operation. Once deployed, a Flow behaves very much like an Action, having the run, status, cancel and release operations defined. Each of these operations is reflected in the ``globus-automate`` tool. The tool also supports listing available Flows.

.. note::
   This section does not provide details on creating new Flows. This is covered in greater detail in the section on :ref:`flows_authoring`.

Finding and displaying Flows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following command will list the flows available for your use:

.. code-block:: BASH

    globus-automate flow list

This outputs a list of flows, where the description of each flow carries the same fields as the output from ``globus-automate action introspect`` described above. This emphasizes again the similarity between Flows and Actions. The ``title`` and ``description`` fields may be helpful in determining what a Flow does and what its purpose is. Like Actions, the ``input_schema`` may define what is required of the input when running the flow. However, not all Flows are required to define an ``input_status`` as a convenience to Flow authors who may not be familiar with creating JSON Schema specifications. Importantly, each entry in the list of Flows will also contain a value for ``id`` which we refer to as the "Flow id" and denote as ``flow_id`` below. This value will be used for further interacting with a particular Flow. For example, to display information about a single Flow you may use:

.. code-block:: BASH

    globus-automate flow display <flow_id>

When focusing on one Flow, it is also useful to notice the field ``definition``. This is the actual encoding of the Flow as it was created and deployed by the Flow's author. Looking at this value may give further information about how the Flow works. This can be useful both to determine if a Flow performs the function you desire, but also as a method to see how other Flows have been defined if you are interested in creating new Flows.

Executing and Monitoring Flows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Execution and monitoring of Flows follows the same pattern as Actions: the run/status/cancel/release pattern is the same. We provide the following flows-specific commands to perform these tasks:

.. code-block:: BASH

    globus-automate flow run --flow-input input.json <flow_id>

This acts like ``globus-automate action run`` with the flow id rather than the ``action_url`` specifying the "name" of the entity to be run. The output, like for Actions, will be an Action status document including an ``action_id`` which is used in the following commands:

.. code-block:: BASH

    globus-automate flow action-status --flow-id <flow_id> <action_id>

.. code-block:: BASH

    globus-automate flow action-cancel --flow-id <flow_id> <action_id>

.. code-block:: BASH

    globus-automate flow action-release --flow-id <flow_id> <action_id>

For each of these, the ``details`` provides information about the most recent, potentially final, state executed by the Flow. However, as the Flow may execute many states, it is useful to be able to see what states have been executed and what their input and output have been. This can be seen via the "log" of the Flow execution as follows:

.. code-block:: BASH

    globus-automate flow action-log --flow-id <flow_id> <action_id>

The log may have a large number of entries. You can request more entries be returned using the option ``-limit N`` where ``N`` is the number of log entries to return. The default value is 10.

Creating and managing Flows
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Many users will only ever use Flows created by others, so they may not necessarily need to understand how to create Flows including the commands listed in this section. For those that are creating new Flows, the first step is to deploy a Flow as follows:

.. code-block:: BASH

    globus-automate flow deploy --title <title> --definition <Flow definition JSON> --input-schema <Input schema JSON> --visible-to <urn of user or group which can see this Flow> --runnable-by <urn of user or group which can run this Flow> --administered-by <urn of user or group who can maintain this flow>

The output will be the Flow description as displayed by the ``flow display`` command above. These command line options provide the values for the similarly named fields in the Flow description. Of these, only ``title`` and ``definition`` are required. To aid users in using your Flow, we highly recommend the use of ``input-schema`` as it provides them both a form of documentation and assurance at run-time that the input they provide is correct for executing the Flow. By providing a value or values to ``administered-by`` you grant rights to others for updating or eventually removing the Flow you have deployed. Commands for updating and removing flows are as follows.

.. code-block:: BASH

    globus-automate flow update --title <title> --definition <Flow definition JSON> --input-schema <Input schema JSON> --visible-to <urn of user or group which can see this Flow> --runnable-by <urn of user or group which can run this Flow> --administered-by <urn of user or group who can maintain this flow> <flow_id>

This will update any of the fields or description of the Flow, including the Flow definition itself. Note the ``flow_id`` field is present at the end of the command line.

Deleting a Flow is done via:

.. code-block:: BASH

    globus-automate flow delete <flow_id>

Care should be taken when issuing this command. There is no further prompting to insure the flow should really be deleted. After deletion, no record of the Flow definition or its execution history (i.e. the ``flow action-*`` commands) is maintained.

The bulk of the effort in creating flows is in authoring their definition which is covered in the section :ref:`flows_authoring`.
