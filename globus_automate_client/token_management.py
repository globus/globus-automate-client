import os
from typing import Optional

from fair_research_login import ConfigParserTokenStorage, NativeClient
from fair_research_login.exc import AuthFailure, LocalServerError
from globus_sdk import AccessTokenAuthorizer, GlobusAPIError
from globus_sdk.exc import AuthAPIError

from globus_automate_client.action_client import ActionClient

CLIENT_ID = "e6c75d97-532a-4c88-b031-8584a319fa3e"
CONFIG_PATH = "~/.globus-automate.cfg"


class MultiScopeTokenStorage(ConfigParserTokenStorage):
    CONFIG_FILENAME = os.path.expanduser(CONFIG_PATH)
    GLOBUS_SCOPE_PREFIX = "https://auth.globus.org/scopes/"

    def __init__(self, scope=None):
        if scope and scope.startswith(self.GLOBUS_SCOPE_PREFIX):
            # This isn't really needed, it just keeps the section name tidy
            section = scope.replace(self.GLOBUS_SCOPE_PREFIX, "")
        else:
            section = "default"
        super().__init__(filename=self.CONFIG_FILENAME, section=section)


def get_authorizer_for_scope(
    scope: str, client_id: str = CLIENT_ID
) -> AccessTokenAuthorizer:
    client = NativeClient(
        client_id=client_id,
        app_name="globus-automate CLI",
        token_storage=MultiScopeTokenStorage(scope),
        default_scopes=[scope],
    )
    try:
        client.login(
            requested_scopes=[scope],
            refresh_tokens=True,
        )
    except (LocalServerError, AuthAPIError, AuthFailure) as e:
        print(f"Login Unsuccessful: {str(e)}")
        raise SystemExit

    authorizers = client.get_authorizers_by_scope(requested_scopes=[scope])
    return authorizers[scope]


def get_cli_authorizer(
    action_url: str,
    action_scope: Optional[str],
    client_id: str = CLIENT_ID,
) -> Optional[AccessTokenAuthorizer]:
    if action_scope is None:
        # We don't know the scope which makes it impossible to get a token,
        # but create a client anyways in case this Action Provider is publicly
        # visible and we can introspect its scope
        try:
            action_scope = ActionClient.new_client(action_url, None).action_scope
        except GlobusAPIError:
            pass

    if action_scope:
        authorizer = get_authorizer_for_scope(action_scope, client_id)
    else:
        # Any attempts to use this authorizer will fail but there's nothing we
        # can do without a scope.
        authorizer = None
    return authorizer
