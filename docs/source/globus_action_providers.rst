.. _globus_action_providers:

Globus Operated Action Providers
================================

Globus provides and operates a number of Action Providers which may be invoked
directly, or may be used within Flows. Below is a brief summary of the Action
Providers being operated including specific information on their URLs and a
summary of their functionality. Specific input specifications are not provided
as they may be retrieved from the Action Provider directly via introspection:

.. code-block:: BASH

    globus-automate action introspect --action-url <action_url>


.. note::
    The ``action_url`` used specifies the target Action Provider and is provided
    in this documentation.

.. note::
    When running Globus operated Action Providers the ``action`` subcommands
    do not require the use of the ``--action-scope`` option as these Action
    Providers are publicly visible. If interacting with a non-publicly visible
    Provider, all ``action`` subcommands will require the ``--action-scope``
    option followed with the Action Provider's corresponding scope value.

List of Globus Operated Action Providers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

HelloWorld
----------

URL: `<https://actions.globus.org/hello_world>`_

Scope: ``https://auth.globus.org/scopes/actions.globus.org/hello_world``

Synchronous / Asynchronous: Either

The HelloWorld Action Provider is very simple and is primarily intended for
testing and bootstrapping purposes. It can operate in either synchronous or
asynchronous modes. In the synchronous mode, only a single string is sent in the
body and the response will return containing a constant value (``"Hello":
"World"``) and a reply to the input (``"hello": "<input string>"``).  To get
asynchronous operation, the value ``sleep_time`` should be included in the input
with a value of a number of seconds the Action should take to complete.
Subsequent invocations of ``/status`` will return the state ``ACTIVE`` until the
number of seconds indicated in ``sleep_time`` have elapsed at which point the
status will become ``SUCCEEDED``.


Globus Transfer - Transfer Data
-------------------------------


URL: `<https://actions.globus.org/transfer/transfer>`_

Scope: ``https://auth.globus.org/scopes/actions.globus.org/transfer/transfer``

Synchronous / Asynchronous: Either

The Action Provider "transfer/transfer" uses the `Globus Transfer API
<https://docs.globus.org/api/transfer/task_submit/>`_ to perform a
transfer of data from one Globus Collection to another. The input
includes both the source and destination collection ids and file paths
within the collection where the source file or folder is located and
the destination folder where the transfer should be placed. It also
supports indicating that transfers should be performed recursively to
traverse the entire source file system tree and allows labeling the
transfer should it be viewed directly in the Globus WebApp or via the
Globus API or CLI. The body of the action status directly reflects the
information returned when monitoring the transfer task using the
Globus Transfer API.

Globus Transfer - Delete Data
-----------------------------

URL: `<https://actions.globus.org/transfer/delete>`_

Scope: ``https://auth.globus.org/scopes/actions.globus.org/transfer/delete``

Synchronous / Asynchronous: Asynchronous

Globus Transfer / delete data works much like the "Transfer /
transfer" provider. It takes a source collection and path as inputs
and uses the `Globus Transfer API
<https://docs.globus.org/api/transfer/task_submit/>`_ to intiate an
asynchronous delete operation. Also like the transfer operation,
labels and recursive options may be set. The status body comes
directly from the Task status in the Globus Transfer API.

Globus Transfer - Set Permission
--------------------------------

URL: `<https://actions.globus.org/transfer/set_permission>`_

Scope: ``https://auth.globus.org/scopes/actions.globus.org/transfer/set_permission``

Synchronous / Asynchronous: Synchronous

The set permission Action Provider uses the `Globus Transfer API
<https://docs.globus.org/api/transfer/acl/>`_ to set permissions on a
folder or file. As the Globus Transfer API returns a status directly
(rather than a task identifier), the Action Provider behaves in a
synchronous manner, returning the Transfer API result.

Globus Transfer - List Directory Contents
-----------------------------------------

URL: `<https://actions.globus.org/transfer/ls>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/transfer_ls``

Synchronous / Asynchronous: Synchronous

The Globus Transfer ls Action Provider uses the `Globus Transfer API
<https://docs.globus.org/api/transfer/file_operations/#list_directory_contents>`_
to retrieve a listing of contents from an (endpoint, path) pair.
Although providing a path is optional, the default path used depends
on endpoint type and it is best to explicitly set a path. This Action
Provider supports all options as defined in the List Directory
Contents Transfer API documentation.

Globus Search - Ingest
----------------------

URL: `<https://actions.globus.org/search/ingest>`_

Scope: ``https://auth.globus.org/scopes/actions.globus.org/search/ingest``

Synchronous / Asynchronous: Asynchronous

Records may be added to an existing `Globus Search
<https://docs.globus.org/api/search/>`_ index using the Search /
ingest Action Provider. The input to the Action Provider includes the
id of the Search index to be added to and the data, in the
Search-defined ``GMetaEntry`` format. The user calling the Action
Provider must have permission to write to the index referenced. Globus
Search will process the ingest operation asynchronously, so this
Action Provider also behaves in an asynchronous fashion: requests to
update the state of an Action will reflect the result from updating
the state of the ingest task in Globus Search. Since Globus Search
does not support cancellation of tasks, this Action Provider also does
not support cancellation of its Actions.

Send Notification - Email
-------------------------

URL: `<https://actions.globus.org/notification/notify>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/notification_notify``

Synchronous / Asynchronous: Synchronous

The Send notification / email Action Provider presently supports sending of
email messages to a set of email addresses. The request to send the email
contains the standard components of an email: sender, receiver(s), subject and
body. The mimetype of the body may be specified so that either HTML or text
formatted messages may be sent. The body also supports the notion of variable
substitution or "templating." Values in the body may be specified with a dollar
sign prefix ($), and when values are provided in the ``body_variables`` property
of the request, the template value will be substituted with the corresponding
value from the ``body_variables``.

The other important component of the request to this action provider is the
email sending credentials. Credentials are provided to allow the provider to
communicate with the service used for sending the email. Presently, two modes of
sending email are supported: SMTP and AWS SES. When SMTP is provided, the
username, password and server hostname are required. When AWS SES is provided,
the AWS access key, AWS access key secret and the AWS region must be provided.
As this service is synchronous and stateless, the requester can be assured that
these credentials will not be stored. The Action Provider will return success as
long as the email service accepts the message. It cannot guarantee successful
delivery of the message including an inability to deliver the message due to an
improper recipient address.

Wait for User Option Selection
------------------------------

URL: `<https://actions.globus.org/weboption/wait_for_option>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/weboption_wait_for_option``

Synchronous / Asynchronous: Asynchronous

Flows or other clients which desire to provide users a method of selecting an
option from a fixed set may use the Wait for User Option Selection Action
Provider. The Action Provider can operate in one of two modes.

In the first mode, a list of options are created which are automatically
selected by any access to a corresponding URLs. For each option, a name, a URL
suffix, and a message or text which is returned in the HTTP response of the
selection operation is provided. The URL suffix is registered with the Action
Provider and is monitored at the URL
``https://actions.globus.org/weboption/option/<url_suffix>``. Any HTTP access to
the URL is considered a selection of that option among all the options defined
by the input to the Action and the Action will transition to a ``SUCCEEDED``
status. Each of the options may be protected for access only via specific Globus
identities by setting values on the ``selectable_by`` list. A direct HTTP access
may present a Bearer token for authorization using the same scope as used for
accessing the other operations on the Action Provider. If no access token is
presented, the user will be re-directed to start an OAuth Flow using Globus Auth
to authenticate access to the option URL.

In the second mode, in addition to monitoring the provided URL suffixes, a
landing page may be hosted which will present the options to a user on a simple
web page. The web page may be "skinned" with options for banner text, color
scheme and icon as well as introductory text presented above the options. The
options are specified in the same manner as in the first mode, but the page
presents links which ease selection of those options for end-users. The landing
page is also given a URL suffix, and the selection page will be present at
``https://actions.globus.org/weboption/landing_page/<url_suffix>``. Selection of
an option within the landing page behaves the same as direct selection of an
option via its URL as described above. Similar to individual options, the
landing page can be protected by setting a ``selectable_by`` list. As the
landing page is intended for use via a browser, it will always start a OAuth
Flow to authenticate the user. If ``selectable_by`` is set on the landing page
but not on any of the individual options, the options inherit the same
``selectable_by`` value defined on the landing page for that Action.

In either mode, once an option has been selected, none of the url suffixes, nor
the landing page if configured, in the initial request, will be responded to by
the Action Provider: they will return the HTTP not found (error) status 404.
Upon completion, the body of the status will include the name and the url suffix
for the selected option. The body may also include input on the HTTP data passed
when the option's URL was accessed including the query parameters and the body.
To include those in the status, flags are set on the definition of the option.


Simple Expression Evaluation
----------------------------

.. note::
    Expression Evaluation has been integrated with Action definitions directly
    (see section :ref:`flow_action_expressions`). Thus, for most use cases, the
    Simple Expression Evaluation Action Provider described here is not needed
    and expressions defined on Action definitions within a Flow are preferred.

URL: `<https://actions.globus.org/expression_eval>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/expression``

Synchronous / Asynchronous: Synchronous

Evaluation of simple expressions is supported using the `simpleeval
<https://github.com/danthedeckie/simpleeval>`_ library and therefore syntax. A
single invocation of the Action Provider may evaluate a single expression or
multiple expressions. An Expression request consists of up to three parts:

* | An ``expression`` (required) which is a basic "arithmetic" type expression.
   This *does* include string type operations so an expression like "foo" + "bar"
   is permitted and performs string concatenation as is common in many programming
   and scripting languages.

* | A set of ``arguments`` (optional) in a JSON object format. These arguments
    may be referenced in an expression. So, if there's an expression such as "x +
    1" and the arguments contain ``{"x": 2}`` the result will be ``3``.

* | A ``result_path`` (optional) which is a path where the result will be
    stored. It may be in "Reference Path" format as defined in the AWS Step
    Functions State Machine Language specification or it may simply be a dot
    separated string of the path elements. In either case, the path indidcates where
    in the ``details`` of the returned action status the value for the evaluated
    expression should be placed. If ``result_path`` is not present, the result will
    be stored in the ``details`` under the key ``result``.

A single request may specify multiple expressions to be evaluated by providing
an array named ``expressions`` as in ``{"expressions": [{ expression1 },
{expression2}, ...]}`` where each of the expressions ``expression1`` and
``expression2`` contains the three fields defined for an expression. These will
be evaluated in order, and expressions using the same ``result_path`` will
result in previous results being over-written.


Datacite DOI Minting
--------------------

URL: `<https://actions.globus.org/datacite/mint/basic_auth>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/datacite_mint_basic_auth_action_all``

Synchronous / Asynchronous: Synchronous

The Datacite DOI Minting action provider uses the `Datacite JSON API
<https://support.datacite.org/docs/api-create-dois>`_ to mint DOIs. The main
part of the body input is as specified in that API. The additional fields
provide the username and password (the "Basic Auth" credentials which is part of
the name of the URL and scope string) as well as a flag indicating whether it
should be used in the Datacite test service or the production service.

Example Input:

.. code-block:: JSON

    {
      "as_test": true,
      "username": "<A Datacite Username>",
      "password": "<A Datacite Password>",
      "Doi": {
        "id": "10.80206/ap_test",
        "type": "dois",
        "attributes": {
          "doi": "10.80206/ap_test",
          "creators": [{"name":"Globus Dev Team"}],
          "titles": [
            {"title": "Test Title"}
          ],
          "publisher": "Globus",
          "publicationYear": "2020"
        }
      }
    }
