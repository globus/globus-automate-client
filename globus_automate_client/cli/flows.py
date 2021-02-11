import json
from enum import Enum
from typing import Any, List, Mapping

import typer
import yaml
from globus_sdk import GlobusAPIError, GlobusHTTPResponse

from globus_automate_client.cli.callbacks import (
    flow_input_validator,
    flows_endpoint_envvar_callback,
    input_validator,
    principal_or_all_authenticated_users_validator,
    principal_or_public_validator,
    principal_validator,
    url_validator_callback,
)
from globus_automate_client.cli.constants import InputFormat
from globus_automate_client.cli.helpers import (
    display_http_details,
    format_and_echo,
    process_input,
    verbosity_option,
)
from globus_automate_client.client_helpers import create_flows_client
from globus_automate_client.flows_client import (
    PROD_FLOWS_BASE_URL,
    FlowValidationError,
    validate_flow_definition,
)
from globus_automate_client.graphviz_rendering import (
    graphviz_format,
    state_colors_for_log,
)
from globus_automate_client.token_management import CLIENT_ID


class FlowRole(str, Enum):
    created_by = "created_by"
    visible_to = "visible_to"
    runnable_by = "runnable_by"
    administered_by = "administered_by"


class FlowDisplayFormat(str, Enum):
    json = "json"
    graphviz = "graphviz"
    image = "image"
    yaml = "yaml"


class ActionRole(str, Enum):
    created_by = "created_by"
    monitor_by = "monitor_by"
    manage_by = "manage_by"


class ActionStatus(str, Enum):
    succeeded = "SUCCEEDED"
    failed = "FAILED"
    active = "ACTIVE"
    inactive = "INACTIVE"


def _process_flow_input(flow_input: str, input_format) -> Mapping[str, Any]:
    flow_input_dict = {}

    if flow_input is not None:
        if input_format is InputFormat.json:
            try:
                flow_input_dict = json.loads(flow_input)
            except json.JSONDecodeError as e:
                raise typer.BadParameter(f"Invalid JSON for input schema: {e}")
        elif input_format is InputFormat.yaml:
            try:
                flow_input_dict = yaml.safe_load(flow_input)
            except yaml.YAMLError as e:
                raise typer.BadParameter(f"Invalid YAML for input schema: {e}")

    return flow_input_dict


app = typer.Typer(short_help="Manage Globus Automate Flows")


@app.callback()
def flows():
    """
    Manage Globus Automate Flows

    To target a different Flows service endpoint, export the
    GLOBUS_AUTOMATE_FLOWS_ENDPOINT environment variable.
    """


@app.command("deploy")
def flow_deploy(
    title: str = typer.Option(..., help="The Flow's title.", prompt=True),
    definition: str = typer.Option(
        ...,
        help=(
            "JSON or YAML representation of the Flow to deploy. May be provided as a filename "
            "or a raw string representing a JSON object or YAML definition."
        ),
        prompt=True,
        callback=input_validator,
    ),
    subtitle: str = typer.Option(
        None,
        help="A subtitle for the Flow providing additional, brief description.",
    ),
    description: str = typer.Option(
        None, help="A long form description of the Flow's purpose or usage."
    ),
    input_schema: str = typer.Option(
        None,
        help=(
            "A JSON or YAML representation of a JSON Schema which will be used to "
            "validate the input to the deployed Flow when it is run. "
            "If not provided, no validation will be performed on Flow input. "
            "May be provided as a filename or a raw string."
        ),
        callback=input_validator,
    ),
    keywords: List[str] = typer.Option(
        None,
        "--keyword",
        help="A keyword which may categorize or help discover the Flow. [repeatable]",
    ),
    visible_to: List[str] = typer.Option(
        None,
        help=(
            "A principal which may see the existence of the deployed Flow. The "
            'special value of "public" may be used to control which users can '
            "discover this flow. [repeatable]"
        ),
        callback=principal_or_public_validator,
    ),
    administered_by: List[str] = typer.Option(
        None,
        help="A principal which may update the deployed Flow. [repeatable]",
        callback=principal_validator,
    ),
    runnable_by: List[str] = typer.Option(
        None,
        help=(
            "A principal which may run an instance of the deployed Flow. The special "
            'value of "all_authenticated_users" may be used to control which users '
            "can invoke this flow. [repeatable]"
        ),
        callback=principal_or_all_authenticated_users_validator,
    ),
    validate: bool = typer.Option(
        True,
        help=("(EXPERIMENTAL) Perform rudimentary validation of the flow definition."),
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL,
        hidden=True,
        callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
    input_format: InputFormat = typer.Option(
        InputFormat.json,
        "--input",
        "-i",
        help="Input format.",
        case_sensitive=False,
        show_default=True,
    ),
):
    """
    Deploy a new Flow.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flow_dict = process_input(definition, input_format)
    input_schema_dict = process_input(input_schema, input_format, " for input schema")

    try:
        result = fc.deploy_flow(
            flow_dict,
            title,
            subtitle,
            description,
            keywords,
            visible_to,
            runnable_by,
            administered_by,
            input_schema_dict,
            validate_definition=validate,
        )
    except GlobusAPIError as err:
        result = err
    format_and_echo(result, input_format.get_dumper(), verbose=verbose)


@app.command("update")
def flow_update(
    flow_id: str = typer.Argument(...),
    title: str = typer.Option(None, help="The Flow's title."),
    definition: str = typer.Option(
        None,
        help=(
            "JSON or YAML representation of the Flow to update. May be provided as a filename "
            "or a raw string."
        ),
        callback=input_validator,
    ),
    subtitle: str = typer.Option(
        None,
        help="A subtitle for the Flow providing additional, brief description.",
    ),
    description: str = typer.Option(
        None, help="A long form description of the Flow's purpose or usage."
    ),
    input_schema: str = typer.Option(
        None,
        help=(
            "A JSON or YAML representation of a JSON Schema which will be used to "
            "validate the input to the deployed Flow when it is run. "
            "If not provided, no validation will be performed on Flow input. "
            "May be provided as a filename or a raw string."
        ),
        callback=input_validator,
    ),
    keywords: List[str] = typer.Option(
        None,
        "--keyword",
        help="A keyword which may categorize or help discover the Flow. [repeatable]",
    ),
    visible_to: List[str] = typer.Option(
        None,
        help=(
            "A principal which may see the existence of the deployed Flow. The "
            'special value of "public" may be used to control which users can '
            "discover this flow. [repeatable]"
        ),
        callback=principal_or_public_validator,
    ),
    administered_by: List[str] = typer.Option(
        None,
        help="A principal which may update the deployed Flow. [repeatable]",
        callback=principal_validator,
    ),
    runnable_by: List[str] = typer.Option(
        None,
        help=(
            "A principal which may run an instance of the deployed Flow. The special "
            'value of "all_authenticated_users" may be used to control which users '
            "can invoke this flow. [repeatable]"
        ),
        callback=principal_or_all_authenticated_users_validator,
    ),
    validate: bool = typer.Option(
        True,
        help=("(EXPERIMENTAL) Perform rudimentary validation of the flow definition."),
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL,
        hidden=True,
        callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
    input_format: InputFormat = typer.Option(
        InputFormat.json,
        "--input",
        "-i",
        help="Input format.",
        case_sensitive=False,
        show_default=True,
    ),
):
    """
    Update a Flow.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flow_dict = process_input(definition, input_format)
    input_schema_dict = process_input(input_schema, input_format, " for input schema")

    try:
        result = fc.update_flow(
            flow_id,
            flow_dict,
            title,
            subtitle,
            description,
            keywords,
            visible_to,
            runnable_by,
            administered_by,
            input_schema_dict,
            validate_definition=validate,
        )
    except GlobusAPIError as err:
        result = err
    if result is None:
        result = "No operation to perform"
    format_and_echo(result, input_format.get_dumper(), verbose=verbose)


@app.command("lint")
def flow_lint(
    definition: str = typer.Option(
        ...,
        help=(
            "JSON or YAML representation of the Flow to deploy. May be provided as a filename "
            "or a raw string."
        ),
        prompt=True,
        callback=input_validator,
    ),
    validate: bool = typer.Option(
        True,
        help=("(EXPERIMENTAL) Perform rudimentary validation of the flow definition."),
        case_sensitive=False,
        show_default=True,
    ),
    output_format: FlowDisplayFormat = typer.Option(
        FlowDisplayFormat.json,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
    input_format: InputFormat = typer.Option(
        InputFormat.json,
        "--input",
        "-i",
        help="Input format.",
        case_sensitive=False,
        show_default=True,
    ),
):
    """
    Parse and validate a Flow definition by providing visual output.
    """
    flow_dict = process_input(definition, input_format)

    try:
        if validate:
            validate_flow_definition(flow_dict)
    except FlowValidationError as fve:
        typer.secho(str(fve), fg=typer.colors.RED)
        raise typer.Exit(code=1)

    graph = graphviz_format(flow_dict)
    if output_format is FlowDisplayFormat.json:
        format_and_echo(flow_dict)
    elif output_format is FlowDisplayFormat.yaml:
        format_and_echo(flow_dict, yaml.dump)
    elif output_format is FlowDisplayFormat.graphviz:
        typer.echo(graph.source)
    else:
        graph.render("flows-output/graph", view=True, cleanup=True)


@app.command("list")
def flow_list(
    roles: List[FlowRole] = typer.Option(
        [FlowRole.created_by],
        "--role",
        "-r",
        help="Display Flows where you have the selected role. [repeatable]",
        case_sensitive=False,
        show_default=True,
    ),
    marker: str = typer.Option(
        None,
        "--marker",
        "-m",
        help="A pagination token for iterating through returned data.",
    ),
    per_page: int = typer.Option(
        None,
        "--per-page",
        "-p",
        help="The page size to return. Only valid when used without providing a marker.",
        min=1,
        max=50,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL,
        hidden=True,
        callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
    output_format: FlowDisplayFormat = typer.Option(
        FlowDisplayFormat.json,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
):
    """
    List Flows for which you have access.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    try:
        flows = fc.list_flows(
            roles=[r.value for r in roles], marker=marker, per_page=per_page
        )
    except GlobusAPIError as err:
        format_and_echo(err, verbose=verbose)
    else:
        _format_and_display_flow(flows, output_format, verbose=verbose)


@app.command("display")
def flow_display(
    flow_id: str = typer.Argument(...),
    output_format: FlowDisplayFormat = typer.Option(
        FlowDisplayFormat.json,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL,
        hidden=True,
        callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Display a deployed Flow. You must have either created the Flow or
    be present in the Flow's "visible_to" list to view it.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    try:
        flow_get = fc.get_flow(flow_id)
    except GlobusAPIError as err:
        format_and_echo(err, verbose=verbose)
    else:
        _format_and_display_flow(flow_get, output_format, verbose=verbose)


@app.command("delete")
def flow_delete(
    flow_id: str = typer.Argument(...),
    output_format: FlowDisplayFormat = typer.Option(
        FlowDisplayFormat.json,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL,
        hidden=True,
        callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Delete a Flow. You must either have created the Flow
    or be in the Flow's "administered_by" list.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    try:
        flow_del = fc.delete_flow(flow_id)
    except GlobusAPIError as err:
        format_and_echo(err, verbose=verbose)
    else:
        _format_and_display_flow(flow_del, output_format, verbose=verbose)


@app.command("run")
def flow_run(
    flow_id: str = typer.Argument(...),
    flow_input: str = typer.Option(
        None,
        help=(
            "JSON or YAML formatted input to the Flow. May be provided as a filename "
            "or a raw string."
        ),
        callback=flow_input_validator,
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL,
        hidden=True,
        callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
    output_format: FlowDisplayFormat = typer.Option(
        FlowDisplayFormat.json,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
    input_format: InputFormat = typer.Option(
        InputFormat.json,
        "--input",
        "-i",
        help="Input format.",
        case_sensitive=False,
        show_default=True,
    ),
    label: str = typer.Option(
        None,
        "--label",
        "-l",
        help="Optional label to mark this run.",
    )
):
    """
    Run an instance of a Flow. The argument provides the initial state of the Flow.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flow_input_dict = _process_flow_input(flow_input, input_format)

    try:
        response = fc.run_flow(flow_id, flow_scope, flow_input_dict, label=label)
    except GlobusAPIError as err:
        format_and_echo(err, verbose=verbose)
    else:
        _format_and_display_flow(response, output_format, verbose=verbose)


@app.command("action-list")
def flow_actions_list(
    flow_id: str = typer.Option(
        ...,
        help="The ID for the Flow which triggered the Action.",
        prompt=True,
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    roles: List[ActionRole] = typer.Option(
        None,
        "--role",
        help="Display Actions where you have the selected role. [repeatable]",
    ),
    statuses: List[ActionStatus] = typer.Option(
        None,
        "--status",
        help="Display Actions with the selected status. [repeatable]",
    ),
    marker: str = typer.Option(
        None,
        "--marker",
        "-m",
        help="A pagination token for iterating through returned data.",
    ),
    per_page: int = typer.Option(
        None,
        "--per-page",
        "-p",
        help="The page size to return. Only valid when used without providing a marker.",
        min=1,
        max=50,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL,
        hidden=True,
        callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    List a Flow definition's discrete invocations.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)

    # This None check and check makes me unhappy but is necessary for mypy to
    # be happy with the enums. If we can figure out what defaults flows uses
    # for flow role/status queries, we can set those here and be done
    statuses_str, roles_str = None, None
    if statuses is not None:
        statuses_str = [s.value for s in statuses]
    if roles is not None:
        roles_str = [r.value for r in roles]

    try:
        result = fc.list_flow_actions(
            flow_id,
            flow_scope,
            statuses=statuses_str,
            roles=roles_str,
            marker=marker,
            per_page=per_page,
        )
    except GlobusAPIError as err:
        result = err
    format_and_echo(result, verbose=verbose)


@app.command("action-status")
def flow_action_status(
    action_id: str = typer.Argument(...),
    flow_id: str = typer.Option(
        ...,
        help="The ID for the Flow which triggered the Action.",
        prompt=True,
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL,
        hidden=True,
        callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Display the status for a Flow definition's particular invocation.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    try:
        result = fc.flow_action_status(flow_id, flow_scope, action_id)
    except GlobusAPIError as err:
        result = err
    format_and_echo(result, verbose=verbose)


@app.command("action-release")
def flow_action_release(
    action_id: str = typer.Argument(...),
    flow_id: str = typer.Option(
        ...,
        help="The ID for the Flow which triggered the Action.",
        prompt=True,
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL,
        hidden=True,
        callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Remove execution history for a particular Flow definition's invocation.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    try:
        result = fc.flow_action_release(flow_id, flow_scope, action_id)
    except GlobusAPIError as err:
        result = err
    format_and_echo(result, verbose=verbose)


@app.command("action-cancel")
def flow_action_cancel(
    action_id: str = typer.Argument(...),
    flow_id: str = typer.Option(
        ...,
        help="The ID for the Flow which triggered the Action.",
        prompt=True,
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL,
        hidden=True,
        callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Cancel an active execution for a particular Flow definition's invocation.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    try:
        result = fc.flow_action_cancel(flow_id, flow_scope, action_id)
    except GlobusAPIError as err:
        result = err
    format_and_echo(result, verbose=verbose)


@app.command("action-log")
def flow_action_log(
    action_id: str = typer.Argument(...),
    flow_id: str = typer.Option(
        ...,
        help="The ID for the Flow which triggered the Action.",
        prompt=True,
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    reverse: bool = typer.Option(
        # Defaulting to any boolean value will reverse output - so we use None
        None,
        "--reverse",
        help="Display logs starting from most recent and proceeding in reverse chronological order",
    ),
    limit: int = typer.Option(
        None,
        help="Set a maximum number of events from the log to return",
        min=0,
        max=100,
    ),
    marker: str = typer.Option(
        None,
        "--marker",
        "-m",
        help="A pagination token for iterating through returned data.",
    ),
    per_page: int = typer.Option(
        None,
        "--per-page",
        "-p",
        help="The page size to return. Only valid when used without providing a marker.",
        min=1,
        max=50,
    ),
    output_format: FlowDisplayFormat = typer.Option(
        FlowDisplayFormat.json,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL,
        hidden=True,
        callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Get a log of the steps executed by a Flow definition's invocation.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)

    try:
        resp = fc.flow_action_log(
            flow_id, flow_scope, action_id, limit, reverse, marker, per_page
        )
    except GlobusAPIError as err:
        format_and_echo(err, verbose=verbose)
        raise typer.Exit(code=1)

    if verbose:
        display_http_details(resp)

    if output_format in (FlowDisplayFormat.json, FlowDisplayFormat.yaml):
        _format_and_display_flow(resp, output_format, verbose)
    elif output_format in (FlowDisplayFormat.graphviz, FlowDisplayFormat.image):
        flow_def_resp = fc.get_flow(flow_id)
        flow_def = flow_def_resp.data["definition"]
        colors = state_colors_for_log(resp.data["entries"])
        graphviz_out = graphviz_format(flow_def, colors)

        if output_format == FlowDisplayFormat.graphviz:
            typer.echo(graphviz_out.source)
        else:
            graphviz_out.render("flows-output/graph", view=True, cleanup=True)


def _format_and_display_flow(
    flow_resp: GlobusHTTPResponse, output_format: FlowDisplayFormat, verbose=False
):
    """
    Diplays a flow as either JSON, graphviz, or an image
    """
    if verbose:
        display_http_details(flow_resp)

    if output_format is FlowDisplayFormat.json:
        format_and_echo(flow_resp, json.dumps)
    elif output_format is FlowDisplayFormat.yaml:
        format_and_echo(flow_resp, yaml.dump)
    elif output_format in (FlowDisplayFormat.graphviz, FlowDisplayFormat.image):
        graphviz_out = graphviz_format(flow_resp.data["definition"])
        if output_format == FlowDisplayFormat.graphviz:
            typer.echo(graphviz_out.source)
        else:
            graphviz_out.render("flows-output/graph", view=True, cleanup=True)


if __name__ == "__main__":
    app()
