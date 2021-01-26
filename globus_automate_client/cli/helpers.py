import json
from typing import Any, Callable, Mapping, Optional, Union

import typer
import yaml
from globus_sdk import GlobusHTTPResponse

from globus_automate_client.cli.constants import InputFormat

verbosity_option = typer.Option(
    False, "--verbose", "-v", help="Run with increased verbosity", show_default=False
)


def default_json_dumper(result, *args, **kwargs):
    return json.dumps(result, indent=4, sort_keys=True)


def format_and_echo(
    result: Union[GlobusHTTPResponse, str],
    dumper: Optional[Callable] = default_json_dumper,
    verbose=False,
) -> None:
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
    typer.secho(dumper(result, indent=4, sort_keys=True), fg=color)


def display_http_details(response: GlobusHTTPResponse) -> None:
    formatted_headers = "\n".join(
        f"  {k}: {v}" for k, v in response._data.request.headers.items()
    )
    print(f"Request: {response._data.request.method} {response._data.request.url}")
    print(f"Headers:\n{formatted_headers}")
    print(f"Response: {response._data.status_code}")


def process_input(
    input_arg: str, input_format: InputFormat, error_explanation: str = ""
) -> Union[Mapping[str, Any], None]:
    """
    Turn input strings into dicts per input format type (InputFormat)
    """
    input_dict = None
    if input_format is InputFormat.json:
        try:
            input_dict = json.loads(input_arg)
        except json.JSONDecodeError as e:
            raise typer.BadParameter(f"Invalid JSON{error_explanation}: {e}")
    elif input_format is InputFormat.yaml:
        try:
            input_dict = yaml.safe_load(input_arg)
        except Exception as e:
            raise typer.BadParameter(f"Invalid YAML{error_explanation}: {e}")

    return input_dict
