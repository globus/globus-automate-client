from typing import Optional

from globus_automate_client.action_client import ActionClient
from globus_automate_client.cli.auth import CLIENT_ID, get_cli_authorizer
from globus_automate_client.cli.rich_rendering import live_content
from globus_automate_client.flows_client import (
    MANAGE_FLOWS_SCOPE,
    PROD_FLOWS_BASE_URL,
    FlowsClient,
)


def create_action_client(
    action_url: str,
    action_scope: Optional[str] = None,
    client_id: str = CLIENT_ID,
) -> ActionClient:
    """
    A helper function to handle creating a properly authenticated ``ActionClient``
    which can operate against *Globus Action Provider Interface* compliant Action
    Providers. This helper will create an ``ActionClient`` by searching for and
    storing tokens on the local filesystem, potentially triggering a log-in flow
    if the requested tokens are not found locally.

    Given the ``action_url`` for a specific ActionProvider, this function will
    attempt to create a valid ``ActionClient`` for interacting with that
    ActionProvider. If the ``action_scope`` is not provided, this function will
    attempt to discover the ``action_scope`` by querying the target Action
    Provider's introspection endpoint. If the Action Provider is not configured
    to allow public, unauthenticated access to its introspection endpoint, the
    ``action_scope`` will be non-discoverable and authentication will fail.

    With the ``action_scope`` available, the function will search for a valid
    token in the local filesystem cache. In the event that tokens for the scope
    cannot be loaded, an interactive login will be triggered. Once
    tokens have been loaded, an Authorizer is created and used to instantiate
    the ``ActionClient`` which can be used for operations against that Action
    Provider.

    :param action_url: The URL address at which the target Action Provider
        exists
    :param action_scope: The target Action Provider's Globus Auth Scope used
        for authenticating access to it
    :param client_id: The ID for the Native App Auth Client which will be
        triggering the login flow for this ActionClient

    **Examples**
        >>> from globus_automate_client import create_action_client
        >>> # Create an ActionClient for the HelloWorld Action
        >>> ac = create_action_client("https://actions.globus.org/hello_world")
        >>> # Run an Action and check its results
        >>> resp = ac.run({"echo_string": "Hello from SDK"})
        >>> assert resp.data["status"] == "SUCCEEDED"
    """
    authorizer = get_cli_authorizer(
        action_url=action_url, action_scope=action_scope, client_id=client_id
    )
    return ActionClient.new_client(action_url=action_url, authorizer=authorizer)


def cli_authorizer_callback(**kwargs):
    flow_url = kwargs["flow_url"]
    flow_scope = kwargs["flow_scope"]
    client_id = kwargs["client_id"]

    live_content.pause_live()
    authorizer = get_cli_authorizer(flow_url, flow_scope, client_id)
    live_content.resume_live()
    return authorizer


def create_flows_client(
    client_id: str = CLIENT_ID, base_url: str = PROD_FLOWS_BASE_URL
) -> FlowsClient:
    """
    A helper function to handle creating a properly authenticated
    ``FlowsClient`` which can operate against the Globus Automate Flows service.
    This function will attempt to load tokens for the ``MANAGE_FLOWS_SCOPE``from
    the local filesystem, triggering a log-in if the requested tokens are not
    found locally. Once tokens have been loaded, an Authorizer is created and
    used to instantiate the ``FlowsClient``. Attempts to interact with a
    specific Flow will similarly search for valid tokens in the local cache,
    triggering an interactive log-in if they cannot be found.

    :param client_id: The Globus ID to associate with this instance of the
        FlowsClient
    :param base_url: The URL at which the Globus Automate Flows service is
        located

    **Examples**
        >>> from globus_automate_client import create_flows_client
        >>> # Create an authenticated FlowsClient that can run operations against the Flows
        >>> # service
        >>> fc = create_flows_client(CLIENT_ID)
        >>> # Get a listing of runnable, deployed flows
        >>> available_flows = fc.list_flows(["runnable_by"])
        >>> for flow in available_flows.data["flows"]:
        >>>     print(flow)
    """
    authorizer = get_cli_authorizer(
        action_url=base_url, action_scope=MANAGE_FLOWS_SCOPE, client_id=client_id
    )
    return FlowsClient.new_client(
        client_id,
        authorizer_callback=cli_authorizer_callback,
        authorizer=authorizer,
        base_url=base_url,
    )
