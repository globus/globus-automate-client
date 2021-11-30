CHANGELOG
#########

Unreleased changes
==================

Unreleased changes are documented in files in the `changelog.d`_ directory.

..  _changelog.d: https://github.com/globus/globus-automate-client/tree/main/changelog.d

..  scriv-insert-here

0.12.3 — 2021-11-10
===================

Bugfixes
--------

-   Fix a bug that prevented the Flows client from properly validating flow definition states in lists.
-   Prevent empty values from appearing in query parameters or JSON submissions.
-   Fix a bug that prevented the input schema of an existing Flow from being set to an all-permissive JSON schema.
-   Fix a bug that prevented a custom authorizer from being used if attempting to list all runs of a specific flow without specifying the flow ID.
-   Fix a bug that introduced duplicate forward slashes in some API URL's.

Documentation
-------------

- Add a CHANGELOG and include it in the documentation.
- Use scriv for CHANGELOG management.

- Added documentation for the new Action Providers for:
  - Make a directory via Globus Transfer (mkdir)
  - Get collection information via Globus Transfer (collection_info)
- Added documentation for new feature of the list directory Action Provider to get information only about the path provided as input

- Added documentation related to use of built-in functions in expressions. Documented the new functions ``pathsplit``, ``is_present`` and ``getattr``.

0.12.2 — 2021-10-19
===================

Features
--------

-   The output of globus-automate flow list is modified to ensure that the Flow ID is always visible.
    The new output search is similar to the output of ``globus endpoint search``.
-   The output when watching the results of a ``globus-automate flow run`` now defaults to table view.

Bugfixes
--------

-   Fixes an infinite loop when watching the output of ``flow action-log``/``flow run-log`` with the ``--reverse`` flag.
-   Fixes the limit minimum level from 0 to 1 when doing ``flow action-log``/``flow run-log`` to prevent server errors.
-   Fixes a bug where an unsafe indexing operation was being made during ``flow action-list``/``flow run-list``

Documentation
-------------

-   CLI documentation is updated to more precisely reflect that ``--label`` is a required property when running a Flow.

0.12.1 — 2021-09-14
===================

Features
--------

-   CLI commands which output lists of data now display a subset of the data fields as a table.
    For access to the full data or to access data in JSON or YAML format, the ``-f json | yaml`` option may be used.
    The tabular output is on the following commands:
    -   ``globus-automate flow list``
    -   ``globus-automate flow action-list ...``
    -   ``globus-automate flow action-enumerate ...``
    -   ``globus-automate flow action-log ...``
-   File inputs to CLI commands may now be in either JSON or YAML formatting without the need to specify the input file format.

Bugfixes
--------

-   Fixed an error where the output of the ``globus-automate flow update`` command displayed unformatted JSON

Documentation
-------------

-   Added text explaining that the Fail state is a supported state type and can be used in Flows.
    A simple example using the Fail state is included in the examples directory for the repository.

0.12.0 — 2021-08-16
===================

Features
--------

-   CLI and SDK support for updating user roles on new and existing Runs
-   Wherever identities are referenced on the CLI we now support supplying Globus Auth usernames instead.
-   Updates to CLI and SDK arguments to more closely reflect RBAC updates in the Flows service.

Bugfixes
--------

-   The Run enumeration CLI and SDK methods would attempt to use the Flow manage authorizer to authenticate its calls.
    This method has been updated to instead look up or create an authorizer for the RUN_STATUS scope

Documentation
-------------

-   The RBAC system for the Flows service has been updated to follow a subset model
    rather than the previously existing separate permissions model.
    The documentation has been updated with `a description of the new behavior <https://globus-automate-client.readthedocs.io/en/latest/overview.html?highlight=role#authentication-and-authorization>`_.

0.11.5 — 2021-06-17
===================

Features
--------

-   Adds SDK and CLI support for dry running a Flow deploy or Flow run
-   Adds SDK + CLI commands for enumerating Actions and sorting/filtering through results
-   Adds a CLI command to retrieve a single Flow definition and its metadata: ``globus-automate flow get <id>``
-   Expands the use of the ``create_flows_client`` function to allow specifying an authorizer, an authorizer callback, and a http_timeout.

Bugfixes
--------

-   Fixes a regression where Flow deploy results via the CLI were unformatted
-   Adds license to output of ``pip show globus-automate-client``

Documentation
-------------

-   Fixes an issue where ``FlowsClient`` and ``ActionClient`` auto-generated docs were not getting generated
-   Adds references to exemplar Flows and their inputs
-   Adds input examples to Action Provider reference page
-   Adds a hosted CLI reference

0.11.4 — 2021-05-10
===================

Features
--------

-   The CLI and SDK now allow Subscription IDs to be associated with Flows

Bugfixes
--------

-   The Flow List CLI and SDK operations were sending malformed query arguments to the API,
    which produced incorrect results when trying to filter based on role.
    This release corrects the behavior.

0.11.3 — 2021-05-04
===================

Bugfixes
--------

-   Reformats verbose output to make the separation between request information and request results more obvious
-   Verbose output writes output to ``stderr`` to allow output to be parsed as ``JSON``
-   Empty query arguments are not sent as part of the Flows API request

Documentation
-------------

-   Typo fixes

0.11.1 — 2021-04-08
===================

Features
--------

-   ``flow display`` can now visualize local Flow definitions and deployed Flows.

Bugfixes
--------

-   Fixes an issue where the Globus Auth login link was being rendered as a non-clickable link.
-   Fixes an issue where the prompt for inputting the Globus Auth auth code was disappearing.

Documentation
-------------

-   Adds explanation and examples for how to use ``manage_by`` and ``monitor_by`` values on Actions and Flow runs to delegate access to other identities.
-   Clarifies the expected format for provided identities.
-   Explicitly adds ``manage_by`` and ``monitor_by`` as parameters to the ``FlowsClient.run`` method.

0.11.0 — 2021-03-29
===================

Features
--------

-   Export the ``validate_flow_definition`` function which can be used to perform a local JSONSchema based validation of a Flow definition.
-   Using ``create_flows_client`` no longer requires the use of a ``CLIENT_ID``.
-   The ``action run``, ``action status``, ``flow run``, ``flow status``, and ``flow log`` CLI commands
    implement a new ``--watch`` flag which lets you stream an Action's status updates.
-   CLI and SDK level support for filtering and ordering Flow Listing and Flow Action Enumerations endpoints [preview].
-   New CLI commands to facilitate the following ``Globus Auth``  operations:
    -   ``session whoami`` - determine the caller's user information as it exists in Auth
    -   ``session logout`` - remove locally cached auth state
    -   ``session revoke`` - invalidate local tokens and remove locally cached auth state.

Documentation
-------------

-   Various typo fixes.

0.10.7 — 2021-02-11
===================

Features
--------

-   Improved error handling on CLI operations so that users receive formatted output instead of ``GlobusAPIError`` tracebacks.
-   Added CLI and SDK level support for using ``label``\s to launch Flows and Actions.

Documentation
-------------

-   Removes references to ``ActionScope`` from example Flow definitions because the Flows service handles the scope lookups.

Bugfixes
--------

-   The Flows CLI interface would attempt to load empty arguments, resulting in ``NoneType`` errors.
    Empty arguments are now ignored.
-   When using the CLI with the ``--verbose`` flag, the results of the verbosity are printed to ``stderr``,
    allowing the commands outputs to still be parsed by other tools, such as ``jq``.
-   Fixes a ``NameTooLong``  exception that was thrown when the CLI attempted to parse long JSON strings as filenames.

0.10.6 — 2021-01-27
===================

Features
--------

-   Adds support for YAML formatted input when defining Flows, input schemas, and inputs via the CLI.

Documentation
-------------

-   Improves documentation around manually creating authorizers and how to use them to create ``ActionClients`` and ``FlowsClient``:
    https://globus-automate-client.readthedocs.io/en/latest/python_sdk.html#sdk-the-hard-way
-   Adds examples for Flow definitions as YAML:
    https://github.com/globus/globus-automate-client/tree/main/examples/flows/hello-world-yaml

0.10.5 — 2020-12-11
===================

Features
--------

-   Removes custom SSH session detection in favor of using fair-research native-login's SSH session detection
-   Adds Flows pagination support to CLI and SDK layers
-   Fully decouples the SDK from the CLI.
    SDK users can now opt to supply their own authorizers for Flow operations,
    either as a kwargs to the operation or as a callback to the FlowsClient
    which should be used to lookup the appropriate authorizer.

Documentation
-------------

-   Fixes typos in Flow's documentation where Private_Parameters were incorrectly referenced as Private_Properties
-   Publishes a new example Flow for performing a multi-step Transfer & delete, along with error checking

0.10.4 — 2020-10-01
===================

Features
--------

-   Added support for deleting messages off a Globus Queue to the CLI and SDK
-   Adds example action bodies to the repository for running an action on the new Search Delete Action Provider
-   Updated docs and example action bodies for running an action on the Set Permissions Action Provider
-   Updates the schema validation for the Pass State to make Parameters and InputPath optional.

Bugfixes
--------

-   Corrected an issue in CLI option validation where "public" and "all_authenticated_users" were not being accepted
-   Corrected an issue where the SDK's ActionClient was setting monitor_by and manage_by to None by default,
    thus failing Action Provider schema validation.

0.10 — 2020-08-24
=================

This release is the first based on the public globus-automate-client repository.
Compared to previous PyPi releases, this release contains:

-   A more complete set of documentation which is also published to readthedocs
-   A set of examples under the examples directory
-   Client side validation of flow definitions based on a jsonschema.
    This is somewhat experimental at this point,
    and feedback is welcome on experience both with the accuracy and the helpfulness of the reported errors.
    Validation is turned on by default when deploying or linting a flow,
    but can be turned off with the SDK parameter ``validate_definition`` and the CLI ``--validate/no-validate`` flags.
