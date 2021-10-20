Globus Automate Overview
========================

The Globus Automate platform provides tools and services which can be used to
create reliable processes for research data management. The platform builds on the
foundation of Globus capabilities such as Authorization and Data Transfer.

The
Automate Platform introduces a few key concepts which may then be extended and
combined to create custom processes solving particular research data management
problems. These concepts are ``Action Providers``, ``Actions``, and ``Flows``.
Read on to learn about how ``Flows`` orchestrate ``Action Providers`` together
in order to create ``Actions`` that perform the actual automation.

Use Cases
---------

The key to the platform is enabling users to orchestrate multiple processing
steps into a single workflow, or ``Flow``. Some of these steps are provided by
``Globus Automate`` and othes of which may be custom implementations supporting
a specific need. Examples of these workflows might be:

- Automatically detect data output from scientific instruments which is then
  transferred, processed, and indexed.
- Provide a curated pipeline for description, annotation and publication of
  research datasets.
- Run data transfers on a recurring schedule.


Action Providers
----------------

An ``Action Provider`` is an HTTP accessible service which acts as a single step
in a process and implements the ``Action Provider Interface``. When
an ``Action Provider`` is invoked, it creates (or "provides") an ``Action``
which represents a single unit of work. Examples of units of work are running a
file transfer using ``Globus Transfer`` or ingesting data into ``Globus
Search``.

Each ``Action Provider`` expects to be invoked with parameters
particular to the service it provides. To support usability and discovery, each
can be introspected to determine what its ``input schema`` or input properties
are. Introspection also provides information such as who operates the ``Action
Provider``, descriptive text on the service it provides, and who can use the
service. Access to ``Action Providers`` and their invocation is controlled via
``Globus Auth``. Some of these services may be *synchronous* meaning that an
invocation will complete in the context of the HTTP request that triggered it.
Other services support *asynchronous* activities, meaning that the invocation
will persist beyond the HTTP request that invoked it and the the caller must
monitor the ``Action`` for updates on when it is completed and its result.

Globus operates a series of these ``Action Providers`` available for
public use.  For a full list of these ``Action Providers``, see
`section Globus Action Providers
<globus_action_providers.html>`_. Globus also supports users writing
their own ``Action Providers`` via the `Globus Action Provider Toolkit
<https://action-provider-tools.readthedocs.io/en/latest/>`_ - a Python
SDK that makes it easy to provide custom services that can be tied
into the ``Globus Automate`` ecosystem of services.

These ``Action Providers`` form the foundation of  ``Globus Automate`` and are
primarily used by referencing their URLs in `Flows`_.
``Globus Automate`` allows users to flexibly piece together these individual
services to create reliable high level workflows.


Actions
-------

An ``Action`` represents a single, discrete invocation of an ``Action
Provider``. It is record of an operation and includes details for its result,
its current execution status, and metadata dictating which ``Globus Auth``
identities are allowed to read or modify the ``Action``'s state. ``Globus
Automate`` services allow orchestrating these individual ``Actions`` into robust
processes that can tolerate their distinct execution states, including success
and failure. Users will not often need to operate on ``Actions`` directly,
rather, the User will create a ``Run`` of a ``Flow`` and the ``Run`` will invoke
``Action Providers``, creating ``Actions`` as necessary to accomplish the
automation.

Flows
-----

A ``Flow`` represents a single process that orchestrates a series of services
into a self contained operation. One can think of a ``Flow`` as a
declaratively defined ordering of ``Action Providers`` with condition handling
to define expected success or failure scenarios.

A ``Flow`` may be defined and deployed to the ``Flows`` service by any user.
When deploying, the user may control which other users can discover the ``Flow``
and separately, which users can run the ``Flow``. All access control is provided
by ``Globus Auth``. Thus, ``Flows`` can easily and safely be shared among users.
Once deployed, the ``Flow`` will receive a HTTP-accessible ``Flow`` URL which
makes it available for use in ``Globus Automate``.

It may also be interesting to note that once deployed, the ``Flow`` will
implement the ``Action Provider Interface``. What this means is that a ``Flow``
is technically a form of ``Action Provider``, and as such it can be referenced
by other ``Flows`` by its ``Flow`` URL. This allows for modularity in defining
``Flows`` and in a separation of concerns where ``SubFlows`` can be trusted to
provide some process or behavior.

When users run an instance of the ``Flow``, we call that a ``Run``. A
``Run`` shares the ``Action`` interface, supporting operations such as viewing
its status, cancelling its execution, and removing its execution state. This
allows for common tooling and terminology for working with ``Runs`` and
``Actions``.  In general, any operation available on an ``Action`` will be
possible on a ``Run`` and vice versa.

``Globus Automate`` imposes no restrictions on how long a ``Run`` may execute or
on the number of units of work defined in a ``Flow``. We support long running
``Runs`` by providing support for monitoring and status updates.

Authentication and Authorization
--------------------------------

An important consideration in the ``Globus Automate`` platform is authentication
and authorization. All interactions with ``Action Providers`` ``Actions`` and
``Flows`` are authenticated by ``Globus Auth``.

For ``Action Providers`` and ``Flows``, authorization lists exist to control
which identities can view its details and which identities can invoke an
``Action`` or ``Run`` of a Flow in the service. For ``Actions`` and ``Runs``,
authorization lists exist to enforce which identities may view its execution
details and which identities may modify the execution status. For these
authorization lists, identities may be specified as individual Globus users or
as Globus Groups. Thus, while the ``Globus Automate`` platform is open to all
users with access, it is possible to carefully control which users have access
to your resources.

The authorization lists for a Flow definition are as follows:

- ``flow_viewers``: Users who are allowed to see that the Flow is present in the system. Users not in the list will have no way of becoming aware that the Flow exists.

- ``flow_starters``: Users who are allowed to start a particular Flow running. If not present in this list, a user attempting to start a Flow will receive an error.

- ``flow_administrators``: Users who can administer a flow, most notably updating the Flow's execution instructions (its "definition") or other meta-data about the Flow.

- ``flow_owner``: A single user who is considered the user with primary responsibility for maintaining the Flow. Users in the ``flow_administrators`` list may transfer ownership to themselves via a Flow update operation.

Once a Flow has been started, a "run" object is created for monitoring and managing the particular run. Authorization lists are created to determine which users may perform these operations as follows:

- ``run_monitors``: These users may request the current state of the Flow run seeing what steps of the Flow have been executed, what the inputs and outputs of the various steps have been and see whether it has completed or not.

- ``run_managers``: These users may also perform operations which alter the run of the Flow or its state. In particular, they may request that the run be canceled or they may remove the state for a completed run.

- ``run_owner``: This is the user who initiated the run of the Flow. Unlike a ``flow_owner`` this role cannot be transferred to another user. The ``run_owner`` can perform the same operations as a user in the ``run_managers`` list.

For both Flows and Flow runs, the authorization lists are "cumulative"
in the sense that a user in a particular list (termed having that
"role") may also perform all the operations of users in the roles
listed prior to it in the list. Thus, for example, a user in the
``flow_administrators`` list can perform all the operations associated
with those in the ``flow_viewers`` and the ``flow_starters``
lists. Similarly, a user in ``run_managers`` can do all that those in
``run_monitors`` can.

Values within the authorization lists take the form of urns
specifying individual users or groups of users based on Globus Groups. When
specifying a user in an authorization list, the principal value
will be the user's UUID prefixed with ``urn:globus:auth:identity:``. When
specifying a Globus Group in the list, the principal value needs to be the
Group's UUID prefixed with ``urn:globus:groups:id:``.

.. tip::

    To determine a Globus user's ID, you can use the `globus` CLI:

    .. code:: BASH

        globus get-identities username@globus.org

    To determine the Globus Group's ID, you can search for the Group in the
    `Globus Web Application <https://app.globus.org/groups>`_.

Two special values, ``public`` and ``all_authenticated_users`` may
also be used in some authorization lists. ``public`` indicates that
the operation is allowed for requests that have no authorization and
may be used in the ``flow_viewers`` list, and
``all_authenticated_users`` indicates that any user who presents a
``Globus Auth`` credential in the form of an access token is permitted
access and may be used in a ``flow_starters`` list.
