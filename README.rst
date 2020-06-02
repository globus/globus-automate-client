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

Globus Transfer / ls
--------------------------------

URL: `<https://actions.globus.org/transfer/ls>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/transfer_ls``

Synchronous / Asynchronous: Synchronous

The Globus Transfer ls Action Provider uses the Globus Transfer API to retrieve a listing of contents from an (endpoint, path) pair.  Although providing a path is optional, the default path used depends on endpoint type and it is best to explicitly set a path. This Action Provider supports all options as defined in the List Directory Contents Transfer API documentation.

Globus Search / Ingest
----------------------

URL: `<https://actions.globus.org/search/ingest>`_

Scope: ``https://auth.globus.org/scopes/5fac2e64-c734-4e6b-90ea-ff12ddbf9653/search/ingest``

Synchronous / Asynchronous: Asynchronous

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

In the first mode, a list of options are created which are automatically selected by any access to a corresponding URLs. For each option, a name, a URL suffix, and a message or text which is returned in the HTTP response of the selection operation is provided. The URL suffix is registered with the Action Provider and is monitored at the URL ``https://actions.globus.org/weboption/option/<url_suffix>``. Any HTTP access to the URL is considered a selection of that option among all the options defined by the input to the Action and the Action will transition to a ``SUCCEEDED`` status. Each of the options may be protected for access only via specific Globus identities by setting values on the ``selectable_by`` list. A direct HTTP access may present a Bearer token for authorization using the same scope as used for accessing the other operations on the Action Provider. If not access token is presented, the user will be re-directed to start an OAuth Flow using Globus Auth to authenticate access to the option URL.

In the second mode, in addition to monitoring the provided URL suffixes, a landing page may be hosted which will present the options to a user on a simple web page. The web page may be "skinned" with options for banner text, color scheme and icon as well as introductory text presented above the options. The options are specified in the same manner as in the first mode, but the page presents links which ease selection of those options for end-users. The landing page is also given a URL suffix, and the selection page will be present at ``https://actions.globus.org/weboption/landing_page/<url_suffix>``. Selection of an option within the landing page behaves the same as direct selection of an option via its URL as described above. Similar to individual options, the landing page can be protected by setting a ``selectable_by`` list. As the landing page is intended for use via a browser, it will always start a OAuth Flow to authenticate the user. If ``selectable_by`` is set on the landing page but not on any of the individual options, the options inherit the same ``selectable_by`` value defined on the landing page for that Action.

In either mode, once an option has been selected, none of the url suffixes, nor the landing page if configured, in the initial request will be responded to by the Action Provider: they will return the HTTP not found (error) status 404. Upon completion, the body of the status will include the name and the url suffix for the selected option. The body may also include input on the HTTP data passed when the option's URL was accessed including the query parameters and the body. To include those in the status, flags are set on the definition of the option.


Simple Expression Evaluation
----------------------------

.. note:: Expression Evaluation has been integrated with Action definitions directly (see section on Action definitions below). Thus, for most use cases, the Simple Expression Evaluation Action Provider described here is not needed and expressions defined on Action definitions within a Flow are preferred.

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


Authoring Flows for the Globus Flows Service
============================================

The Globus Flows Service provides users with the ability to easily define compositions, Flows, of a numerous Actions to perform a single, logical operation. Flows may be invoked as other Actions, potentially running for a long time with an API for monitoring the progress of the flow instance during its lifetime. Definition of such Flows requires an easy to read, author, and potentially visualize method of defining the Flows. For this purpose, the Flows service starts from the core of the `Amazon States Language <https://states-language.net/spec.html>`_. In particular, the general structure of a Flow matches that of a States Language State Machine in particular matching the requirements defined for `Top-Level Fields <https://states-language.net/spec.html#toplevelfields>`_ including the properties:

* ``States``

* ``StartAt``

* ``Comment``

Additionally, general concepts from the States Language and its method of managing state for the State Machine/Flow are maintained. Concepts such as `Input and Output Processing <https://states-language.net/spec.html#filters>`_ are handled in the same manner (see note below for an important exception). In particular, paths within the state of the Flow are referenced with a ``$.`` prefix just as defined in the States Language.

Only the following two state types are supported in Flows in nearly (see note below) the same manor as defined in the States Language:

* `Pass <https://states-language.net/spec.html#pass-state>`_

* `Choice <https://states-language.net/spec.html#choice-state>`_

.. note:: The exception is the user of the ``OutputPath`` property of either of these states. ``OutputPath`` is not allowed in a Flow definition. Instead, the ``ResultPath`` must always be used to specify where the result of a state execution will be stored placed into the state of the Flow.

Invoking Actions
----------------

As Actions are the core building block for most concepts in Globus Automate, Action invocation takes on a central role in the definition of Flows. Actions are invoked from a Flow using the state type ``Action``. We describe the structure of an ``Action`` state via the following example which is described in detail below:

.. code-block:: JSON

    {
      "Type": "Action",
      "ActionUrl": "<URL to the Action, as defined above for various Actions>",
      "ActionScope": "<Scope String for the Action, as defined above for various Actions>",
      "WaitTime": 3600,
      "ExceptionOnActionFailure": true,
      "RunAs": "User",
      "InputPath": "$.Path.To.Action.Body",
      "Parameters": {
        "constant_val": 10,
        "reference_value.$": "$.Path.To.Value",
        "nested_value": {
          "child_const_val": true,
          "child_ref_val.$": "$.Child.Val.Path"
        },
        "secret_value": "MyPassword",
        "__Private_Parameters": ["secret_value"]
      },
      "ResultPath": "$.ActionOutput",
      "Catch": [
        {
          "ErrorEquals": ["ActionUnableToRun"],
          "Next": "RunFailureHandler"
        },
        {
          "ErrorEquals": ["ActionFailedException"],
          "Next": "ActionFailureHandler"
        }
      ],
      "Next": "FollowingState",
      "End": true
    }

Each of the properties on the ``Action`` state are defined as follows. In some cases, we provide additional discussion of topics raised by specific properties in further sections below this enumeratiion.

*  ``Type`` (required): As with other States defined by the States Language, the ``Type`` indicates the type of this state. The value ``Action`` indicates that this state represents an Action invocation.

*  ``ActionUrl`` (required): The base URL of the Action. As defined by the Action Interface, this URL has methods such as ``/run``, ``/status``, ``/cancel`` and so on defined to manage the life-cycle of an Action. The Action Flow state manages the life-cycle of the invoked Action using these methods and assumes that the specific operations are appended to the base URL defined in this property. For Globus operated actions, the base URLs are as defined previously in this document.

*  ``ActionScope`` (required): The scope string to be used when authenticating to access the Action. Users of the Flow in which this definition occurs will be required to consent to the Flow use of this scope on their behalf. For Globus operated actions, the scopes are as defined previously in this document.

*  ``WaitTime`` (optional, default value ``300``): The maximum amount time to wait for the Action to complete in seconds. Upon execution, the Flow will monitor the execution of the Action for the specified amount of time, and if it does not complete by this time it will abort the Action. See `Action Execution Monitoring`_ for additional information on this. The default value is ``300`` or Five Minutes.

*  ``ExceptionOnActionFailure`` (optional, default value ``false``): When an Action is executed but is unable complete successfully, it returns a ``status`` value of ``FAILED``. As this represents a complete execution of the Action, this returned state is, by default, returned as the final state of the Action state. However, it is commonly useful to treat this "Action Failed" occurrence as an Exception type state for the Flow itself. Setting this property to ``true`` will cause a Run-time exception of type ``ActionFailedException`` to be raised which can be managed with a ``Catch`` statement. Further details on discussion of the ``Catch`` property of the Action state and in the `Managing Exceptions`_ section.

*  ``RunAs`` (option, default value ``User``): When the Flow executes the Action, it will, by default, execute the Action on behalf of the user which invoked the Flow. Thus, from the perspective of the Action, it is the user who invoked the Flow who is also invoking the Action, and thus the Action will make authorization decisions based on the identity of the User invoking the Flow. In some circumstances, it will be beneficial for the Action to be configured to perform authorization based on a value known during Flow definition rather than being dependent on the user who invoked the Flow. As each Flow has its own identity the Flow's identity can be used for this purpose. Thus, setting a value of ``Flow`` for the ``RunAs`` property implies that, at run-time, the Action will be invoked by an identity associated with the Flow itself, and not the user invoking the flow.

.. note:: At time of writing, this capability is not yet implemented and only the default behavior of invoking as the user is supported.

*  ``InputPath`` or ``Parameters`` (mutually exclusive options, at least one is required): Either ``InputPath`` or ``Parameters`` can be used to identify or form the input to the Action to be run. as passed in the ``body`` of the call to the action ``/run`` operation.

   *  ``Parameters``: The Parameters property is defined as an object that becomes the input to the Action. As such, it becomes relatively plain in the ``Action`` state definition that the structure of the ``Parameters`` object matches the structure of the body of the input to the Action being invoked. Some of the fields in the ``Parameters`` object can be protected from introspection later so that secret or sensitive information, such as credentials, can be encoded in the parameter values without allowing visibility outside the flow, including by those running the Flow. The private parameter functionality is described in `Protecting Action and Flow State`_. Values in ``Parameters`` can be specified in a variety of ways:

      *  **Constants**: Simply specify a value which will always be passed for that property. Constants can be any type: numeric, string, boolean or other objects should an action body specify sub-objects as part of their input. When an object is used, each of the properties within the object can also be of any of the types enumerated here.

      *  **References**: Copies values from the state of the flow to the name given. The name must end with the sequence ``.$`` to indicate that a reference is desired, and the string-type value must be a `Reference Path <https://states-language.net/spec.html#ref-paths>`_ starting with the characters ``$.`` indicating the location in the Flow run-time state that values should be retrieved from.

      *  **Expressions**: Allow values to be computed as a combination of constants and references to other state in the Flow's run-time. This provides a powerful mechanism for deriving parameter values and is defined more fully below in `Expressions in Parameters`_

   *  ``InputPath``: Specifies a path within the existing state of the Flow where the values to be passed will be present. Thus, use of ``InputPath`` requires that the proper input be formed in the Flow state.

*  ``ResultPath``: Is a `Reference Path <https://states-language.net/spec.html#ref-paths>`_ indicating where the output of the Action will be placed in the state of the Flow run-time. The entire output returned from the Action will be returned including the ``action_id``, the final ``status`` of the Action, the ``start_time`` and ``completion_time`` and, importantly, the ``details`` containing the action-specific result values. If ``ResultPath`` is not explicitly provided, the default value of simply ``$``, indicating the root of the Flow state, is assumed and thus the result of the Action will become the entire Flow state following the ``Action`` state's execution. Typically this is not the desired behavior, so a ``ResultPath`` should almost always be included.

*  ``Catch``: When Actions end abnormally, an Exception is raised. A ``Catch`` property defines how the Exception should be handled by identifying the Exception name in the ``ErrorEquals`` property and identifying a ``Next`` state to transition to when the Exception occurs. If no ``Catch`` can handle an exception, the Flow execution will abort on the Exception. A variety of exception types are defined and are enumerated in `Managing Exceptions`_.

*  ``Next`` or ``End`` (mutually exclusive, one required): These indicate how the Flow should proceed after the Action state. ``Next`` indicates the name of the following state of the flow, and ``End`` with a value ``true`` indicates that the Flow is complete after this state completes.

Protecting Action and Flow State
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At times, portions of a Flow state may need to be secret or protected from the various operations, like status and log, which can be used to monitor and observe the state of a Flow execution. For example, some Actions may require credentials or keys to authenticate or permit access. These items should not be visible to some users, particularly when they are encoded (e.g. in Parameter constants) by the Flow author. There are two areas where these values may be stored or encoded: in ``Parameters`` to Actions, and within the state of the Flow at run-time. The service provides mechanisms for protecting information in both cases.

For ``Parameters``, a list with special property name ``__Private_Parameters`` may be placed in the ``Parameters`` object indicating which other Parameters should be protected. For simplicity, the values in the ``__Private_Properties`` list may include the "simple" name even when the parameter name is a Reference or Expression. For example, if a parameter value has the form ``"SecretValue.$": "$.Path.To.Secret"`` the value in the ``__Private_Parameters`` list may be simply ``SecretValue`` omitting the trailing ``.$`` which identifies the parameter as a reference. Similarly for expression parameters, the trailing ``.=`` may be omitted.  The ``__Private_Parameters`` list may be applied at any nesting level of the Parameters. Thus, in the following ``Parameters`` definition:

.. code-block:: JSON

    {
      "Parameters": {
        "server_info": {
          "URL": "https://example.com",
          "user_name": "FlowUser",
          "password": "my_password",
          "__Private_Parameters": ["password"]
        }
      }
    }


The ``password`` property within the ``server_info`` object would be omitted from output of any state of the Flow retrieved by any user.

To protect the state of the Flow's run-time, any property which starts with the prefix ``_private`` will be omitted from Flow introspection. Thus, if protected values need to be stored within the Flow state, they could be stored in a property with a name like ``_private_secret_property`` or in an object simply having the name ``_private`` as that object, starting with the prefix will entirely be omitted from the output. As an example, the following flow state would not be visible:

.. code-block:: JSON

    {
      "_private": {
          "user_name": "FlowUser",
          "password": "my_password",
      }
    }


However, the properties *MAY* still be referenced as part of a reference path such as in an Action parameter. Thus, the reference path ``$._private.password`` could be used and the value ``my_password`` would be used for the parameter. In such a case, that parameter would also most likely need to appear in the ``__Private_Parameters`` list to prevent the value from being shown when the state of the particular Action is displayed to a user. Thus, the state protection via ``_private`` property names and the enumeration of protected parameters via ``__Private_Parameters`` will often be used in tandem.

Action Execution Monitoring
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``Action`` states will block waiting until the executed action reaches a completion state with status value either ``SUCCEEDED`` or ``FAILED`` or when the ``WaitTime`` duration is reached. Within this time interval, the Flow will periodically poll the Action to determine if it has reached a completion state. The interval between polls increases using an exponential back-off strategy (i.e. the amount of time between two polls is a multiple of the interval between the previous two polls). Thus, detection of the completion will not be instantaneous compared to when the action "actually" completes. And, the longer the wait time, the longer the interval between "actual" completion and the poll detecting completion may be. This "slop" time is related to both the total run time for the Action and the exponential back-off factor increasing the time between polls. Presently, the factor is 1.1, though this is subject to change as the system is tuned. As a result, the maximum slop time is 10% of the total time the action takes to execute. Thus, for example, an action which takes 30 hours to run might not be observed as complete until 33 hours after it starts in the absolute worst case.

When using the Flows service, it is important to remember that this slop time can occur. One may observer or receive other notification (such as an email for a Globus Transfer) that an Action has completed but the Flows service may not poll to discover the same state has been reached. This is an inherent property of the system. and while the maximum slop time may, as stated, be tuned, there is presently no way to avoid it entirely.

Expressions in Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^

Action Parameters allow the inputs to an Action to be formed from different parts of the Flow run-time state. However, the reference approach requires that the exact value needed be present in the Flow's state. If the required value is somehow to be derived from multiple values in the Flow state, reference parameters are not sufficient. Thus, we introduce expression type parameters which may evaluate multiple parts of the state to compute a single, required value.

The syntax of an expression paramter takes the following form:

.. code-block:: JSON

    {
      "computed_param.=": "`$.JsonPathExpr1` <op> `$.JsonPathExpr2` <op> ..."
    }


The important parts of this expression are the references to the Flow state via `JsonPath <https://goessner.net/articles/JsonPath/>`_ expressions, and the operations and expression syntax that may be used. Values from the state are specified via a JsonPath expression which is surrounded by single "back-quote" characters (\`). The full selection capability of JsonPath is supported, so entire list values, list indexing, list slicing and so on may be specified in the JsonPath.

Values in the expression may also be constant values. It is important to remember that within an expression, a string type value must be enclosed in quotes. Thus, the expression ``foo + bar`` will be an error as the unquoted values ``foo`` and ``bar`` don't represent either a constant or a JsonPath value, where as the expression ``"foo" + "bar"`` will result in the expected(?) output ``foobar``.

The syntax for the expression largely follows what is expected in common expression languages. This includes common arithmetic operators on numeric values as well as operations on strings (e.g. string concatenation via a `+` operation) and on lists (similarly the `+` operator will concatenate lists).


Managing Exceptions
^^^^^^^^^^^^^^^^^^^

Failures of Action states in the Flow are exposed via Exceptions which, as described above, can be handled via a ``Catch`` property on the Action state. The form of the ``Catch`` is described, but the types of exceptions need to be discussed in more detail. There are three forms of exceptions that impact an Action execution:

*  ``ActionUnableToRun``: This exception indicates that the initial attempt to run the Action failed and no action whatsoever was initiated. The output of the exception contains the error structure returned by the Action. This condition will always result in an exception.

*  ``ActionFailedException``: This indicates that the Action was able to be initiated but during execution the Action was considered to have failed. This exception will only be raised if the property ``ExceptionOnActionFailure`` is set to true. This allows the Action failure to be handled by checking the result or by causing an exception. Either approach is valid and different users and different use cases may lend themselves to either approach. In either case, the output will contain the same Action status structure a completed action will contain, but the ``status`` value will necessarily be ``FAILED``.

*  Action timed out: When the running time of the Action exceeds the ``WaitTime`` value a generic exception signaling the timeout is raised. As the exception does not have a specific name, it can be caught using the value ``States.ALL`` (as defined in the States Language definition) in the ``ErrorEquals`` list for the Catch. Indeed, the ``States.ALL`` value indicates any exception condition, so if handling all of the above exception conditions in the same manner is desired, then simply one handler with the ``States.ALL`` value can be used.
