import json
import os
import pathlib
import re
from errno import ENAMETOOLONG
from typing import AbstractSet, Callable, List, Optional, cast
from urllib.parse import urlparse

import typer
import yaml
from globus_sdk import AuthClient

from .auth import get_authorizer_for_scope

_uuid_regex = (
    "([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"
)
_principal_urn_regex = f"^urn:globus:(auth:identity|groups:id):{_uuid_regex}$"


def url_validator_callback(url: str) -> str:
    """
    Validates that a user provided string "looks" like a URL aka contains at
    least a valid scheme and netloc [www.example.org].
    Logic taken from https://stackoverflow.com/a/38020041
    """
    if url is None:
        return url

    url = url.strip()
    try:
        result = urlparse(url)
        if result.scheme and result.netloc:
            return url
    except Exception:
        pass
    raise typer.BadParameter("Please supply a valid url")


def _base_principal_validator(
    principals: List[str], *, special_vals: AbstractSet[str] = frozenset()
) -> List[str]:
    """
    This validator ensures the principal IDs are valid UUIDs prefixed with valid
    Globus ID beginnings. It will optionally determine if a provided principal
    exists in a set of "special" values.
    """
    auth_beginning = "urn:globus:auth:identity:"

    auth_client: Optional[AuthClient] = None

    valid_principals = []

    invalid_principals = []
    for p in principals:
        if special_vals and p in special_vals or re.match(_principal_urn_regex, p):
            valid_principals.append(p)
        else:
            # Try to do a lookup of the identity
            if auth_client is None:
                auth = get_authorizer_for_scope(
                    "urn:globus:auth:scope:auth.globus.org:view_identities"
                )
                auth_client = AuthClient(authorizer=auth)
            auth_resp = auth_client.get_identities(usernames=p)
            identities = auth_resp.data.get("identities", [])
            if len(identities) == 0:
                invalid_principals.append(p)
            for identity in identities:
                valid_principals.append(auth_beginning + identity["id"])

    if invalid_principals:
        raise typer.BadParameter(
            f"Invalid principal value {'; '.join(invalid_principals)}"
        )
    return valid_principals


def principal_validator(principals: List[str]) -> List[str]:
    """A principal ID needs to be a valid UUID."""

    return _base_principal_validator(cast(List[str], principals))


def custom_principal_validator(special_values: AbstractSet[str]) -> Callable:
    """A principal ID needs to be a valid UUID."""

    def wrapper(principals: List[str]) -> List[str]:
        return _base_principal_validator(principals, special_vals=special_values)

    return wrapper


def flows_endpoint_envvar_callback(default_value: str) -> str:
    """
    This callback searches the caller's environment for an environment variable
    defining the target Flow endpoint.
    """
    return os.getenv("GLOBUS_AUTOMATE_FLOWS_ENDPOINT", default_value)


def input_validator(body: str) -> str:
    """
    Checks if input is a file and loads its contents, otherwise returns the
    supplied string. This validator will also attempt to parse the string as a
    dict, failing if the parsing fails.
    """
    # Callbacks are run regardless of whether an option was explicitly set.
    # Handle the scenario where the default value for an option is empty
    if not body:
        return body

    # Reading from a file was indicated by prepending the filename with the @
    # symbol -- for backwards compatability check if the symbol is present and
    # remove it
    body = body.lstrip("@")

    body_path = pathlib.Path(body)
    try:
        if body_path.exists() and body_path.is_dir():
            raise typer.BadParameter("Expected file, received directory")
        elif body_path.exists() and body_path.is_file():
            with body_path.open() as f:
                body = f.read()
    except OSError as e:
        if e.errno == ENAMETOOLONG:
            # We cannot load the string to check if it exists, is a file, or
            # is a directory, so we have to assume the string is JSON and
            # continue
            pass
    try:
        parsed_body = json.loads(body)
    except json.JSONDecodeError:
        try:
            parsed_body = yaml.safe_load(body)
        except yaml.YAMLError:
            raise typer.BadParameter("Unable to load input as JSON or YAML")
    if not isinstance(parsed_body, dict):
        raise typer.BadParameter("Unable to load input as JSON or YAML")
    return body


def flow_input_validator(body: str) -> str:
    """
    Flow inputs can be either YAML or JSON formatted
    We can encompass these with just the YAML load checking,
    but we need a more generic error message than is provided
    by the other validators
    """
    # Callbacks are run regardless of whether an option was explicitly set.
    # Handle the scenario where the default value for an option is empty
    if not body:
        return body

    body = input_validator(body)
    try:
        yaml_body = yaml.safe_load(body)
    except yaml.YAMLError as e:
        raise typer.BadParameter(f"Invalid flow input: {e}")

    try:
        yaml_to_json = json.dumps(yaml_body)
    except TypeError as e:
        raise typer.BadParameter(f"Unable to translate flow input to JSON: {e}")

    return yaml_to_json
