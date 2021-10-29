``globus-automate``
===================

CLI for Globus Automate

By default, this CLI keeps all its config and cached tokens in
.globus_automate_tokens.json in the user’s home directory.

**Usage**:

.. code:: console

   $ globus-automate [OPTIONS] COMMAND [ARGS]...

**Options**:

-  ``-V, --version``: Print CLI version number and exit
-  ``--install-completion``: Install completion for the current shell.
-  ``--show-completion``: Show completion for the current shell, to copy
   it or customize the installation.
-  ``--help``: Show this message and exit.

**Commands**:

-  ``action``: Manage Globus Automate Actions
-  ``flow``: Manage Globus Automate Flows
-  ``queue``: Manage Globus Automate Queues
-  ``session``: Manage your session with the Automate Command Line

``globus-automate action``
--------------------------

**Usage**:

.. code:: console

   $ globus-automate action [OPTIONS] COMMAND [ARGS]...

**Options**:

-  ``--help``: Show this message and exit.

**Commands**:

-  ``cancel``: Terminate a running Action by its ACTION_ID.
-  ``introspect``: Introspect an Action Provider’s schema.
-  ``release``: Remove an Action’s execution history by its…
-  ``resume``: Resume an inactive Action by its ACTION_ID.
-  ``run``: Launch an Action.
-  ``status``: Query an Action’s status by its ACTION_ID.

``globus-automate action cancel``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Terminate a running Action by its ACTION_ID.

**Usage**:

.. code:: console

   $ globus-automate action cancel [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--action-url TEXT``: The url at which the target Action Provider is
   located. [required]
-  ``--action-scope TEXT``: The scope this Action Provider uses to
   authenticate requests.
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``--help``: Show this message and exit.

``globus-automate action introspect``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Introspect an Action Provider’s schema.

**Usage**:

.. code:: console

   $ globus-automate action introspect [OPTIONS]

**Options**:

-  ``--action-url TEXT``: The url at which the target Action Provider is
   located. [required]
-  ``--action-scope TEXT``: The scope this Action Provider uses to
   authenticate requests.
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``--help``: Show this message and exit.

``globus-automate action release``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Remove an Action’s execution history by its ACTION_ID.

**Usage**:

.. code:: console

   $ globus-automate action release [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--action-url TEXT``: The url at which the target Action Provider is
   located. [required]
-  ``--action-scope TEXT``: The scope this Action Provider uses to
   authenticate requests.
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``--help``: Show this message and exit.

``globus-automate action resume``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Resume an inactive Action by its ACTION_ID.

**Usage**:

.. code:: console

   $ globus-automate action resume [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--action-url TEXT``: The url at which the target Action Provider is
   located. [required]
-  ``--action-scope TEXT``: The scope this Action Provider uses to
   authenticate requests.
-  ``--query-for-inactive-reason / --no-query-for-inactive-reason``:
   Should the Action first be queried to determine the reason for the
   resume, and prompt for additional consent if needed. [default: True]
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-w, --watch``: Continuously poll this Action until it reaches a
   completed state. [default: False]
-  ``--help``: Show this message and exit.

``globus-automate action run``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Launch an Action.

**Usage**:

.. code:: console

   $ globus-automate action run [OPTIONS]

**Options**:

-  ``--action-url TEXT``: The url at which the target Action Provider is
   located. [required]
-  ``--action-scope TEXT``: The scope this Action Provider uses to
   authenticate requests.
-  ``-b, --body TEXT``: The body to supply to the Action Provider. Can
   be a filename or raw JSON string. [required]
-  ``--request-id TEXT``: An identifier to associate with this Action
   invocation request
-  ``--manage-by TEXT``: A principal which may change the execution of
   the Action. The principal is the user’s or group’s UUID prefixed with
   either ‘urn:globus:groups:id:’ or ‘urn:globus:auth:identity:’
   [repeatable]
-  ``--monitor-by TEXT``: A principal which may view the state of the
   Action. The principal is the user’s or group’s UUID prefixed with
   either ‘urn:globus:groups:id:’ or ‘urn:globus:auth:identity:’
   [repeatable]
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-l, --label TEXT``: Optional label to mark this execution of the
   action.
-  ``-w, --watch``: Continuously poll this Action until it reaches a
   completed state. [default: False]
-  ``--help``: Show this message and exit.

``globus-automate action status``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Query an Action’s status by its ACTION_ID.

**Usage**:

.. code:: console

   $ globus-automate action status [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--action-url TEXT``: The url at which the target Action Provider is
   located. [required]
-  ``--action-scope TEXT``: The scope this Action Provider uses to
   authenticate requests.
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-w, --watch``: Continuously poll this Action until it reaches a
   completed state. [default: False]
-  ``--help``: Show this message and exit.

``globus-automate flow``
------------------------

Manage Globus Automate Flows

To target a different Flows service endpoint, export the
GLOBUS_AUTOMATE_FLOWS_ENDPOINT environment variable.

**Usage**:

.. code:: console

   $ globus-automate flow [OPTIONS] COMMAND [ARGS]...

**Options**:

-  ``--help``: Show this message and exit.

**Commands**:

-  ``action-cancel``: Cancel an active execution for a particular…
-  ``action-enumerate``: Retrieve all Flow Runs you have access to…
-  ``action-list``: List a Flow definition’s discrete…
-  ``action-log``: Get a log of the steps executed by a Flow…
-  ``action-release``: Remove execution history for a particular…
-  ``action-resume``: Resume a Flow in the INACTIVE state.
-  ``action-status``: Display the status for a Flow definition’s…
-  ``action-update``: Update a Run on the Flows service
-  ``delete``: Delete a Flow.
-  ``deploy``: Deploy a new Flow.
-  ``display``: Visualize a local or deployed Flow defintion.
-  ``get``: Get a Flow’s definition as it exists on the…
-  ``lint``: Parse and validate a Flow definition by…
-  ``list``: List Flows for which you have access.
-  ``run``: Run an instance of a Flow.
-  ``run-cancel``: Cancel an active execution for a particular…
-  ``run-enumerate``: Retrieve all Flow Runs you have access to…
-  ``run-list``: List a Flow definition’s discrete…
-  ``run-log``: Get a log of the steps executed by a Flow…
-  ``run-release``: Remove execution history for a particular…
-  ``run-resume``: Resume a Flow in the INACTIVE state.
-  ``run-status``: Display the status for a Flow definition’s…
-  ``run-update``: Update a Run on the Flows service
-  ``update``: Update a Flow.

``globus-automate flow action-cancel``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cancel an active execution for a particular Flow definition’s
invocation.

**Usage**:

.. code:: console

   $ globus-automate flow action-cancel [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
   [required]
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow action-enumerate``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve all Flow Runs you have access to view.

**Usage**:

.. code:: console

   $ globus-automate flow action-enumerate [OPTIONS]

**Options**:

-  ``--role [run_monitor|run_manager|run_owner|created_by|monitor_by|manage_by]``:
   Display Actions/Runs where you have at least the selected role.
   Precedence of roles is: run_monitor, run_manager, run_owner. Thus, by
   specifying, for example, run_manager, all flows for which you hvae
   run_manager or run_owner roles will be displayed. Values
   monitored_by, managed_by and created_by are deprecated. [repeatable
   use deprecated as the lowest precedence value provided will determine
   the Actions/Runs displayed.] [default: ActionRole.run_owner]
-  ``--status [SUCCEEDED|FAILED|ACTIVE|INACTIVE]``: Display Actions with
   the selected status. [repeatable] [default: ]
-  ``-m, --marker TEXT``: A pagination token for iterating through
   returned data.
-  ``-p, --per-page INTEGER RANGE``: The page size to return. Only valid
   when used without providing a marker.
-  ``--filter TEXT``: A filtering criteria in the form ‘key=value’ to
   apply to the resulting Action listing. The key indicates the filter,
   the value indicates the pattern to match. Multiple patterns for a
   single key may be specified as a comma seperated string, the results
   for which will represent a logical OR. If multiple filters are
   applied, the returned data will be the result of a logical AND
   between them. [repeatable]
-  ``--orderby TEXT``: An ordering criteria in the form ‘key=value’ to
   apply to the resulting Flow listing. The key indicates the field to
   order on, and the value is either ASC, for ascending order, or DESC,
   for descending order. The first ordering criteria will be used to
   sort the data, subsequent ordering criteria will further sort ties.
   [repeatable]
-  ``-w, --watch``: Continuously poll for new Actions. [default: False]
-  ``-f, --format [json|yaml|table]``: Output display format. [default:
   table]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow action-list``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List a Flow definition’s discrete invocations.

**Usage**:

.. code:: console

   $ globus-automate flow action-list [OPTIONS]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
   If not present runs from all Flows will be displayed.
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``--role [run_monitor|run_manager|run_owner|created_by|monitor_by|manage_by]``:
   Display Actions/Runs where you have at least the selected role.
   Precedence of roles is: run_monitor, run_manager, run_owner. Thus, by
   specifying, for example, run_manager, all runs for which you hvae
   run_manager or run_owner roles will be displayed. [repeatable use
   deprecated as the lowest precedence value provided will determine the
   flows displayed.]
-  ``--status [SUCCEEDED|FAILED|ACTIVE|INACTIVE]``: Display Actions with
   the selected status. [repeatable] [default: ]
-  ``-m, --marker TEXT``: A pagination token for iterating through
   returned data.
-  ``-p, --per-page INTEGER RANGE``: The page size to return. Only valid
   when used without providing a marker.
-  ``--filter TEXT``: A filtering criteria in the form ‘key=value’ to
   apply to the resulting Action listing. The key indicates the filter,
   the value indicates the pattern to match. Multiple patterns for a
   single key may be specified as a comma seperated string, the results
   for which will represent a logical OR. If multiple filters are
   applied, the returned data will be the result of a logical AND
   between them. [repeatable]
-  ``--orderby TEXT``: An ordering criteria in the form ‘key=value’ to
   apply to the resulting Flow listing. The key indicates the field to
   order on, and the value is either ASC, for ascending order, or DESC,
   for descending order. The first ordering criteria will be used to
   sort the data, subsequent ordering criteria will further sort ties.
   [repeatable]
-  ``-v, --verbose``: Run with increased verbosity
-  ``-w, --watch``: Continuously poll for new Actions. [default: False]
-  ``-f, --format [json|yaml|table]``: Output display format. [default:
   table]
-  ``--help``: Show this message and exit.

``globus-automate flow action-log``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get a log of the steps executed by a Flow definition’s invocation.

**Usage**:

.. code:: console

   $ globus-automate flow action-log [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
   [required]
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``--reverse``: Display logs starting from most recent and proceeding
   in reverse chronological order [default: False]
-  ``--limit INTEGER RANGE``: Set a maximum number of events from the
   log to return
-  ``-m, --marker TEXT``: A pagination token for iterating through
   returned data.
-  ``-p, --per-page INTEGER RANGE``: The page size to return. Only valid
   when used without providing a marker.
-  ``-f, --format [json|yaml|table|image|graphiz]``: Output display
   format. [default: table]
-  ``-w, --watch``: Continuously poll this Action until it reaches a
   completed state. Using this option will report only the latest state
   available. [default: False]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow action-release``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Remove execution history for a particular Flow definition’s invocation.
After this, no further information about the run can be accessed.

**Usage**:

.. code:: console

   $ globus-automate flow action-release [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
   [required]
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow action-resume``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Resume a Flow in the INACTIVE state. If query-for-inactive-reason is
set, and the Flow Action is in an INACTIVE state due to requiring
additional Consent, the required Consent will be determined and you may
be prompted to allow Consent using the Globus Auth web interface.

**Usage**:

.. code:: console

   $ globus-automate flow action-resume [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
   [required]
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``--query-for-inactive-reason / --no-query-for-inactive-reason``:
   Should the Action first be queried to determine the reason for the
   resume, and prompt for additional consent if needed. [default: True]
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-w, --watch``: Continuously poll this Action until it reaches a
   completed state. [default: False]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow action-status``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Display the status for a Flow definition’s particular invocation.

**Usage**:

.. code:: console

   $ globus-automate flow action-status [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``-w, --watch``: Continuously poll this Action until it reaches a
   completed state. [default: False]
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow action-update``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update a Run on the Flows service

**Usage**:

.. code:: console

   $ globus-automate flow action-update [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--run-manager TEXT``: A principal which may change the execution of
   the Run.The principal value is the user’s Globus Auth username or
   their identity UUID in the form urn:globus:auth:identity:. A Globus
   Group may also be used using the form urn:globus:groups:id:.
   [repeatable]
-  ``--run-monitor TEXT``: A principal which may monitor the execution
   of the Run.The principal value is the user’s Globus Auth username or
   their identity UUID in the form urn:globus:auth:identity:. A Globus
   Group may also be used using the form urn:globus:groups:id:.
   [repeatable]
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``--help``: Show this message and exit.

``globus-automate flow delete``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete a Flow. You must be in the Flow’s “flow_administrators” list.

**Usage**:

.. code:: console

   $ globus-automate flow delete [OPTIONS] FLOW_ID

**Arguments**:

-  ``FLOW_ID``: [required]

**Options**:

-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow deploy``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy a new Flow.

**Usage**:

.. code:: console

   $ globus-automate flow deploy [OPTIONS]

**Options**:

-  ``--title TEXT``: The Flow’s title. [required]
-  ``--definition TEXT``: JSON or YAML representation of the Flow to
   deploy. May be provided as a filename or a raw string representing a
   JSON object or YAML definition. [required]
-  ``--subtitle TEXT``: A subtitle for the Flow providing additional,
   brief description.
-  ``--description TEXT``: A long form description of the Flow’s purpose
   or usage.
-  ``--input-schema TEXT``: A JSON or YAML representation of a JSON
   Schema which will be used to validate the input to the deployed Flow
   when it is run. If not provided, no validation will be performed on
   Flow input. May be provided as a filename or a raw string.
-  ``--keyword TEXT``: A keyword which may categorize or help discover
   the Flow. [repeatable]
-  ``--flow-viewer TEXT``: A principal which may view this Flow. The
   principal value is the user’s Globus Auth username or their identity
   UUID in the form urn:globus:auth:identity:. A Globus Group may also
   be used using the form urn:globus:groups:id:. The special value of
   ‘public’ may be used to indicate that any user can view this Flow.
   [repeatable]
-  ``--flow-starter TEXT``: A principal which may run an instance of the
   deployed Flow. The principal value is the user’s Globus Auth username
   or their identity UUID in the form urn:globus:auth:identity:. A
   Globus Group may also be used using the form
   urn:globus:groups:id:.The special value of ‘all_authenticated_users’
   may be used to indicate that any authenticated user can invoke this
   flow. [repeatable]
-  ``--flow-administrator TEXT``: A principal which may update the
   deployed Flow. The principal value is the user’s Globus Auth username
   or their identity UUID in the form urn:globus:auth:identity:. A
   Globus Group may also be used using the form
   urn:globus:groups:id:.[repeatable]
-  ``--subscription-id TEXT``: The Id of the Globus Subscription which
   will be used to make this flow managed.
-  ``--validate / --no-validate``: (EXPERIMENTAL) Perform rudimentary
   validation of the flow definition. [default: True]
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``--dry-run``: Do a dry run of deploying the flow to test your
   definition without actually making changes. [default: False]
-  ``--help``: Show this message and exit.

``globus-automate flow display``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Visualize a local or deployed Flow defintion. If providing a Flows’s ID,
You must have either created the Flow or be present in the Flow’s
“flow_viewers” list to view it.

**Usage**:

.. code:: console

   $ globus-automate flow display [OPTIONS] [FLOW_ID]

**Arguments**:

-  ``[FLOW_ID]``

**Options**:

-  ``--flow-definition TEXT``: JSON or YAML representation of the Flow
   to display. May be provided as a filename or a raw string
   representing a JSON object or YAML definition.
-  ``-f, --format [json|yaml|image|graphviz]``: Output display format.
   [default: json]
-  ``--help``: Show this message and exit.

``globus-automate flow get``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get a Flow’s definition as it exists on the Flows service.

**Usage**:

.. code:: console

   $ globus-automate flow get [OPTIONS] FLOW_ID

**Arguments**:

-  ``FLOW_ID``: A deployed Flow’s ID [required]

**Options**:

-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow lint``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parse and validate a Flow definition by providing visual output.

**Usage**:

.. code:: console

   $ globus-automate flow lint [OPTIONS]

**Options**:

-  ``--definition TEXT``: JSON or YAML representation of the Flow to
   deploy. May be provided as a filename or a raw string. [required]
-  ``--help``: Show this message and exit.

``globus-automate flow list``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List Flows for which you have access.

**Usage**:

.. code:: console

   $ globus-automate flow list [OPTIONS]

**Options**:

-  ``-r, --role [flow_viewer|flow_starter|flow_administrator|flow_owner|created_by|visible_to|runnable_by|administered_by]``:
   Display Flows where you have at least the selected role. Precedence
   of roles is: flow_viewer, flow_starter, flow_administrator,
   flow_owner. Thus, by specifying, for example, flow_starter, all flows
   for which you hvae flow_starter, flow_administrator, or flow_owner
   roles will be displayed. Values visible_to, runnable_by,
   administered_by and created_by are deprecated. [repeatable use
   deprecated as the lowest precedence value provided will determine the
   flows displayed.] [default: FlowRole.flow_owner]
-  ``-m, --marker TEXT``: A pagination token for iterating through
   returned data.
-  ``-p, --per-page INTEGER RANGE``: The page size to return. Only valid
   when used without providing a marker.
-  ``--filter TEXT``: A filtering criteria in the form ‘key=value’ to
   apply to the resulting Flow listing. The key indicates the filter,
   the value indicates the pattern to match. Multiple patterns for a
   single key may be specified as a comma seperated string, the results
   for which will represent a logical OR. If multiple filters are
   applied, the returned data will be the result of a logical AND
   between them. [repeatable]
-  ``--orderby TEXT``: An ordering criteria in the form ‘key=value’ to
   apply to the resulting Flow listing. The key indicates the field to
   order on, and the value is either ASC, for ascending order, or DESC,
   for descending order. The first ordering criteria will be used to
   sort the data, subsequent ordering criteria will further sort ties.
   [repeatable]
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml|table]``: Output display format. [default:
   table]
-  ``-w, --watch``: Continuously poll for new Flows. [default: False]
-  ``--help``: Show this message and exit.

``globus-automate flow run``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run an instance of a Flow. The argument provides the initial state of
the Flow. You must be in the Flow’s “flow_starters” list.

**Usage**:

.. code:: console

   $ globus-automate flow run [OPTIONS] FLOW_ID

**Arguments**:

-  ``FLOW_ID``: [required]

**Options**:

-  ``--flow-input TEXT``: JSON or YAML formatted input to the Flow. May
   be provided as a filename or a raw string. [required]
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``--run-manager TEXT``: A principal which may change the execution of
   the Flow instance. The principal value is the user’s Globus Auth
   username or their identity UUID in the form
   urn:globus:auth:identity:. A Globus Group may also be used using the
   form urn:globus:groups:id:. [repeatable]
-  ``--run-monitor TEXT``: A principal which may monitor the execution
   of the Flow instance. The principal value is the user’s Globus Auth
   username or their identity UUID in the form
   urn:globus:auth:identity:. A Globus Group may also be used using the
   form urn:globus:groups:id:. [repeatable]
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml|table]``: Output display format. If –watch
   is enabled then the default is ‘table’, otherwise ‘json’ is the
   default.
-  ``-l, --label TEXT``: Label to mark this run. [required]
-  ``-w, --watch``: Continuously poll this Action until it reaches a
   completed state. If enabled the default output format is ‘table’.
   [default: False]
-  ``--dry-run``: Do a dry run with your input to this flow to test the
   input without actually running anything. [default: False]
-  ``--help``: Show this message and exit.

``globus-automate flow run-cancel``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cancel an active execution for a particular Flow definition’s
invocation.

**Usage**:

.. code:: console

   $ globus-automate flow run-cancel [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
   [required]
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow run-enumerate``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrieve all Flow Runs you have access to view.

**Usage**:

.. code:: console

   $ globus-automate flow run-enumerate [OPTIONS]

**Options**:

-  ``--role [run_monitor|run_manager|run_owner|created_by|monitor_by|manage_by]``:
   Display Actions/Runs where you have at least the selected role.
   Precedence of roles is: run_monitor, run_manager, run_owner. Thus, by
   specifying, for example, run_manager, all flows for which you hvae
   run_manager or run_owner roles will be displayed. Values
   monitored_by, managed_by and created_by are deprecated. [repeatable
   use deprecated as the lowest precedence value provided will determine
   the Actions/Runs displayed.] [default: ActionRole.run_owner]
-  ``--status [SUCCEEDED|FAILED|ACTIVE|INACTIVE]``: Display Actions with
   the selected status. [repeatable] [default: ]
-  ``-m, --marker TEXT``: A pagination token for iterating through
   returned data.
-  ``-p, --per-page INTEGER RANGE``: The page size to return. Only valid
   when used without providing a marker.
-  ``--filter TEXT``: A filtering criteria in the form ‘key=value’ to
   apply to the resulting Action listing. The key indicates the filter,
   the value indicates the pattern to match. Multiple patterns for a
   single key may be specified as a comma seperated string, the results
   for which will represent a logical OR. If multiple filters are
   applied, the returned data will be the result of a logical AND
   between them. [repeatable]
-  ``--orderby TEXT``: An ordering criteria in the form ‘key=value’ to
   apply to the resulting Flow listing. The key indicates the field to
   order on, and the value is either ASC, for ascending order, or DESC,
   for descending order. The first ordering criteria will be used to
   sort the data, subsequent ordering criteria will further sort ties.
   [repeatable]
-  ``-w, --watch``: Continuously poll for new Actions. [default: False]
-  ``-f, --format [json|yaml|table]``: Output display format. [default:
   table]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow run-list``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List a Flow definition’s discrete invocations.

**Usage**:

.. code:: console

   $ globus-automate flow run-list [OPTIONS]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
   If not present runs from all Flows will be displayed.
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``--role [run_monitor|run_manager|run_owner|created_by|monitor_by|manage_by]``:
   Display Actions/Runs where you have at least the selected role.
   Precedence of roles is: run_monitor, run_manager, run_owner. Thus, by
   specifying, for example, run_manager, all runs for which you hvae
   run_manager or run_owner roles will be displayed. [repeatable use
   deprecated as the lowest precedence value provided will determine the
   flows displayed.]
-  ``--status [SUCCEEDED|FAILED|ACTIVE|INACTIVE]``: Display Actions with
   the selected status. [repeatable] [default: ]
-  ``-m, --marker TEXT``: A pagination token for iterating through
   returned data.
-  ``-p, --per-page INTEGER RANGE``: The page size to return. Only valid
   when used without providing a marker.
-  ``--filter TEXT``: A filtering criteria in the form ‘key=value’ to
   apply to the resulting Action listing. The key indicates the filter,
   the value indicates the pattern to match. Multiple patterns for a
   single key may be specified as a comma seperated string, the results
   for which will represent a logical OR. If multiple filters are
   applied, the returned data will be the result of a logical AND
   between them. [repeatable]
-  ``--orderby TEXT``: An ordering criteria in the form ‘key=value’ to
   apply to the resulting Flow listing. The key indicates the field to
   order on, and the value is either ASC, for ascending order, or DESC,
   for descending order. The first ordering criteria will be used to
   sort the data, subsequent ordering criteria will further sort ties.
   [repeatable]
-  ``-v, --verbose``: Run with increased verbosity
-  ``-w, --watch``: Continuously poll for new Actions. [default: False]
-  ``-f, --format [json|yaml|table]``: Output display format. [default:
   table]
-  ``--help``: Show this message and exit.

``globus-automate flow run-log``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get a log of the steps executed by a Flow definition’s invocation.

**Usage**:

.. code:: console

   $ globus-automate flow run-log [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
   [required]
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``--reverse``: Display logs starting from most recent and proceeding
   in reverse chronological order [default: False]
-  ``--limit INTEGER RANGE``: Set a maximum number of events from the
   log to return
-  ``-m, --marker TEXT``: A pagination token for iterating through
   returned data.
-  ``-p, --per-page INTEGER RANGE``: The page size to return. Only valid
   when used without providing a marker.
-  ``-f, --format [json|yaml|table|image|graphiz]``: Output display
   format. [default: table]
-  ``-w, --watch``: Continuously poll this Action until it reaches a
   completed state. Using this option will report only the latest state
   available. [default: False]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow run-release``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Remove execution history for a particular Flow definition’s invocation.
After this, no further information about the run can be accessed.

**Usage**:

.. code:: console

   $ globus-automate flow run-release [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
   [required]
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow run-resume``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Resume a Flow in the INACTIVE state. If query-for-inactive-reason is
set, and the Flow Action is in an INACTIVE state due to requiring
additional Consent, the required Consent will be determined and you may
be prompted to allow Consent using the Globus Auth web interface.

**Usage**:

.. code:: console

   $ globus-automate flow run-resume [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
   [required]
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``--query-for-inactive-reason / --no-query-for-inactive-reason``:
   Should the Action first be queried to determine the reason for the
   resume, and prompt for additional consent if needed. [default: True]
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-w, --watch``: Continuously poll this Action until it reaches a
   completed state. [default: False]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow run-status``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Display the status for a Flow definition’s particular invocation.

**Usage**:

.. code:: console

   $ globus-automate flow run-status [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--flow-id TEXT``: The ID for the Flow which triggered the Action.
-  ``--flow-scope TEXT``: The scope this Flow uses to authenticate
   requests.
-  ``-w, --watch``: Continuously poll this Action until it reaches a
   completed state. [default: False]
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate flow run-update``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update a Run on the Flows service

**Usage**:

.. code:: console

   $ globus-automate flow run-update [OPTIONS] ACTION_ID

**Arguments**:

-  ``ACTION_ID``: [required]

**Options**:

-  ``--run-manager TEXT``: A principal which may change the execution of
   the Run.The principal value is the user’s Globus Auth username or
   their identity UUID in the form urn:globus:auth:identity:. A Globus
   Group may also be used using the form urn:globus:groups:id:.
   [repeatable]
-  ``--run-monitor TEXT``: A principal which may monitor the execution
   of the Run.The principal value is the user’s Globus Auth username or
   their identity UUID in the form urn:globus:auth:identity:. A Globus
   Group may also be used using the form urn:globus:groups:id:.
   [repeatable]
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``--help``: Show this message and exit.

``globus-automate flow update``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update a Flow.

**Usage**:

.. code:: console

   $ globus-automate flow update [OPTIONS] FLOW_ID

**Arguments**:

-  ``FLOW_ID``: [required]

**Options**:

-  ``--title TEXT``: The Flow’s title.
-  ``--definition TEXT``: JSON or YAML representation of the Flow to
   update. May be provided as a filename or a raw string.
-  ``--subtitle TEXT``: A subtitle for the Flow providing additional,
   brief description.
-  ``--description TEXT``: A long form description of the Flow’s purpose
   or usage.
-  ``--input-schema TEXT``: A JSON or YAML representation of a JSON
   Schema which will be used to validate the input to the deployed Flow
   when it is run. If not provided, no validation will be performed on
   Flow input. May be provided as a filename or a raw string.
-  ``--keyword TEXT``: A keyword which may categorize or help discover
   the Flow. [repeatable]
-  ``--flow-viewer TEXT``: A principal which may view this Flow. The
   principal value is the user’s Globus Auth username or their identity
   UUID in the form urn:globus:auth:identity:. A Globus Group may also
   be used using the form urn:globus:groups:id:.The special value of
   ‘public’ may be used to indicate that any user can view this Flow.
   [repeatable]
-  ``--flow-starter TEXT``: A principal which may run an instance of the
   deployed Flow. The principal value is the user’s Globus Auth username
   or their identity UUID in the form urn:globus:auth:identity:. A
   Globus Group may also be used using the form urn:globus:groups:id:.
   The special value of ‘all_authenticated_users’ may be used to
   indicate that any authenticated user can invoke this flow.
   [repeatable]
-  ``--flow-administrator TEXT``: A principal which may update the
   deployed Flow. The principal value is the user’s Globus Auth username
   or their identity UUID in the form urn:globus:auth:identity:. A
   Globus Group may also be used using the form
   urn:globus:groups:id:.[repeatable]
-  ``--assume-ownership``: Assume the ownership of the Flow. This can
   only be performed by user’s in the flow_administrators role.
   [default: False]
-  ``--subscription-id TEXT``: The Globus Subscription which will be
   used to make this flow managed.
-  ``--validate / --no-validate``: (EXPERIMENTAL) Perform rudimentary
   validation of the flow definition. [default: True]
-  ``-v, --verbose``: Run with increased verbosity
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``--help``: Show this message and exit.

``globus-automate queue``
-------------------------

**Usage**:

.. code:: console

   $ globus-automate queue [OPTIONS] COMMAND [ARGS]...

**Options**:

-  ``--help``: Show this message and exit.

**Commands**:

-  ``create``: Create a new Queue.
-  ``delete``: Delete a Queue based on its id.
-  ``display``: Display the description of a Queue based on…
-  ``list``: List Queues for which you have access.
-  ``message-delete``: Notify a Queue that a message has been…
-  ``message-receive``: Receive a message from a Queue.
-  ``message-send``: Send a message to a Queue.
-  ``update``: Update a Queue’s properties.

``globus-automate queue create``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new Queue.

**Usage**:

.. code:: console

   $ globus-automate queue create [OPTIONS]

**Options**:

-  ``--label TEXT``: A convenient name to identify the new Queue.
   [required]
-  ``--admin TEXT``: The Principal URNs allowed to administer the Queue.
   [repeatable] [required]
-  ``--sender TEXT``: The Principal URNs allowed to send to the Queue.
   [repeatable] [required]
-  ``--receiver TEXT``: The Principal URNs allowed to receive from the
   Queue. [repeatable] [required]
-  ``--delivery-timeout INTEGER RANGE``: The minimum amount of time (in
   seconds) that the Queue Service should wait for a message-delete
   request after delivering a message before making the message visible
   for receiving by other consumers once again. If used in conjunction
   with ‘receiver_url’ this value represents the minimum amount of time
   (in seconds) that the Queue Service should attempt to retry delivery
   of messages to the ‘receiver_url’ if delivery is not initially
   successful [default: 60]
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate queue delete``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete a Queue based on its id. You must have either created the Queue
or have a role defined on the Queue.

**Usage**:

.. code:: console

   $ globus-automate queue delete [OPTIONS] QUEUE_ID

**Arguments**:

-  ``QUEUE_ID``: [required]

**Options**:

-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate queue display``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Display the description of a Queue based on its id.

**Usage**:

.. code:: console

   $ globus-automate queue display [OPTIONS] QUEUE_ID

**Arguments**:

-  ``QUEUE_ID``: [required]

**Options**:

-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate queue list``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

List Queues for which you have access.

**Usage**:

.. code:: console

   $ globus-automate queue list [OPTIONS]

**Options**:

-  ``-r, --role [admin|sender|receiver]``: Display Queues where you have
   the selected role. [repeatable] [default: QueueRole.admin]
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate queue message-delete``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notify a Queue that a message has been processed.

**Usage**:

.. code:: console

   $ globus-automate queue message-delete [OPTIONS] QUEUE_ID

**Arguments**:

-  ``QUEUE_ID``: [required]

**Options**:

-  ``--receipt-handle TEXT``: A receipt_handle value returned by a
   previous call to receive message. [repeatable] [required]
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate queue message-receive``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Receive a message from a Queue. You must have the “receiver” role on the
Queue to perform this action.

**Usage**:

.. code:: console

   $ globus-automate queue message-receive [OPTIONS] QUEUE_ID

**Arguments**:

-  ``QUEUE_ID``: [required]

**Options**:

-  ``--max-messages INTEGER RANGE``: The maximum number of messages to
   retrieve from the Queue
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate queue message-send``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send a message to a Queue. You must have the “sender” role on the Queue
to perform this action.

**Usage**:

.. code:: console

   $ globus-automate queue message-send [OPTIONS] QUEUE_ID

**Arguments**:

-  ``QUEUE_ID``: [required]

**Options**:

-  ``-m, --message TEXT``: Text of the message to send. Files may also
   be referenced. [required]
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate queue update``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update a Queue’s properties. Requires the admin role on the Queue.

**Usage**:

.. code:: console

   $ globus-automate queue update [OPTIONS] QUEUE_ID

**Arguments**:

-  ``QUEUE_ID``: [required]

**Options**:

-  ``--label TEXT``: A convenient name to identify the new Queue.
   [required]
-  ``--admin TEXT``: The Principal URNs allowed to administer the Queue.
   [repeatable] [required]
-  ``--sender TEXT``: The Principal URNs allowed to send to the Queue.
   [repeatable] [required]
-  ``--receiver TEXT``: The Principal URNs allowed to receive from the
   Queue. [repeatable] [required]
-  ``--delivery-timeout INTEGER RANGE``: The minimum amount of time (in
   seconds) that the Queue Service should wait for a message-delete
   request after delivering a message before making the message visible
   for receiving by other consumers once again. If used in conjunction
   with ‘receiver_url’ this value represents the minimum amount of time
   (in seconds) that the Queue Service should attempt to retry delivery
   of messages to the ‘receiver_url’ if delivery is not initially
   successful [required]
-  ``--visibility-timeout INTEGER RANGE``: [default: 30]
-  ``-f, --format [json|yaml]``: Output display format. [default: json]
-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.

``globus-automate session``
---------------------------

**Usage**:

.. code:: console

   $ globus-automate session [OPTIONS] COMMAND [ARGS]...

**Options**:

-  ``--help``: Show this message and exit.

**Commands**:

-  ``logout``: Remove all locally cached Globus Automate…
-  ``revoke``: Remove all locally cached Globus Automate…
-  ``whoami``: Determine the username for the identity…

``globus-automate session logout``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Remove all locally cached Globus Automate authentication information.

**Usage**:

.. code:: console

   $ globus-automate session logout [OPTIONS]

**Options**:

-  ``--help``: Show this message and exit.

``globus-automate session revoke``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Remove all locally cached Globus Automate authentication information and
invalidate all locally cached access or refresh tokens. These tokens can
no longer be used elsewhere.

**Usage**:

.. code:: console

   $ globus-automate session revoke [OPTIONS]

**Options**:

-  ``--help``: Show this message and exit.

``globus-automate session whoami``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Determine the username for the identity logged in to Globus Auth. If run
with increased verbosity, the caller’s full user information is
displayed.

**Usage**:

.. code:: console

   $ globus-automate session whoami [OPTIONS]

**Options**:

-  ``-v, --verbose``: Run with increased verbosity
-  ``--help``: Show this message and exit.
