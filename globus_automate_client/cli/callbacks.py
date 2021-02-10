import json
import os
import pathlib
from errno import ENAMETOOLONG
from typing import AbstractSet, List
from urllib.parse import urlparse
from uuid import UUID

import typer
import yaml


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
    except:
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
    groups_beginning = "urn:globus:groups:id:"
    auth_beginning = "urn:globus:auth:identity:"

    for p in principals:
        if special_vals and p in special_vals:
            continue

        valid_beggining = False
        for beggining in [groups_beginning, auth_beginning]:
            if p.startswith(beggining):
                uuid = p[len(beggining) :]
                try:
                    UUID(uuid, version=4)
                except ValueError:
                    raise typer.BadParameter(
                        f"Principal could not be parsed as a valid identifier: {p}"
                    )
                else:
                    valid_beggining = True
        if not valid_beggining:
            raise typer.BadParameter(
                f"Principal could not be parsed as a valid identifier: {p}"
            )

    return principals


def principal_validator(principals: List[str]) -> List[str]:
    """
    A principal ID needs to be a valid UUID.
    """
    return _base_principal_validator(principals)


def principal_or_all_authenticated_users_validator(principals: List[str]) -> List[str]:
    """
    Certain fields expect values to be a valid Globus Auth UUID or one of a set
    of special strings that are meaningful in the context of authentication.
    This callback is a specialized form of the principal_validator where the
    special value of 'all_authenticated_users' is accepted.
    """
    return _base_principal_validator(
        principals, special_vals={"all_authenticated_users"}
    )


def principal_or_public_validator(principals: List[str]) -> List[str]:
    """
    Certain fields expect values to be a valid Globus Auth UUID or one of a set
    of special strings that are meaningful in the context of authentication.
    This callback is a specialized form of the principal_validator where the
    special value of 'public' is accepted.
    """
    return _base_principal_validator(principals, special_vals={"public"})


def flows_endpoint_envvar_callback(default_value: str) -> str:
    """
    This callback searches the caller's environment for an environment variable
    defining the target Flow endpoint.
    """
    return os.getenv("GLOBUS_AUTOMATE_FLOWS_ENDPOINT", default_value)


def input_validator(body: str) -> str:
    """
    Checks if input is a file and loads its contents, otherwise returns the
    supplied string.
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
