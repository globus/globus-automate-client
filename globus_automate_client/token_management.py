import os

from fair_research_login import ConfigParserTokenStorage, NativeClient
from fair_research_login.exc import AuthFailure, LocalServerError
from globus_sdk import AccessTokenAuthorizer
from globus_sdk.exc import AuthAPIError

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
