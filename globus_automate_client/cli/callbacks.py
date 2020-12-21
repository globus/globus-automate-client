import json
import os
import pathlib
import yaml
import typer

from typing import AbstractSet, List
from urllib.parse import urlparse
from uuid import UUID


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


def json_validator_callback(body: str) -> str:
    """
    A user supplied body can be a properly formatted JSON string or a the name
    of a file that contains valid JSON.  This validator ensures the user
    supplies a valid JSON or valid filename containing valid JSON. Returns the
    valid JSON string.
    """
    # Callbacks are run regardless of whether an option was explicitly set.
    # Handle the scenario where the default value for an option is empty
    if not body:
        return body

    # Reading from a file was indicated by prepending the filename with the @
    # symbol -- for backwards compatability check if the symbol is present and
    # remove it
    if body.startswith("@"):
        body = body[1:]

    body_path = pathlib.Path(body)
    if body_path.exists() and body_path.is_file():
        with body_path.open() as f:
            try:
                json_body = json.load(f)
            except json.JSONDecodeError as e:
                raise typer.BadParameter(f"Invalid JSON: {e}")
            else:
                body = json.dumps(json_body)
    elif body_path.exists() and body_path.is_dir():
        raise typer.BadParameter("Expected file, received directory")
    else:
        try:
            json.loads(body)
        except json.JSONDecodeError as e:
            raise typer.BadParameter(f"Invalid JSON: {e}")
    return body


def yaml_validator_callback(body: str) -> str:
    """
    A user supplied body can be a properly formatted YAML string or a the name
    of a file that contains valid YAML.  This validator ensures the user
    supplies a valid YAML or valid filename containing valid YAML. Returns the
    valid JSON string.
    """
    # Callbacks are run regardless of whether an option was explicitly set.
    # Handle the scenario where the default value for an option is empty
    if not body:
        return body

    # Reading from a file was indicated by prepending the filename with the @
    # symbol -- for backwards compatability check if the symbol is present and
    # remove it
    if body.startswith("@"):
        body = body[1:]

    body_path = pathlib.Path(body)

    if body_path.exists() and body_path.is_file():
        with body_path.open() as f:
            try:
                yaml_body = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise typer.BadParameter(f"Invalid YAML: {e}")
    elif body_path.exists() and body_path.is_dir():
        raise typer.BadParameter("Expected file, received directory")
    else:
        try:
            yaml_body = yaml.safe_load(body)
        except yaml.YAMLError as e:
            raise typer.BadParameter(f"Invalid YAML: {e}")

    try:
        yaml_to_json = json.dumps(yaml_body)
    except TypeError as e:
        raise typer.BadParameter(f"Unable to translate to JSON: {e}")

    return yaml_to_json


def text_validator_callback(message: str) -> str:
    """
    A user may supply a message directly on the command line or by referencing a
    file whose contents should be interpreted as the message. This validator
    determines if a user supplied a valid file name else use the raw text as the
    message. Returns the text to be used as a message.
    """
    # Reading from a file was indicated by prepending the filename with the @
    # symbol -- for backwards compatability check if the symbol is present and
    # remove it
    if message.startswith("@"):
        message = message[1:]

    message_path = pathlib.Path(message)
    if message_path.exists() and message_path.is_file():
        with message_path.open() as f:
            return f.read()

    return message


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


def input_validator_callback(value: str) -> str:
    """
    Allows for the input_format parameter to guide which input
    validation scheme to use (JSON or YAML) with JSON as default
    """
    json_data = None

    try:
        json_data = json_validator_callback(value)
    except:

        json_data = yaml_validator_callback(value)
    finally:
        return json_data
