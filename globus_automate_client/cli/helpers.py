import json
from typing import Any, Callable, Dict, List, Mapping, Optional, Union

import requests
import typer
import yaml
from globus_sdk import GlobusAPIError, GlobusHTTPResponse

from globus_automate_client.cli.callbacks import flows_endpoint_envvar_callback
from globus_automate_client.cli.constants import (
    ActionRoleAllNames,
    FlowRoleAllNames,
    OutputFormat,
)

GlobusCallable = Callable[[], GlobusHTTPResponse]
GlobusAPIResponse = Union[GlobusAPIError, GlobusHTTPResponse]

verbosity_option = typer.Option(
    False, "--verbose", "-v", help="Run with increased verbosity", show_default=False
)

flows_env_var_option = typer.Option(
    None,
    hidden=True,
    callback=flows_endpoint_envvar_callback,
)

output_format_option: OutputFormat = typer.Option(
    OutputFormat.json,
    "--format",
    "-f",
    help="Output display format.",
    case_sensitive=False,
    show_default=True,
)


def get_http_details(result: Union[GlobusHTTPResponse, GlobusAPIError]) -> str:
    if isinstance(result, GlobusHTTPResponse):
        if isinstance(result._response, requests.Response):
            base_request = result._response.request
        elif result._wrapped and isinstance(
            result._wrapped._response, requests.Response
        ):
            base_request = result._wrapped._response.request
        else:
            return "HTTP details are unavailable"
        response_status_code = result.http_status
    else:  # isinstance(result, GlobusAPIError)
        base_request = result._underlying_response.request
        response_status_code = result._underlying_response.status_code

    formatted_headers = "\n".join(
        f"  {k}: {v}" for k, v in base_request.headers.items()
    )
    http_details = (
        f"Request: {base_request.method} {base_request.url}\n"
        f"Headers:\n{formatted_headers}\n"
        f"Response: {response_status_code}"
    )
    return http_details


def process_input(input_arg: Optional[str]) -> Optional[Mapping[str, Any]]:
    """
    Turn input strings into dicts
    """
    if input_arg is None:
        return None

    try:
        input_dict = json.loads(input_arg)
    except json.JSONDecodeError:
        try:
            input_dict = yaml.safe_load(input_arg)
        except yaml.YAMLError:
            raise typer.BadParameter("Unable to load input as JSON or YAML")

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


def make_role_param(
    roles_list: Optional[Union[List[FlowRoleAllNames], List[ActionRoleAllNames]]]
) -> Mapping[str, Any]:
    if roles_list is None or len(roles_list) == 0:
        return {"role": None}
    elif len(roles_list) == 1:
        return {"role": roles_list[0].value}
    else:
        typer.secho(
            "Warning: Use of multiple --role options is deprecated",
            err=True,
            fg=typer.colors.YELLOW,
        )
        return {"roles": [r.value for r in roles_list]}
