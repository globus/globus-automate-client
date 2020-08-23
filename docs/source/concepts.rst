Introduction and Concepts
=========================

The Globus Automate platform provides tools, services and processes for creating reliable, customizable processes for research data management building on the foundation of Globus capabilities such as Authorization and Data Transfer. The Automate Platform introduces a few key concepts which may then be extended and combined for creating custom processes solving particular research data management problems.

Examples of typical scenarios include automatically detecting, transferring, processing and indexing data output from scientific instruments, or providing a curated pipeline for description, annotation and publication of research datasets. In these, or in any number of other scenarios, the key to the platform is enabling users to leverage multiple processing steps, some provided by the platform, and some which may require custom development, in a manner which satisfies their particular needs, and which are then operated with the degree of availability required for production use.

To provide this capability, the Automate platform defines a small number of inter-related, key concepts which are combined to achieve users' goals. These concepts are described briefly below.

Actions
-------

Actions make up the individual units of work upon which Automate processes are built. Many Actions are provided by Automate to allow common operations, including those provided by the Globus service. Actions are defined by a common REST/HTTP programming interface allowing users to extend the set of available capability to satisfy their needs. We `provide tooling <https://action-provider-tools.readthedocs.io/en/latest/>`_ to help users build these Actions.

As we will see in later sections, Actions can be invoked directly when needed, but they can also be combined to form Flows.

.. _flows_concept:

Flows
-----

Flows define a combination of Actions and other processing steps into more complicated, and useful operations. The method of defining a flow is "declarative" requiring a user to define the Actions and conditions upon which the flow should proceed. This approach is intended to be easier than other automation approaches which are more "programmatic" such as Python or Shell scripts.

Flows may be defined by any user and deployed to the Flows service. Once deployed, a Flow may be invoked by the creator and be discovered and invoked by other, authorized users. Thus, flows are easily and safely shared among users. Operationally, Flows behave like other Actions which allows both common tooling for executing and monitoring Flows and Actions. This also allows Flows to make use of other Flows, leading to good separation of concerns and an environment in which users may make further use of contributions from other users.

Flows by their very nature are expected to be long running and may control and monitor a complex sequence of steps. As the Flows are run by the Flow service, a user need not provide any hosting or any other platform to keep a Flow running and making forward progress. This intrinsic hosting, and monitoring of Flows again makes creating automation processes easier because a user who defines the process need not also create and maintain a resource, such as a physical or virtual server, to keep the process running.


.. _auth:

Authentication and Authorization
--------------------------------

An important consideration in the Globus Automate platform is authentication and authorization. All interactions between Automate Actions or Flows are authenticated via the `Globus Auth <https://docs.globus.org/api/auth/>`_ system. Authorization lists are defined by Actions and by users who create Flows controlling who can discover their existence, perform and monitor operations running on them. Thus, while the Automate platform is open to all users who have access to any form of Globus resource, users of Automate can carefully control which other users are sharing their activities.

When authorization lists are in place, the values take the form of urns specifying individual users or groups of users based on the Globus Groups system. Two special values, ``public`` and ``all_authenticated_usrs`` may also be used. ``public`` indicates that the operation is allowed for requests that have no authorization, and ``all_authenticated_users`` indicates that any user who presents a Globus Auth credential, in the form of an access token is permitted.
