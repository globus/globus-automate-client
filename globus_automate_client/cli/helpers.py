import json
import time
from typing import Any, Callable, Dict, List, Mapping, Optional, Union

import typer
import yaml
from globus_sdk import GlobusAPIError, GlobusHTTPResponse
from rich.text import Text

from globus_automate_client.cli.constants import InputFormat, OutputFormat
from globus_automate_client.cli.rich_rendering import cli_content

GlobusCallable = Callable[[], GlobusHTTPResponse]
GlobusAPIResponse = Union[GlobusAPIError, GlobusHTTPResponse]

verbosity_option = typer.Option(
    False, "--verbose", "-v", help="Run with increased verbosity", show_default=False
)


def get_renderable_response(
    result: Union[GlobusHTTPResponse, str, GlobusAPIError],
    dumper: Callable = OutputFormat.json.get_dumper(),
    verbose: bool = False,
) -> Text:
    text = Text()

    if verbose:
        verbose_output = get_http_details(result)
        text.append(f"{verbose_output}\n\n", style="bright_cyan")

    if isinstance(result, GlobusHTTPResponse):
        result = result.data
        style = "green"
    elif isinstance(result, GlobusAPIError):
        result = result.raw_json if result.raw_json else result.raw_text
        style = "red"
    else:
        result = result

    text.append(dumper(result), style=style)
    return text


def request_runner(
    operation: GlobusCallable, output_format, verbose: bool, follow: bool
) -> GlobusAPIResponse:
    """
    This function takes an operation and executes it until it returns a
    completed Action state or a GlobusAPIError. On each execution, it will
    display the results of the query while keeping track of how much output was
    produced. Using this information, it will clear the previous number of lines
    from stdout before displaying updated results.
    """
    dumper = output_format.get_dumper()
    terminal_statuses = {"SUCCEEDED", "FAILED"}
    cli_content.init()

    while True:
        if cli_content.time_to_update():
            try:
                result = operation()
            except GlobusAPIError as err:
                result = err

            text = get_renderable_response(result, dumper, verbose)
            cli_content.update(text)
            if (
                not follow
                or isinstance(result, GlobusAPIError)
                or result.data["status"] in terminal_statuses
            ):
                break
        else:
            time.sleep(1)

    cli_content.complete()
    return result


# TODO Any way to refactor this?
def flow_log_runner(
    operation: GlobusCallable, output_format, verbose: bool, follow: bool
) -> GlobusAPIResponse:
    dumper = output_format.get_dumper()
    terminal_statuses = {"FlowSucceeded", "FlowFailed", "FlowCanceled"}
    cli_content.init()

    while True:
        if cli_content.time_to_update():
            try:
                result = operation()
            except GlobusAPIError as err:
                result = err

            text = get_flow_renderable_response(result, dumper, verbose)
            cli_content.update(text)
            if (
                not follow
                or isinstance(result, GlobusAPIError)
                or result.data["entries"][-1]["code"] in terminal_statuses
            ):
                break
        else:
            time.sleep(1)

    cli_content.complete()
    return result


def get_flow_renderable_response(
    result: Union[GlobusHTTPResponse, str, GlobusAPIError],
    dumper: Callable = OutputFormat.json.get_dumper(),
    verbose: bool = False,
) -> Text:
    text = Text()

    if verbose:
        verbose_output = get_http_details(result)
        text.append(f"{verbose_output}\n\n", style="bright_cyan")

    if isinstance(result, GlobusHTTPResponse):
        result = result.data["entries"][-1]
        style = "green"
    elif isinstance(result, GlobusAPIError):
        result = result.raw_json if result.raw_json else result.raw_text
        style = "red"
    else:
        result = result

    text.append(dumper(result), style=style)
    return text


def format_and_echo(
    result: Union[GlobusHTTPResponse, str, GlobusAPIError],
    dumper: Callable = OutputFormat.json.get_dumper(),
    verbose=False,
):
    if verbose:
        typer.secho(
            f"{get_http_details(result)}\n", fg=typer.colors.BRIGHT_CYAN, err=True
        )

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

    typer.secho(dumper(result), fg=color)


def get_http_details(result: Union[GlobusHTTPResponse, GlobusAPIError]) -> str:
    if isinstance(result, GlobusHTTPResponse):
        base_request = result._data.request
        reponse_status_code = result._data.status_code
    if isinstance(result, GlobusAPIError):
        base_request = result._underlying_response.request
        reponse_status_code = result._underlying_response.status_code

    formatted_headers = "\n".join(
        f"  {k}: {v}" for k, v in base_request.headers.items()
    )
    http_details = f"Request: {base_request.method} {base_request.url}\n"
    http_details += f"Headers:\n{formatted_headers}\n"
    http_details += f"Response: {reponse_status_code}"
    return http_details


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


def parse_query_options(queries: Optional[List[str]]) -> Dict[str, str]:
    result: Dict[str, str] = {}

    if queries is None:
        return result

    for q in queries:
        try:
            field, pattern = q.split("=")
        except ValueError:
            raise typer.BadParameter(
                f"Issue parsing '{q}'. Options should be of the form 'field=pattern'."
            )
        if pattern == "":
            raise typer.BadParameter(f"Issue parsing '{q}'. Missing pattern.")
        result[field] = pattern
    return result
