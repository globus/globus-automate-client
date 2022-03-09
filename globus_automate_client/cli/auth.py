import copy
import json
import os
import pathlib
import platform
import sys
from json import JSONDecodeError
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Set, Union, cast

import click
import typer
from globus_sdk import (
    AuthAPIError,
    AuthClient,
    GlobusAPIError,
    NativeAppAuthClient,
    OAuthTokenResponse,
)
from globus_sdk.authorizers import (
    AccessTokenAuthorizer,
    GlobusAuthorizer,
    RefreshTokenAuthorizer,
)

from globus_automate_client.action_client import ActionClient

CLIENT_ID = "e6c75d97-532a-4c88-b031-8584a319fa3e"
CLIENT_NAME = "Globus Automate Command Line Interface"
AUTH_SCOPES = [
    "openid",
    "email",
    "profile",
]

DEFAULT_TOKEN_FILE = pathlib.Path.home() / pathlib.Path(".globus_automate_tokens.json")


def _get_base_scope(scope: str):
    if "[" in scope:
        return scope.split("[")[0]
    return scope


class TokenSet(NamedTuple):
    """
    Might want to check out this as a replacement:
    https://www.attrs.org/en/stable/why.html#namedtuples
    """

    access_token: str
    refresh_token: Optional[str]
    expiration_time: Optional[int]
    # Keep track of scopes associated with these tokens with the dependencies still
    # included. If we need to get a token where tokens for the base scope exist but
    # there isn't a matching dependent scope, that means we need to prompt for consent
    # again. If there is a matching full-scope-string in `dependent_scopes`, then we're
    # OK to use the token from looking up that base scope.
    dependent_scopes: Set[str]


TokensInTokenCache = Dict[str, Union[TokenSet, Dict[str, TokenSet]]]


class TokenCache:
    # A prefix we put in place in the token cache dict to create a key sub-dividing the
    # cache based on a particular environment.
    _environment_prefix = "__"

    def __init__(self, token_store: Union[pathlib.Path, str]):
        self.token_store = token_store
        self.tokens: TokensInTokenCache = {}
        self.modified = False

    @property
    def tokens_for_environment(self):
        """
        We will sub-key the full token set for environments other than production
        """
        environ = os.environ.get("GLOBUS_SDK_ENVIRONMENT")
        if environ is None or environ in {"production", "prod", "default"}:
            return self.tokens
        environ_cache_key = TokenCache._environment_prefix + environ
        if environ_cache_key not in self.tokens:
            self.tokens[environ_cache_key]: Dict[str, TokenSet] = {}
        return self.tokens[environ_cache_key]

    def set_tokens(self, scope: str, tokens: TokenSet) -> TokenSet:
        if scope in self.tokens_for_environment:
            dependent_scopes = set(tokens.dependent_scopes).union(
                set(self.tokens_for_environment[scope].dependent_scopes)
            )
            new_token_set = TokenSet(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                expiration_time=tokens.expiration_time,
                dependent_scopes=dependent_scopes,
            )
            self.tokens_for_environment[scope] = new_token_set
        else:
            self.tokens_for_environment[scope] = tokens
        self.modified = True
        return tokens

    def get_tokens(self, scope: str) -> Optional[TokenSet]:
        if "[" in scope:
            # If the full scope string is in our mapping already, we can just return
            # the tokens. If not, even if we have a token for the base scope, we
            # shouldn't return that because it won't work for the new scope.
            base_scope = scope.split("[")[0]
            tokens = self.tokens_for_environment.get(base_scope)
            if not tokens or scope not in getattr(tokens, "dependent_scopes", set()):
                return None
            else:
                return tokens
        return self.tokens_for_environment.get(scope)

    @staticmethod
    def _deserialize_from_file(file_tokens: Dict[str, Any]) -> TokensInTokenCache:
        deserialized: TokensInTokenCache = {}
        for k, v in file_tokens.items():
            if k.startswith(TokenCache._environment_prefix):
                v = TokenCache._deserialize_from_file(v)
            else:
                v = TokenSet(**v)
            deserialized[k] = v
        return deserialized

    def load_tokens(self):
        """
        May raise an EnvironmentError if the cache file exists but can't be read.
        """
        try:
            with open(self.token_store) as f:
                contents = json.load(f)
                self.tokens = TokenCache._deserialize_from_file(contents)
        except FileNotFoundError:
            pass
        except JSONDecodeError:
            raise EnvironmentError(
                "Token cache is corrupted; please run `session revoke` or remove "
                f"file {self.token_store} and try again"
            )

    @staticmethod
    def _make_jsonable(tokens) -> Dict[str, Any]:
        serialized: Dict[str, Any] = {}
        for k, v in tokens.items():
            if isinstance(v, TokenSet):
                v = v._asdict()
            elif isinstance(v, dict):
                v = TokenCache._make_jsonable(v)
            serialized[k] = v
        return serialized

    def save_tokens(self):
        def default(x):
            if isinstance(x, set):
                return list(x)
            return str(x)

        if self.modified:
            with open(self.token_store, "w") as f:
                if isinstance(self.token_store, pathlib.Path):
                    self.token_store.chmod(0o600)
                else:
                    os.chmod(self.token_store, 0o600)
                jsonable = TokenCache._make_jsonable(self.tokens)
                json.dump(
                    jsonable,
                    f,
                    indent=2,
                    sort_keys=True,
                    default=default,
                )
        self.modified = False

    def clear_tokens(
        self,
        environment_aware: bool = True,
        callback: Optional[Callable[[str, TokenSet], bool]] = None,
    ) -> None:
        if environment_aware:
            tokens = self.tokens_for_environment
        else:
            tokens = self.tokens
        for scope, token_set in copy.copy(tokens).items():
            if scope.startswith(TokenCache._environment_prefix):
                continue
            do_remove = True
            if callback is not None:
                do_remove = callback(scope, cast(TokenSet, token_set))
            if do_remove:
                tokens.pop(scope)
                self.modified = True

    def update_from_oauth_token_response(
        self, token_response: OAuthTokenResponse, original_scopes: Set[str]
    ) -> Dict[str, TokenSet]:
        by_scopes = token_response.by_scopes
        token_sets: Dict[str, TokenSet] = {}
        for scope in by_scopes:
            token_info = by_scopes[scope]
            dependent_scopes = {s for s in original_scopes if "[" in s}
            # token_info must be cast()'ed because mypy detects that
            # str and int types exist in the `token_info` dict, adds
            # them to the union of possible types, then complains.
            token_set = TokenSet(
                access_token=cast(str, token_info.get("access_token")),
                refresh_token=cast(Optional[str], token_info.get("refresh_token")),
                expiration_time=cast(
                    Optional[int], token_info.get("expires_at_seconds")
                ),
                dependent_scopes=dependent_scopes,
            )
            self.set_tokens(scope, token_set)
            token_sets[scope] = token_set
        self.save_tokens()
        return token_sets


def _get_globus_sdk_native_client(
    client_id: str = CLIENT_ID,
    client_name: str = CLIENT_NAME,
):
    return NativeAppAuthClient(client_id, app_name=client_name)


def safeprint(s, err: bool = False):
    try:
        typer.secho(s, err=err)
        if err:
            sys.stderr.flush()
        else:
            sys.stdout.flush()
    except IOError:
        pass


def _do_login_for_scopes(
    native_client: NativeAppAuthClient, scopes: List[str]
) -> OAuthTokenResponse:
    label = CLIENT_NAME
    host = platform.node()
    if host:
        label = label + f" on {host}"
    native_client.oauth2_start_flow(
        requested_scopes=scopes,
        refresh_tokens=True,
        prefill_named_grant=label,
    )

    linkprompt = (
        "Please log into Globus here:\n"
        "----------------------------\n"
        f"{native_client.oauth2_get_authorize_url()}\n"
        "----------------------------\n"
    )
    safeprint(linkprompt, err=True)
    auth_code = typer.prompt("Enter the resulting Authorization Code here", err=True)
    return native_client.oauth2_exchange_code_for_tokens(auth_code)


def get_authorizers_for_scopes(
    scopes: List[str],
    token_store: Optional[Union[pathlib.Path, str]] = None,
    client_id: str = CLIENT_ID,
    client_name: str = CLIENT_NAME,
    no_login: bool = False,
) -> Dict[str, GlobusAuthorizer]:
    token_store = token_store or str(DEFAULT_TOKEN_FILE)
    token_cache = TokenCache(token_store)
    token_cache.load_tokens()
    token_sets: Dict[str, TokenSet] = {}
    needed_scopes: Set[str] = set()
    native_client = _get_globus_sdk_native_client(client_id, client_name)

    for scope in scopes:
        token_set = token_cache.get_tokens(scope)
        if token_set is not None:
            token_sets[scope] = token_set
        else:
            needed_scopes.add(scope)

    if len(needed_scopes) > 0 and not no_login:
        token_response = _do_login_for_scopes(native_client, list(needed_scopes))
        new_tokens = token_cache.update_from_oauth_token_response(
            token_response, set(scopes)
        )
        token_sets.update(new_tokens)

    authorizers: Dict[str, GlobusAuthorizer] = {}
    for scope, token_set in token_sets.items():
        if token_set is not None:
            authorizer: Union[RefreshTokenAuthorizer, AccessTokenAuthorizer]
            if token_set.refresh_token is not None:

                def refresh_handler(
                    grant_response: OAuthTokenResponse, *args, **kwargs
                ):
                    token_cache.update_from_oauth_token_response(
                        grant_response, {scope}
                    )

                authorizer = RefreshTokenAuthorizer(
                    token_set.refresh_token,
                    native_client,
                    access_token=token_set.access_token,
                    expires_at=token_set.expiration_time,
                    on_refresh=refresh_handler,
                )
            else:
                authorizer = AccessTokenAuthorizer(token_set.access_token)
            authorizers[_get_base_scope(scope)] = authorizer
            authorizers[scope] = authorizer
    return authorizers


def get_authorizer_for_scope(
    scope: str, client_id: str = CLIENT_ID
) -> Optional[GlobusAuthorizer]:
    authorizers = get_authorizers_for_scopes([scope], client_id=client_id)
    return authorizers.get(_get_base_scope(scope))


def get_access_token_for_scope(scope: str) -> Optional[str]:
    authorizer = get_authorizers_for_scopes([scope]).get(_get_base_scope(scope))
    if not authorizer:
        click.echo(f"couldn't obtain authorizer for scope: {scope}", err=True)
        return None
    token = getattr(authorizer, "access_token", None)
    if not token:
        click.echo("authorizer failed to get token from Globus Auth")
        return None
    return token


def logout(token_store: Union[pathlib.Path, str] = DEFAULT_TOKEN_FILE) -> bool:
    cache = TokenCache(token_store)
    cache.load_tokens()
    cache.clear_tokens()
    cache.save_tokens()
    return True


def revoke_login(token_store: Union[pathlib.Path, str] = DEFAULT_TOKEN_FILE) -> bool:
    client = _get_globus_sdk_native_client(CLIENT_ID, CLIENT_NAME)
    if not client:
        click.echo("failed to get auth client", err=True)
        return False
    cache = TokenCache(token_store)
    cache.load_tokens()

    def revoker(scope: str, token_set: TokenSet) -> bool:
        client.oauth2_revoke_token(token_set.access_token)
        client.oauth2_revoke_token(token_set.refresh_token)
        return True

    cache.clear_tokens(callback=revoker)
    cache.save_tokens()
    return True


def get_current_user(
    no_login: bool = False, token_store: Union[pathlib.Path, str] = DEFAULT_TOKEN_FILE
) -> Optional[Dict[str, Any]]:
    """
    When `no_login` is set, returns `None` if not logged in.
    """
    # We don't really care which scope from the AUTH_SCOPE list we use here since they
    # all share the same resource server (Auth itself) and therefore an authorizer for
    # any of them grants us access to the same resource server.
    authorizers = get_authorizers_for_scopes(
        AUTH_SCOPES, token_store=token_store, no_login=no_login
    )
    if not authorizers:
        return None
    auth_client = AuthClient(authorizer=authorizers.get("openid"))
    try:
        user_info = auth_client.oauth2_userinfo()
    except AuthAPIError as e:
        click.echo(
            (
                "Couldn't get user information from Auth service\n"
                "(If you rescinded your consents in the Auth service, do `session"
                " logout` and try again)\n"
                f"    Error details: {str(e)}"
            ),
            err=True,
        )
        sys.exit(1)
    return user_info.data


def get_cli_authorizer(
    action_url: str,
    action_scope: Optional[str],
    client_id: str = CLIENT_ID,
) -> Optional[GlobusAuthorizer]:
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
