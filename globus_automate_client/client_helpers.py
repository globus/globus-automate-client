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
    Providers. This helper will look for and store tokens on a local filesystem,
    optionally triggering a log-in flow if the requested tokens are not found
    locally. To create an ActionClient without referencing local storage or
    triggering a login flow, instantiate an authorizer directly and use the
    ``ActionClient.new_client`` classmethod.

    Given the ``action_url`` for a specific ActionProvider, this function will
    attempt to create a valid ``ActionClient`` for interacting with that
    ActionProvider. If the ``action_scope`` is not provided, this function will
    attempt to discover the ``action_scope`` by querying the target Action
    Provider's introspection endpoint. If the Action Provider is not configured
    to allow public, unauthenticated access to its introspection endpoint, the
    ``action_scope`` will be non-discoverable and authentication will fail.

    With the ``action_scope`` available, the function will search for a valid
    token using the fair-research/native-login library. In the event that tokens
    for the scope cannot be loaded, an interactive login will be triggered. Once
    tokens have been loaded, an Authorizer is created and used to instantiate
    the ``ActionClient`` which can be used for operations against that Action
    Provider.

    :param action_url: The URL address at which the target Action Provider
        exists
    :param action_scope: The target Action Provider's Globus Auth Scope used
        for authenticating access to it
    :param client_id: The ID for the Native App Auth Client which will be
        triggering the login flow for this ActionClient
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
    This function will attempt to load tokens for the MANAGE_FLOWS_SCOPE using
    the fair-research/native-login library. In the event that tokens for the
    scope cannot be loaded, an interactive login Flow will be triggered. Once
    tokens have been loaded, an Authorizer is created and used to instantiate
    the ``FlowsClient``. To create a FlowsClient without referencing local
    storage or triggering a login flow, instantiate an authorizer directly and
    use the ``FlowsClient.new_client`` classmethod.

    :param client_id: The Globus ID to associate with this instance of the
        FlowsClient
    :param base_url: The URL at which the Globus Automate Flows service is
        located
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
