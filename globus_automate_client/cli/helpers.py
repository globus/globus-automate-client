import json
import yaml
from typing import Union

import typer
from globus_sdk import GlobusHTTPResponse
from flows import FlowInputFormat

verbosity_option = typer.Option(
    False, "--verbose", "-v", help="Run with increased verbosity", show_default=False
)


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


def process_definition(definition, input_format):
    """
    Turn input strings into dicts per input format type (json, yaml)
    """
    flow_dict = None
    if input_format == FlowInputFormat.json:
        try:
            flow_dict = json.loads(definition)
        except json.JSONDecodeError as e:
            raise typer.BadParameter(f"Invalid JSON: {e}")
    elif input_format == FlowInputFormat.yaml:
        try:
            flow_dict = yaml.safe_load(definition)
        except Exception as e:
            raise typer.BadParameter(f"Invalid YAML: {e}")

    return flow_dict
