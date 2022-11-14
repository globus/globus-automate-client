Globus Automation Overview
==========================

The Globus automation platform provides tools and services which can be used to
create reliable, easily-repeatable processes for research data management.
The platform builds on key Globus services like Authorization and Data Transfer.

The automation platform introduces a few key concepts which may then be extended and
combined to create custom processes solving particular research data management
problems. These concepts are *action providers*, *actions*, and *flows*.
Read on to learn about how flows can orchestrate action providers together
in order to create actions that perform the actual automation.

Use Cases
---------

The key to the platform is enabling users to orchestrate multiple processing
steps into a single workflow, or *flow*. Some of these steps are provided by
Globus and others of which may be custom implementations supporting
a specific need. Examples of these workflows might be:

- Automatically detect data output from scientific instruments which is then
  transferred, processed, and indexed.
- Provide a curated pipeline for description, annotation and publication of
  research datasets.
- Run data transfers on a recurring schedule.


Action Providers
----------------

An *action provider* is an HTTP accessible service which acts as a single step
in a process and implements the action provider interface. When
an action provider is invoked, it creates (or "provides") an action
which represents a single unit of work. Examples of units of work are running a
file transfer using *Globus Transfer* or ingesting data into *Globus
Search*.

Each action provider expects to be invoked with parameters
particular to the service it provides. To support usability and discovery, each
can be introspected to determine what its ``input schema`` or input properties
are. Introspection also provides information such as who operates the action
provider, descriptive text on the service it provides, and who can use the
service. Access to action providers and their invocation is controlled via
*Globus Auth*. Some of these services may be *synchronous* meaning that an
invocation will complete in the context of the HTTP request that triggered it.
Other services support *asynchronous* activities, meaning that the invocation
will persist beyond the HTTP request that invoked it and the caller must
monitor the action for updates on when it is completed and its result.

Globus operates a series of these action providers available for
public use.  For a full list of these action providers, see
`section Globus Action Providers
<globus_action_providers.html>`_. Globus also supports users writing
their own action providers via the `Globus Action Provider Toolkit
<https://action-provider-tools.readthedocs.io/en/latest/>`_ - a Python
SDK that makes it easy to provide custom services that can be tied
into the Globus automation ecosystem.

These action providers form the foundation of the Globus automation ecosystem
and are primarily used by referencing their URLs in `Flows`_.
*Globus Flows* allows users to flexibly piece together these individual
services to create reliable high level workflows.


Actions
-------

An *action* represents a single, discrete invocation of an action
provider. It is record of an operation and includes details for its result,
its current execution status, and metadata dictating which *Globus Auth*
identities are allowed to read or modify the action's state. *Globus Flows*
allows orchestrating these individual actions into robust
processes that can tolerate their distinct execution states, including success
and failure. Users will not often need to operate on actions directly,
rather, the User will start a run of a flow and the run will invoke
action providers, creating actions as necessary to accomplish the
automation.


..  _Flows:

Flows
-----

A *flow* represents a single process that orchestrates a series of services
into a self contained operation. One can think of a flow as a
declaratively defined ordering of action providers with condition handling
to define expected success or failure scenarios.

A flow may be defined and deployed to the *Globus Flows* service by any user.
When deploying, the user may control which other users can discover the flow
and separately, which users can run the flow. All access control is provided
by *Globus Auth*. Thus, flows can easily and safely be shared among users.

It may also be interesting to note that once deployed, the flow will
implement the action provider interface. What this means is that a flow
is technically a form of action provider, and as such it can be referenced
by other flows by its flow URL. This allows for modularity in defining
flows and in a separation of concerns where "sub-flows" can be trusted to
provide some process or behavior.

When users start a flow, we call that a *run*. A
run shares the action interface, supporting operations such as viewing
its status, cancelling its execution, and removing its execution state. This
allows for common tooling and terminology for working with runs and
actions.  In general, any operation available on an action will be
possible on a run and vice versa.

*Globus Flows* imposes no restrictions on how long a run may execute or
on the number of units of work defined in a flow. We support long-lived
runs by providing monitoring and status updates.

Authentication and Authorization
--------------------------------

An important consideration in the Globus automation platform is authentication
and authorization. All interactions with action providers, actions, and
flows are authenticated by *Globus Auth*.

For action providers and flows, authorization lists exist to control
which identities can view its details and which identities can invoke an
action or run of a Flow in the service. For actions and runs,
authorization lists exist to enforce which identities may view its execution
details and which identities may modify the execution status. For these
authorization lists, identities may be specified as individual Globus users or
as Globus Groups. Thus, while the Globus automation platform is open to all
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

For both flows and runs, the authorization lists are "cumulative"
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
