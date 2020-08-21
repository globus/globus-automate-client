import json
import os
import pathlib
from typing import List, Optional
from urllib.parse import urlparse
from uuid import UUID

import typer


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


def principal_validator_callback(principals: List[str]) -> List[str]:
    """
    A principal ID needs to be a valid UUID. This validator ensures the
    principal IDs are valid UUIDs.
    """
    groups_beginning = "urn:globus:groups:id:"
    auth_beginning = "urn:globus:auth:identity:"

    for p in principals:
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


def flows_endpoint_envvar_callback(default_value: str) -> str:
    """
    This callback searches the caller's environment for an environment variable
    defining the target Flow endpoint.
    """
    return os.getenv("GLOBUS_AUTOMATE_FLOWS_ENDPOINT", default_value)
