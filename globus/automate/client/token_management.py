from time import time
from globus_sdk import NativeAppAuthClient
import json
from os import path
from typing import Any, Dict, List, Optional, Tuple


# python2/3 safe simple input reading
get_input = getattr(__builtins__, "raw_input", input)

_token_cache_filename = path.join(path.expanduser("~"), ".globus_token_cache")


def perform_token_refresh(refresh_token: str) -> Tuple[Optional[str], Optional[int]]:
    return (None, None)


def _load_cache() -> Dict[Any, Any]:
    try:
        with open(_token_cache_filename) as f:
            cache = json.load(f)
            return cache
    except FileNotFoundError:
        return {}


def get_cached_tokens(scope: str) -> Tuple[Optional[str], Optional[str]]:
    token_cache = _load_cache()
    access_token = None
    refresh_token = None
    if scope in token_cache:
        access_token = token_cache[scope]["access_token"]
        refresh_token = token_cache[scope]["refresh_token"]
        access_token_expiration = token_cache[scope]["expires_at_seconds"]
        if access_token_expiration < int(time() - 60.0):
            # IF we think the access token will expire soon, we don't return it
            access_token = None
    return (access_token, refresh_token)


def update_cache(
    scope: str, access_token: str, access_token_expiration: int, refresh_token: str
) -> None:
    token_cache = _load_cache()
    token_cache[scope] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at_seconds": access_token_expiration,
    }
    with open(_token_cache_filename, "w") as f:
        json.dump(token_cache, f, indent=2)


def perform_native_auth_flow(
    client_id: str, scopes: List[str]
) -> List[Tuple[str, int, str]]:
    native_client = NativeAppAuthClient(client_id)
    native_client.oauth2_start_flow(
        requested_scopes=scopes,
        refresh_tokens=True,
        prefill_named_grant="Globus Automate Client",
    )
    # Login link for an authorization code this is like a one-time password used to
    # fetch longer-lasting credentials (tokens)
    print("Login Here:\n\n{0}".format(native_client.oauth2_get_authorize_url()))
    print(
        (
            "\n\nNote that this link can only be used once! "
            "If login or a later step in the flow fails, you must restart it."
        )
    )

    # fill this line in with the code that you got
    auth_code = get_input("Enter resulting code:")

    # and exchange it for a response object containing your token(s)
    # we'll use this "tokens" object in later steps
    tokens = native_client.oauth2_exchange_code_for_tokens(auth_code)
    token_list = []
    for scope in scopes:
        scope_token = tokens.by_scopes[scope]
        token_list.append(
            (
                scope_token["access_token"],
                scope_token["expires_at_seconds"],
                scope_token["refresh_token"],
            )
        )
    return token_list


def get_access_token_for_scope(scope: str, native_app_client_id: str) -> Optional[str]:
    access_token, refresh_token = get_cached_tokens(scope)

    access_token_expiration = None
    cache_needs_update = False
    if refresh_token and not access_token:
        access_token, access_token_expiration = perform_token_refresh(refresh_token)
        cache_needs_update = True

    if not access_token:
        access_token, access_token_expiration, refresh_token = perform_native_auth_flow(
            native_app_client_id, (scope,)
        )[0]
        cache_needs_update = True

    if cache_needs_update:
        update_cache(scope, access_token, access_token_expiration, refresh_token)
    return access_token
