import json
from typing import Optional, Union

import typer
from globus_sdk import GlobusHTTPResponse

from globus_automate_client.action_client import ActionClient, create_action_client
from globus_automate_client.token_management import get_access_token_for_scope

CLIENT_ID = "e6c75d97-532a-4c88-b031-8584a319fa3e"

verbosity_option = typer.Option(
    False, "--verbose", "-v", help="Run with increased verbosity", show_default=False
)


def get_action_client_for_args(
    action_url: str, action_scope: Optional[str]
) -> Optional[ActionClient]:
    """
    Attempts to create an action client for a given Action url. If the
    action_scope is not available, creates a client without a token in case the
    target Action Provider is publically visible without authentication which we
    then pull the action_scope from. Once we have the scope, retrieve its token
    sand create a client.
    """
    if action_url is None:
        return None
    if action_scope is None:
        # We don't know the scope which makes it impossible to get a token,
        # but create a client anyways in case this action provider is publicly
        # visible without authentication. If we still can't get the scope, all
        # we can do is fail.
        ac = create_action_client(action_url, "NoTokenAvailable")
        if ac is None or not ac.action_scope:
            return None
        action_scope = ac.action_scope

    access_token = get_access_token_for_scope(action_scope, CLIENT_ID)
    if access_token is not None:
        ac = create_action_client(action_url, access_token)
        return ac
    return None


def format_and_echo(result: Union[GlobusHTTPResponse, str], verbose=False) -> None:
    if verbose and isinstance(result, GlobusHTTPResponse):
        display_http_details(result)

    if isinstance(result, GlobusHTTPResponse):
        if 200 <= result.http_status < 300:
            color = typer.colors.GREEN
        else:
            color = typer.colors.RED
        result = result.data
    else:
        color = typer.colors.GREEN
    typer.secho(json.dumps(result, indent=4, sort_keys=True), fg=color)


def display_http_details(response: GlobusHTTPResponse) -> None:
    formatted_headers = "\n".join(
        f"  {k}: {v}" for k, v in response._data.request.headers.items()
    )
    print(f"Request: {response._data.request.method} {response._data.request.url}")
    print(f"Headers:\n{formatted_headers}")
    print(f"Response: {response._data.status_code}")
