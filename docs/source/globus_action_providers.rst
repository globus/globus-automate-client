Globus Action Providers
=======================

Globus provides and operates a number of ``Action Providers`` which may be
invoked directly or used within Flows. Below is a brief summary of the ``Action
Providers`` being operated including specific information on their URLs, scopes,
and a summary of their functionality. Specific input specifications are not
provided as they may be retrieved from the ``Action Provider`` directly via
introspection:

.. code-block:: BASH

    globus-automate action introspect --action-url <action_url>

Or simply click on the URL to view the introspection results in a browser.

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

.. literalinclude:: ../../examples/action_bodies/hello_world.json
   :language: json
   :caption: Example Input

.. literalinclude:: ../../examples/cli/run_hello_world.sh
   :language: BASH
   :caption: Try It

Globus Transfer - Transfer Data
-------------------------------

URL: `<https://actions.globus.org/transfer/transfer>`_

Scope: ``https://auth.globus.org/scopes/actions.globus.org/transfer/transfer``

Synchronous / Asynchronous: Either

The Action Provider "transfer/transfer" uses the `Globus Transfer Task API`_ to
perform a transfer of data from one Globus Collection to another. The input
includes both the source and destination collection ids and file paths
within the collection where the source file or folder is located and
the destination folder where the transfer should be placed. It also
supports indicating that transfers should be performed recursively to
traverse the entire source file system tree and allows labeling the
transfer should it be viewed directly in the Globus WebApp or via the
Globus API or CLI. The body of the action status directly reflects the
information returned when monitoring the transfer task using the
Globus Transfer API.

.. literalinclude:: ../../examples/action_bodies/transfer.json
   :language: json
   :caption: Example Input

Globus Transfer - Delete Data
-----------------------------

URL: `<https://actions.globus.org/transfer/delete>`_

Scope: ``https://auth.globus.org/scopes/actions.globus.org/transfer/delete``

Synchronous / Asynchronous: Asynchronous

Globus Transfer / delete data works much like the "Transfer /
transfer" provider. It takes a source collection and path as inputs
and uses the `Globus Transfer Task API`_ to intiate an
asynchronous delete operation. Also like the transfer operation,
labels and recursive options may be set. The status body comes
directly from the Task status in the Globus Transfer API.

Globus Transfer - Set/Manage Permissions
----------------------------------------

URL: `<https://actions.globus.org/transfer/set_permission>`_

Scope: ``https://auth.globus.org/scopes/actions.globus.org/transfer/set_permission``

Synchronous / Asynchronous: Synchronous

The set permission Action Provider uses the `Globus Transfer ACL API`_ to set or
manage permissions on a folder or file. The body of the request indicates
whether the permission rule is to be created, updated or deleted using the
``operation`` property. For update or delete, the ``rule_id`` of a previously
created permission rule must also be provided.

As the Globus Transfer API returns a status directly (rather than a
task identifier), the Action Provider behaves in a synchronous manner,
returning the Transfer API result.

.. literalinclude:: ../../examples/action_bodies/set_permission.json
   :language: json
   :caption: Example Input to Set Permissions

.. literalinclude:: ../../examples/action_bodies/delete_permission.json
   :language: json
   :caption: Example Input to Delete Permissions

.. literalinclude:: ../../examples/action_bodies/update_permission.json
   :language: json
   :caption: Example Input to Update Permissions

Globus Transfer - List Directory Contents
-----------------------------------------

URL: `<https://actions.globus.org/transfer/ls>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/transfer_ls``

Synchronous / Asynchronous: Synchronous

The Globus Transfer ls Action Provider uses the `Globus Transfer Directory API`_
to retrieve a listing of contents from an (endpoint, path) pair.
Although providing a path is optional, the default path used depends
on endpoint type and it is best to explicitly set a path. This Action
Provider supports all options as defined in the List Directory
Contents Transfer API documentation.

Additionally, it adds two features not found in the base Globus Transfer List Directory operation.

1. An input Boolean parameter ``path_only`` may be specified which indicates that regardless of the file type of the path, we only will return information about the path itself. This changes the behavior when the path references a folder. Rather than returning the *contents* of the folder, this will return information about the folder itself. Thus, when this option is present, the output will contain only one file entry.

2. For each file entry returned, an additional property, ``is_folder``, is included. This is set to ``true`` if the file type is folder. This can be helpful, particularly within Flows, to perform branching or other logic dependent on whether a path points to a folder or a regular file.

Globus Transfer - Make Directory
--------------------------------

URL: `<https://actions.globus.org/transfer/mkdir>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/transfer_mkdir``

Synchronous / Asynchronous: Synchronous

The Globus Transfer mkdir Action Provider uses the `Globus Transfer Make Directory API`_
to create a new directory on an endpoint. The input is simply the id for endpoint where the directory will be created and the path on the endpoint to the directory to be created.

.. literalinclude:: ../../examples/action_bodies/mkdir.json
   :language: json
   :caption: Example Input to Make Directory


Globus Transfer - Get Collection Information
--------------------------------------------

URL: `<https://actions.globus.org/transfer/collection_info>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/transfer_collection_info``

Synchronous / Asynchronous: Synchronous

The Globus Transfer ls Action Provider uses the `Globus Transfer Get Collection API`_
to get information about a Globus Collection. The information returned is the same as defined by the Globus Transfer API with one addition: a property ``is_managed`` will be set to ``true`` if there is a ``subscription_id`` associated with the collection, and ``false`` if not. This allows, for example, branching within a Flow (using a ``Choice`` state type) based on whether a collection/endpoint is managed under a Globus subscription.

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

.. literalinclude:: ../../examples/action_bodies/search_ingest.json
   :language: json
   :caption: Example Input

Globus Search - Delete
----------------------

URL: `<https://actions.globus.org/search/delete>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/search_delete``

Synchronous / Asynchronous: Asynchronous

Subjects or entries may be removed from an existing `Globus Search
<https://docs.globus.org/api/search/>`_ index using the Search
Delete Action Provider. The input to the Action Provider includes the
Search index id to delete the data from. The body also specifies the type of
delete operation to execute via the ``delete_by`` parameter. It's value may be
``entry`` to delete a single entry, ``subject`` to delete a subject, or
``query`` to remove data matching a `Search query
<https://docs.globus.org/api/search/entry_and_subject_ops/#delete_by_query>`_.

The user calling the Action Provider must have permission to write to the index
referenced. Globus Search will process the delete operation asynchronously, so
this Action Provider also behaves in an asynchronous fashion. Requests for the
state of an Action will lookup the state of the ``task_id`` in Globus Search,
ensuring the status remains up-to-date. Since Globus Search does not support
cancellation of tasks, this Action Provider also does not support cancellation
of its Actions.

.. literalinclude:: ../../examples/action_bodies/search_delete_by_subject.json
   :language: json
   :caption: Example Input to Delete by Subject

.. literalinclude:: ../../examples/action_bodies/search_delete_by_query.json
   :language: json
   :caption: Example Input to Delete by Query

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

.. literalinclude:: ../../examples/action_bodies/notification_email.json
   :language: json
   :caption: Example Input with Complex Templating

.. literalinclude:: ../../examples/action_bodies/email.json
   :language: json
   :caption: Example Input with Simple Formatting

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

.. literalinclude:: ../../examples/action_bodies/web_option.json
   :language: json
   :caption: Example Input for Creating Options

.. literalinclude:: ../../examples/action_bodies/web_option_landing_page.json
   :language: json
   :caption: Example Input for Creating Options on a Landing Page

.. literalinclude:: ../../examples/action_bodies/web_option_landing_page_selectable_by.json
   :language: json
   :caption: Example Input for Creating Options on a Landing Page Limiting Selection

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

.. literalinclude:: ../../examples/action_bodies/datacite.json
   :language: json
   :caption: Example Input

.. _Globus Transfer ACL API: https://docs.globus.org/api/transfer/acl/
.. _Globus Transfer Task API: https://docs.globus.org/api/transfer/task_submit/
.. _Globus Transfer Directory API: https://docs.globus.org/api/transfer/file_operations/#list_directory_contents
.. _Globus Transfer Make Directory API: https://docs.globus.org/api/transfer/file_operations/#make_directory
.. _Globus Transfer Get Collection API: https://docs.globus.org/api/transfer/endpoint/#get_endpoint_by_id


HTTP requests
-------------

URL: `<https://actions.globus.org/http>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/http``

Synchronous / Asynchronous: Synchronous

The HTTP action provider supports making HTTP requests to arbitrary URL's of your choosing.
This allows you to gather information from, or submit information to, external services.

At minimum, you must specify the HTTP method and the target URL.
Here is an example of the simplest functional input document:

..  code-block:: json

    {
        "method": "GET",
        "url": "https://httpbin.org/get"
    }

A single HTTP request can be customized in four key ways:

*   HTTP method
*   HTTP timeout
*   Content submission
*   URL customization

..  note::

    The JSON schema that authoritatively describes the accepted keys and values can be retrieved using this command:

    ..  code-block:: text

        globus-automate action introspect --action-url https://actions.globus.org/http


HTTP method
...........

..  csv-table::

    "Key name", "``method``"
    "Value type", "string"
    "Required", "True"
    "Accepted values", "``DELETE``, ``GET``, ``POST``, ``PUT``"
    "Default", "*None*"

The HTTP method determines how a URL is accessed.

Generally speaking, GET requests can only gather existing information.
POST requests create new information,
PUT requests update existing information,
and DELETE requests erase existing information.

..  code-block:: json

    {
        "method": "GET",
        "url": "https://httpbin.org/get"
    }


HTTP timeout
............

..  csv-table::

    "Key name", "``timeout``"
    "Value type", "number"
    "Required", "False"
    "Value range", "``(0, 30]``"
    "Default", "``10``"

In some cases an HTTP request may take longer than expected to respond.
You can customize the maximum length of time that a single request can take using the ``timeout`` key.

..  code-block:: json

    {
        "method": "GET",
        "url": "https://domain.example/lengthy-calculation",
        "timeout": 30
    }


Content submission
..................

..  csv-table::

    "Key name", "``content``"
    "Value type", "a JSON object"
    "Required", "False"
    "Default", "*None*"

If you need to submit data to a URL, use the ``content`` key.
This can be used for all HTTP methods except GET requests.

..  code-block:: json

    {
        "method": "POST",
        "url": "https://httpbin.org/post",
        "content": {
            "example-id": "123",
            "values": [3, 5, 7]
        }
    }

Content will be submitted directly as JSON, but you can customize this using the ``content-type`` key.


Content type
............

..  csv-table::

    "Key name", "``content-type``"
    "Value type", "string"
    "Required", "False"
    "Accepted values", "``application/json``, ``application/x-www-form-urlencoded``"
    "Default", "``application/json``"

While content will be submitted as JSON data by default, some servers may expect data to be URL-encoded.
Here is an example of how these two content types appear when submitted to a server:

..  code-block:: http

    POST /example HTTP/1.1
    Content-Type: application/json

    {"dataset": "123", "status": "running"}

..  code-block:: http

    POST /example HTTP/1.1
    Content-Type: application/x-www-form-urlencoded

    dataset=123&status=running

Set the ``content-type`` if required by the service you are submitting content to.

..  code-block:: json

    {
        "method": "POST",
        "url": "https://httpbin.org/post",
        "content": {"dataset": "123", "status": "running"},
        "content-type": "application/x-www-form-urlencoded"
    }


Query parameters
................

..  csv-table::

    "Key name", "``query-parameters``"
    "Value type", "JSON keys and values"
    "Required", "False"
    "Default", "*None*"

Some HTTP endpoints require query parameters at the end of the URL.
If the query parameters never change you can specify them directly in the URL:

..  code-block:: json

    {
        "method": "GET",
        "url": "https://domain.example/datasets?geo=AMER&date=2021-01-17"
    }

However, the query parameters can also be specified in the input document.
This allows you to dynamically construct the query parameters using information generated or retrieved in the context of a larger Globus Flow.
For example:

..  code-block:: json

    {
        "method": "GET",
        "url": "https://domain.example/datasets",
        "query-parameters": {
            "geo": "AMER",
            "date": "2021-01-17"
        }
    }


URL substitutions
.................

..  csv-table::

    "Key name", "``url-substitutions``"
    "Value type", "JSON keys and values"
    "Required", "False"
    "Default", "*None*"

Some HTTP endpoints require a customized URL hierarchy.
For example, the URL may require an ID to be embedded in the path:

..  code-block:: text

    https://domain.example/dataset/37/status/42/info

When this is required you can specify substitution identifiers in the ``url``
and dynamically provide the correct values in the input document.

Substitution identifiers in the URL are wrapped in curly braces like "``{id}``".
You can specify multiple substitution identifiers, and identifiers can be repeated.
Each identifier MUST be referenced as a key in the ``url-substitutions`` object.

If identifiers are specified in the URL but are not provided in the ``url-substitutions`` object an error will be returned.
Similarly, if identifier values are provided in ``url-substitutions`` but are not required then this will also be treated as an error.

The input document below will result in the same URL as the example above,
but the dataset ID and the status ID can now be dynamically specified during Flow execution.

..  code-block:: json

    {
        "method": "GET",
        "url": "https://domain.example/dataset/{dataset-id}/status/{status-id}/info",
        "url-substitutions": {
            "dataset-id": "37",
            "status-id": "42"
        }
    }

This feature can be combined with dynamic query parameters, too.

..  note::

    To support this feature, bare curly braces cannot appear in a URL.
    If you need to have bare curly braces in the URL you can escape them using URL substitution:

    ..  code-block:: json

        {
            "method": "GET",
            "url": "https://domain.example/{open-brace}success{close-brace}/",
            "url-substitutions": {
                "open-brace": "{",
                "close-brace": "}"
            }
        }

    This will result in the following URL with curly braces embedded:

    ..  code-block:: text

        https://domain.example/{success}/


Errors: JSON schema validation
..............................

Input documents will be validated against the HTTP action provider JSON schema.
You can get an authoritative copy of the JSON schema by running this command:

..  code-block:: text

    globus-automate action introspect --action-url https://actions.globus.org/http

If the JSON schema validation fails the HTTP provider will return a JSON document with a list of errors.
For example, if the ``method`` is not one of the supported values you will see an error like this:

..  code-block:: json

    {
        "code": "BadActionRequest",
        "description": [
            "'method' invalid due to 'GATHER' is not one of ['DELETE', 'GET', 'POST', 'PUT']"
        ]
    }

If you encounter a ``BadActionRequest`` it is possible that the input document contains a typo or a missing key.


Errors: Additional input documentation validation
.................................................

Additional validation of the input document will be performed before submitting the HTTP request.
These errors may be returned in the result document:

``HTTP_URL_SUBSTITUTION_EMPTY_ID``
    All URL substitution identifiers must have at least one character.

    If this error is encountered it means that an empty identifier was encountered in the ``url`` key.
    An empty identifier is two curly braces next to each other: "``{}``".

    If literal curly braces must appear in the URL,
    please see the section above titled "URL substitutions" for a workaround.

    If a value is required at that location in the URL, give the identifier a name using at least one character.
    Otherwise, remove the curly braces from the URL.

``HTTP_URL_SUBSTITUTION_ID_UNFILLED``
    All substitution identifiers in ``url`` must have values specified in ``url-substitutions``.

    If this error is encountered it means that one or more identifiers do not have values.
    For example, the following URL contains two identifiers (``dataset-id`` and ``status-id``)
    but only one value (``dataset-id``) is provided in ``url-substitutions``:

    ..  code-block:: json

        {
            "method": "GET",
            "url": "https://domain.example/{dataset-id}/{status-id}",
            "url-substitutions": {
                "dataset-id": "123"
            }
        }

    To fix this error, provide a value for each substitution identifier that appears in ``url``.

``HTTP_URL_SUBSTITUTION_ID_UNKNOWN``
    All substitution values in ``url-substitutions`` must be required in ``url``.

    If you see this error it means that one or more values would be unused in the ``url``.
    For example, the following URL contains one identifier (``dataset-id``)
    but two values (``dataset-id`` and ``status-id``) are provided in ``url-substitutions``:

    ..  code-block:: json

        {
            "method": "GET",
            "url": "https://domain.example/{dataset-id}",
            "url-substitutions": {
                "dataset-id": "123",
                "status-id": "unused"
            }
        }

    To fix this error, only provide values for each substitution identifier that appears in ``url``.

``HTTP_METHOD_DOES_NOT_SUPPORT_CONTENT``
    The HTTP specification does not allow content to be submitted with GET requests.

    If you see this error it means that the input document specifies "``GET``" as the HTTP method but also specifies a ``content`` key.
    This is an incompatible combination.

    If you are attempting to submit data to the specified URL you must use a different HTTP method, like "``POST``" or "``PUT``".

    If you are only attempting to retrieve data from the specified URL, remove the ``content`` key from the input document.


Errors: HTTP request or response failures
.........................................

``HTTP_REQUEST_FAILED``
    The HTTP request was submitted but failed for some reason.

    This error can happen for many reasons.
    For example, you may see this error if the ``url`` contains a typo,
    or if the ``url`` refers to an internal server that cannot be reached from the outside internet,
    or if the server doesn't respond before the ``timeout`` value is reached.

    The text of the failure is included in the error message and can help troubleshoot why the request failed.

``HTTP_RESPONSE_NOT_JSON``
    At this time, all HTTP requests must return valid JSON.

    If you see this error it means that the server responded with something other than valid JSON.
