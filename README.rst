Globus SDK and CLI for Automate
===============================

This is an experimental, and unsupported interface for working with Globus Automate tools, notably the Globus Flows service and any service implementing the Action Provider interface.

As this is experimental, no support is implied or provided for any sort of use of this package. It is published for ease of distribution among those planning to use it for its intended, experimental, purpose.

Basic Usage
-----------

Install with ``pip install globus-automate-client``

This will install both a command-line tool ``globus-automate`` and a client library for interacting with Actions and FLows. Running the script without parameters will provide a summary of its functionality.

Use of the script to invoke any services requires authentication. Upon first interaction with any Action Provider or the Flows Service, you will be prompted to proceed through an Authentication process using Globus Auth to consent for use by the CLI with the service it is interacting with. This typically only needs to be done once, the first time a service is invoked. Subsequently, the cached authentication information will be used. Authentication information is cached in the file ``$HOME/.globus_token_cache``. It is recommended that this file be protected. If re-authentication or re-consent is needed, the file may be deleted. This will remove consents to **all** Action Providers and the Flows service. The file is in JSON format with keys based on the "scope". It may be edited to remove particular scopes if done with care.




Summary of Globus Operated Action Providers
===========================================

Globus provides and operates a number of Action Providers which may be invoked directly, or may be used within Flows. Below is a brief summary of the Action Providers being operated including specific information on their URLs and Globus Auth Scopes and a summary of their functionality. Specific input specifications are not provided as they may be retrieved from the Action Provider directly using, for example, the command:

.. code-block:: BASH

    globus-automate action-provider-introspect --action-url <action_url>


where the ``action_url`` is as provided in this documentation. When running the ``action-provider-introspect`` command with the Globus operated action providers, it is not necessary to include the scope, and the scope will be part of returned information in the property ``globus_auth_scope``.


The Action Providers include:

HelloWorld
----------

URL: `<https://actions.globus.org/hello_world>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/hello_world``

Synchronous / Asynchronous: Either

The HelloWorld Action Provider is very simple and is primarily intended for testing and bootstrapping purposes. It can operate in either synchronous or asynchronous modes. In the synchronous mode, only a single string is sent in the body and the response will return containing a constant value (``"Hello": "World"``) and a reply to the input (``"hello": "<input string>"``). To get asynchronous operation, the value ``sleep_time`` should be included in the input with a value of a number of seconds the Action should take to complete. Subsequent invocations of ``/status`` will return the state ``ACTIVE`` until the number of seconds indicated in ``sleep_time`` have elapsed at which point the status will become ``SUCCEEDED``.


Globus Transfer / transfer data
-------------------------------


URL: `<https://actions.globus.org/transfer/transfer>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/transfer/transfer``

Synchronous / Asynchronous: Either

The Action Provider "transfer/transfer" uses the Globus Transfer API to perform a transfer of data from one Globus Collection to another. The input includes both the source and destination collection ids and file paths within the collection where the source file or folder is located and the destination folder where the transfer should be placed. It also supports indicating that transfers should be performed recursively to traverse the entire source file system tree and allows labeling the transfer should it be viewed directly in the Globus WebApp or via the Globus API or CLI. The body of the action status directly reflects the information returned when monitoring the transfer task using the Globus Transfer API.

Globus Transfer / delete data
-----------------------------

URL: `<https://actions.globus.org/transfer/delete>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/transfer/delete``

Synchronous / Asynchronous: Asynchronous

Globus Transfer / delete data works much like the "Transfer / transfer" provider. It takes a source collection and path as inputs and uses the Globus Transfer API to intiate an asynchronous delete operation. Also like the transfer operation, labels and recursive options may be set. The status body comes directly from the Task status in the Globus Transfer API.

Globus Transfer / set permission
--------------------------------

URL: `<https://actions.globus.org/transfer/set_permission>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/transfer/set_permission``

Synchronous / Asynchronous: Synchronous

The set permission Action Provider uses the Globus Transfer API to set permissions on a folder or file. As the Globus Transfer API returns a status directly (rather than a task identifier), the Action Provider behaves in a synchronous manner, returning the Transfer API result.

Globus Search / Ingest
----------------------

URL: `<https://actions.globus.org/search/ingest>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/search/ingest``

Synchronous / Asynchronous: ASynchronous

Records may be added to an existing Globus Search index using the Search / ingest Action Provider. The input to the Action Provider includes the id of the Search index to be added to and the data, in the Search-defined ``GMetaEntry`` format. The user calling the Action Provider must have permission to write to the index referenced. Globus Search will process the ingest operation asynchronously, so this Action Provider also behaves in an asynchronous fashion: requests to update the state of an Action will reflect the result from updating the state of the ingest task in Globus Search. Since Globus Search does not support cancellation of tasks, this Action Provider also does not support cancellation of its Actions.

Send Notification / email
-------------------------

URL: `<https://actions.globus.org/notification/notify>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/notification_notify``

Synchronous / Asynchronous: Synchronous

The Send notification / email Action Provider presently supports sending of email messages to a single email address. The request to send the email contains the standard components of an email: sender, receiver, subject and body. The mimetype of the body may be specified so that either HTML or text formatted messages may be sent. The body also supports the notion of variable substitution or "templating." Values in the body may be specified with a dollar sign prefix ($), and when values are provided in the ``body_variables`` property of the request, the template value will be substituted with the corresponding value from the ``body_variables``.

The other important component of the request to this action provider is the email sending credentials. Credentials are provided to allow the provider to communicate with the service used for sending the email. Presently, two modes of sending email are supported: SMTP and AWS SES. When SMTP is provided, the username, password and server hostname are required. When AWS SES is provided, the AWS access key, AWS access key secret and the AWS region must be provided. As this service is synchronous and stateless, the requester can be assured that these credentials will not be stored. The Action Provider will return success as long as the email service accepts the message. It cannot guarantee successful delivery of the message including an inability to deliver the message due to an improper recipient address.

Wait for User Option Selection
------------------------------

URL: `<https://actions.globus.org/weboption/wait_for_option>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/weboption_wait_for_option``

Synchronous / Asynchronous: Asynchronous

Flows or other clients which desire to provide users a method of selecting an option from a fixed set may use the Wait for User Option Selection Action Provider. The Action Provider can operate in one of two modes.

In the first mode, a list of options are created which are automatically selected by any access to a corresponding URLs. For each option, a name, a URL suffix, and a message or text which is returned in the HTTP response of the selection operation is provided. The URL suffix is registered with the Action Provider and is monitored at the URL ``https://actions.globus.org/weboption/option/<url_suffix>``. Any HTTP access to the URL is considered a selection of that option among all the options defined by the input to the Action and the Action will transition to a ``SUCCEEDED`` status.

In the second mode, in addition to monitoring the provided URL suffixes, a landing page may be hosted which will present the options to a user on a simple web page. The web page may be "skinned" with options for banner text, color scheme and icon as well as introductory text presented above the options. The options are specified in the same manner as in the first mode, but the page presents links which ease selection of those options for end-users. The landing page is also given a URL suffix, and the selection page will be present at ``https://actions.globus.org/weboption/landing_page/<url_suffix>``. Selection of an option within the landing page behaves the same as direct selection of an option via its URL as described above.

In either mode, once an option has been selected, none of the url suffixes, nor the landing page if configured, in the initial request will be responded to by the Action Provider: they will return the HTTP not found (error) status 404. Upon completion, the body of the status will include the name and the url suffix for the selected option. The body may also include input on the HTTP data passed when the option's URL was accessed including the query parameters and the body. To include those in the status, flags are set on the definition of the option.


Simple Expression Evaluation
----------------------------

URL: `<https://actions.globus.org/expression_eval>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/expression``

Synchronous / Asynchronous: Synchronous

Evaluation of simple expressions is supported using the `simpleeval  <https://github.com/danthedeckie/simpleeval>`_ library and therefore syntax. A single invocation of the Action Provider may evaluate a single expression or multiple expressions. An Expression request consists of up to three parts:

* An ``expression`` (required) which is a basic "arithmetic" type expression. This *does* include string type operations so an expression like "foo" + "bar" is permitted and performs string concatenation as is common in many programming and scripting languages.

* A set of ``arguments`` (optional) in a JSON object format. These arguments may be referenced in an expression. So, if there's an expression such as "x + 1" and the arguments contain ``{"x": 2}`` the result will be ``3``.

* A ``result_path`` (optional) which is a path where the result will be stored. It may be in "Reference Path" format as defined in the AWS Step Functions State Machine Language specification or it may simply be a dot separated string of the path elements. In either case, the path indidcates where in the ``details`` of the returned action status the value for the evaluated expression should be placed. If ``result_path`` is not present, the result will be stored in the ``details`` under the key ``result``.

A single request may specify multiple expressions to be evaluated by providing an array named ``expressions`` as in ``{"expressions": [{ expression1 }, {expression2}, ...]}`` where each of the expressions ``expression1`` and ``expression2`` contains the three fields defined for an expression. These will be evaluated in order, and expressions using the same ``result_path`` will result in previous results being over-written.


Datacite DOI Minting
--------------------

URL: `<https://actions.globus.org/datacite/mint/basic_auth>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/datacite_mint_basic_auth_action_all``

Synchronous / Asynchronous: Synchronous

The Datacite DOI Minting action provider uses the `Datacite JSON API <https://support.datacite.org/docs/api-create-dois>`_ to mint DOIs. The main part of the body input is as specified in that API. The additional fields provide the username and password (the "Basic Auth" credentials which is part of the name of the URL and scope string) as well as a flag indicating whether it should be used in the Datacite test service or the production service.

Example Input
^^^^^^^^^^^^^

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
