CHANGELOG
#########

Unreleased changes
==================

Unreleased changes are documented in files in the `changelog.d`_ directory.

..  _changelog.d: https://github.com/globus/globus-automate-client/tree/main/changelog.d

..  scriv-insert-here

.. _changelog-0.17.1:

0.17.1 — 2023-07-24
===================

Bugfixes
--------

- Update pyyaml to 6.0.1 in order to resolve build issues related to Cython 3.

.. _changelog-0.17.0:

0.17.0 — 2023-03-16
===================

Features
--------

-   Add official support for python3.11

-   Support retrieval of the flow definition and input schema used to start a run.

    This is supported in the new ``flow run-definition`` subcommand.

Bugfixes
--------

-   Fix a bug which could lead to improper handling of token refreshes

-   `[sc-19291] <https://app.shortcut.com/globus/story/19291>`_
    Prevent passive flow permission updates.

    Previously, permissions were erased during updates if no permissions were specified.
    Now, permissions will only be erased if an empty string is passed. For example:

    ..  code-block:: text

        # Erase all viewer permissions.
        globus-automate flow update $UUID --flow-viewer=""

Documentation
-------------

-   Fix example flow definition web-option-with-parameters

-   Improve documentation by normalizing capitalization and emphasis, as well as
    clarifying usage of "Globus Automate" wherever it occurred.

-   Add simplified versions of our production flows as inline examples on the
    "Authoring Flows" page.

.. _changelog-0.16.1.post1:

0.16.1.post1 — 2022-07-15
=========================

Documentation
-------------

-   `[sc-16711] <https://app.shortcut.com/globus/story/16711>`_
    Document how to automatically run a flow based on filesystem change events.

.. _changelog-0.16.1:

0.16.1 — 2022-06-23
===================

Bugfixes
--------

-   Fix a bug in the flow administrator/starter/runner CLI alias validation
    which prevents successfully running the ``flow update`` subcommand.

.. _changelog-0.16.0:

0.16.0 — 2022-06-23
===================

Changes
-------

-   `[sc-13892] <https://app.shortcut.com/globus/story/13892>`_
    Standardize flow viewer, starter, and administrator arguments -- and their aliases -- throughout the CLI and API.

    Although this change fixes bugs that prevented documented CLI options from working,
    it also introduces breaking changes:

    *   ``--flow-viewer``, ``--flow-starter``, and ``--flow-administrator`` are the canonical CLI options.
    *   The CLI option aliases will continue to work, but the alias behavior has changed:

        *   If an alias is used, a warning is written to STDERR.
        *   If the canonical option name is combined with one of its aliases,
            an error will be written to STDERR and the Automate client will exit.
            The exit code will be 1.
        *   If more than one of the acceptable aliases is used (like ``--starter`` and ``--runnable-by``),
            an error will be written to STDERR and the Automate client will exit.
            The exit code will be 1.

    In addition, there are breaking changes in the API:

    *   ``flow_viewers``, ``flow_starters``, and ``flow_administrators`` are the canonical API argument names.
    *   The API argument aliases will continue to work, but the alias behavior has changed:

        *   If an alias is used, a Python warning will be issued.
            Applications can control the warning behavior using Python's ``warnings`` module.
        *   If the canonical option name is combined with one of its aliases, a ``ValueError`` will be raised.
        *   If more than one of the acceptable aliases is used (like ``starters`` and ``runnable_by``), a ``ValueError`` will be raised.

Bugfixes
--------

-   Update pyjwt to version 2.4.0 to address
    `CVE-2022-29217 <https://nvd.nist.gov/vuln/detail/CVE-2022-29217>`_.

.. _changelog-0.15.2:

0.15.2 — 2022-06-06
===================

-   `[sc-16137] <https://app.shortcut.com/globus/story/16137>`_
    Fix flows run dry-run URL path

.. _changelog-0.15.1:

0.15.1 — 2022-05-09
===================

Bugfixes
--------

-   Fix a missing dependency when running on Python 3.10.

    This was fixed by adding typing-extensions as an explicit dependency.
    Note that pip may need to be upgraded due to changes in its dependency resolver.

.. _changelog-0.15.0.post1:

0.15.0.post1 — 2022-05-09
=========================

    **NOTE:**

    This release contains no changes from 0.15.0.
    It adds text to the changelog regarding an update to the rich package dependency.

Documentation
-------------

-   `[sc-13642] <https://app.shortcut.com/globus/story/13642>`_
    Provide two examples of looping in flow definitions:

    *   How to loop a set number of times
    *   How to perform batch processing over an unknown quantity of items

Development
-----------

-   Update click to version 8.0.4.
    This resolves a security issue.
-   Update typer to version 0.4.1.
-   Update scriv to version 0.14.0.
    scriv is a development dependency.
-   Update rich to 0.12.3.

    This resolves a dependency conflict between the Globus CLI and the Globus Automate CLI.
    Both command line clients can now be installed in the same environment.

-   Temporarily remove typer-cli as a listed development dependency.
    It is still needed when generating the CLI documentation.
-   Add safety as a test environment for local and CI testing.
-   Test against Python 3.10 in CI.
-   `[sc-14485] <https://app.shortcut.com/globus/story/14485>`_
    Disable SSL verification when interacting with a local development server.

.. _changelog-0.15.0:

0.15.0 — 2022-04-29
===================

Documentation
-------------

-   `[sc-13642] <https://app.shortcut.com/globus/story/13642>`_
    Provide two examples of looping in flow definitions:

    *   How to loop a set number of times
    *   How to perform batch processing over an unknown quantity of items

Development
-----------

-   Update click to version 8.0.4.
    This resolves a security issue.
-   Update typer to version 0.4.1.
-   Update scriv to version 0.14.0.
    scriv is a development dependency.
-   Temporarily remove typer-cli as a listed development dependency.
    It is still needed when generating the CLI documentation.
-   Add safety as a test environment for local and CI testing.
-   Test against Python 3.10 in CI.

-   `[sc-14485] <https://app.shortcut.com/globus/story/14485>`_
    Disable SSL verification when interacting with a local development server.

0.14.1 — 2022-04-13
===================

Bugfixes
--------

- Changed text on improper token cache file condition so that it doesn't reference the Timer CLI

0.14.0 — 2022-03-25
===================

Features
--------

-   `[sc-13426] <https://app.shortcut.com/globus/story/13426>`_
    Support setting tags when using the ``flow run`` subcommand.
-   Support batch updates of one or more Runs.
-   Support updating tags and labels using the ``flow run-update`` subcommand.
-   Support erasing the list of Run managers and Run monitors using the ``flow run-update`` subcommand.
    This can be done by specifying an empty string for the value of the ``--run-manager`` and ``--run-monitor`` options.

Bugfixes
--------

-   `[sc-13664] <https://app.shortcut.com/globus/story/13664/>`_
    Fix tabular ``run-list`` output.
-   `[sc-14109] <https://app.shortcut.com/globus/story/14109>`_
    Mark the ``run-status`` subcommand's ``--flow-id`` option as a mandatory UUID.
-   `[sc-14127] <https://app.shortcut.com/globus/story/14127>`_
    Prevent a validation error that occurs when an input schema is not provided to the ``flow deploy`` subcommand.

0.13.1 — 2022-03-02
===================

Bugfixes
--------

-   Output login prompts to STDERR.
    This protects serialized output to STDOUT so it can be piped to tools like `jq`.

Documentation
-------------

- Documentation and examples for the ``globus-collection`` input schema format.

0.13.0 — 2022-02-11
===================

Documentation
-------------

- Add the ``"notify_on_*"`` parameters to the transfer action provider JSON example.

- The description of the Action polling policy has been updated and a discussion of how caching of token validation checks may impact users who invalidate their tokens has been added.

- Adds an input schema for the example single-transfer Flow definition.

- Add documentation for `globus-collection-id` and `globus-collection-path` formats

0.13.0b2 — 2021-12-09
=====================

Bugfixes
--------

-   Fix a ``KeyError`` crash that occurs when enabling verbose output using the ``-v`` argument. (#111)
-   Fix a ``ValueError`` crash that occurs when displaying a flow. (#110)

0.13.0b1 — 2021-12-09
=====================

Features
--------

-   Upgrade to Globus SDK v3.

Bugfixes
--------

-   Fixes a bug in the SDK that prevented Flow updates from removing all
    flow_administrators,  flow_viewers, and flow_starters. This bug also
    prevented updates from setting text fields to empty strings.

-   Fix a bug that could allow the Flows authorizer to be lost if an exception
    was raised. (Authorizer swaps are now handled using a context manager.)

-   Support strings (and tuples/sets containing strings) as argument values
    when running, deploying, or updating an action or a flow and specifying
    a keyword argument alias like ``visible_to`` or ``runnable_by``.

Other
-----

-   Add code linting, documentation build testing, and a bunch of unit tests.
-   Add GitHub Actions to run on push and pull requests.
-   Add a pre-commit configuration file to increase overall code quality.

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
