import json
from typing import Any, Callable, Mapping, Union

import typer
import yaml
from globus_sdk import GlobusAPIError, GlobusHTTPResponse

from globus_automate_client.cli.constants import InputFormat

verbosity_option = typer.Option(
    False, "--verbose", "-v", help="Run with increased verbosity", show_default=False
)


def default_json_dumper(result, *args, **kwargs):
    return json.dumps(result, indent=4, sort_keys=True)


def format_and_echo(
    result: Union[GlobusHTTPResponse, str, GlobusAPIError],
    dumper: Callable = default_json_dumper,
    verbose=False,
) -> None:
    if verbose:
        display_http_details(result)

    if isinstance(result, GlobusHTTPResponse):
        if 200 <= result.http_status < 300:
            color = typer.colors.GREEN
        else:
            color = typer.colors.RED
        result = result.data
    elif isinstance(result, GlobusAPIError):
        color = typer.colors.RED
        result = result.raw_json if result.raw_json else result.raw_text
    else:
        color = typer.colors.GREEN
    typer.secho(dumper(result, indent=4, sort_keys=True), fg=color)


def display_http_details(result: Union[GlobusHTTPResponse, GlobusAPIError]) -> None:
    if isinstance(result, GlobusHTTPResponse):
        base_request = result._data.request
        reponse_status_code = result._data.status_code
    if isinstance(result, GlobusAPIError):
        base_request = result._underlying_response.request
        reponse_status_code = result._underlying_response.status_code

    formatted_headers = "\n".join(
        f"  {k}: {v}" for k, v in base_request.headers.items()
    )
    typer.echo(f"Request: {base_request.method} {base_request.url}", err=True)
    typer.echo(f"Headers:\n{formatted_headers}", err=True)
    typer.echo(f"Response: {reponse_status_code}", err=True)


def process_input(
    input_arg: Union[str, None], input_format: InputFormat, error_explanation: str = ""
) -> Union[Mapping[str, Any], None]:
    """
    Turn input strings into dicts per input format type (InputFormat)
    """

    if input_arg is None:
        return None

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
