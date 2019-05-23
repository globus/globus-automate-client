from time import time
from globus_sdk import NativeAppAuthClient
import json
from os import path
from typing import Any, Dict, List, Optional, Tuple


# python2/3 safe simple input reading
get_input = getattr(__builtins__, "raw_input", input)

_token_cache_filename = path.join(path.expanduser("~"), ".globus_token_cache")


def perform_token_refresh(
    refresh_token: str, client_id: str
) -> Tuple[Optional[str], Optional[int]]:
    native_client = NativeAppAuthClient(client_id)
    token_response = native_client.oauth2_refresh_token(refresh_token)
    tokens = token_response.by_resource_server
    for resource_server in tokens:
        token_info = tokens[resource_server]
        return (token_info["access_token"], token_info["expires_at_seconds"])
    return (None, None)


def _load_cache() -> Dict[Any, Any]:
    try:
        with open(_token_cache_filename) as f:
            cache = json.load(f)
            return cache
    except FileNotFoundError:
        return {}


def get_cached_tokens(
    scopes: List[str]
) -> Dict[str, Tuple[Optional[str], Optional[str]]]:
    token_cache = _load_cache()
    access_token = None
    refresh_token = None
    ret_tokens: Dict[str, Tuple[Optional[str], Optional[str]]] = {}
    for scope in scopes:
        if scope in token_cache:
            access_token = token_cache[scope]["access_token"]
            refresh_token = token_cache[scope]["refresh_token"]
            access_token_expiration = token_cache[scope]["expires_at_seconds"]
            if access_token_expiration < int(time() - 60.0):
                # IF we think the access token will expire soon, we don't return it
                access_token = None
            ret_tokens[scope] = (access_token, refresh_token)
        else:
            ret_tokens[scope] = (None, None)
    return ret_tokens


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
) -> Dict[str, Tuple[str, int, str]]:
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
    token_map: Dict[str, Tuple[str, str, str]] = {}
    for scope in scopes:
        scope_token = tokens.by_scopes[scope]
        token_map[scope] = (
            scope_token["access_token"],
            scope_token["expires_at_seconds"],
            scope_token["refresh_token"],
        )
    return token_map


def get_access_tokens_for_scopes(
    scopes: List[str], native_app_client_id: str
) -> Dict[str, str]:
    token_cache = get_cached_tokens(scopes)
    missing_scopes: List[str] = []
    access_tokens: Dict[str, str] = {}
    for scope in scopes:
        access_token, refresh_token = token_cache.get(scope, (None, None))
        if refresh_token is not None and access_token is None:
            print(f"Requesting refresh on scope {scope}")
            access_token, access_token_expiration = perform_token_refresh(
                refresh_token, native_app_client_id
            )
            print(f"Refresh retruned {(access_token, access_token_expiration)}")
            if access_token is not None and access_token_expiration is not None:
                update_cache(
                    scope, access_token, access_token_expiration, refresh_token
                )

        if access_token is None:
            missing_scopes.append(scope)
        else:
            access_tokens[scope] = access_token

    if len(missing_scopes) > 0:
        new_tokens = perform_native_auth_flow(native_app_client_id, missing_scopes)
        for scope in missing_scopes:
            access_token, access_token_expiration, refresh_token = new_tokens[scope]
            update_cache(scope, access_token, access_token_expiration, refresh_token)
            access_tokens[scope] = access_token

    return access_tokens


def get_access_token_for_scope(scope: str, native_app_client_id: str) -> Optional[str]:
    access_token_map = get_access_tokens_for_scopes((scope,), native_app_client_id)
    return access_token_map.get(scope)
