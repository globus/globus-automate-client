import json
from enum import Enum
from typing import List

import typer
from globus_sdk import GlobusHTTPResponse

from globus_automate_client.cli.callbacks import (
    flows_endpoint_envvar_callback,
    json_validator_callback,
    principal_validator_callback,
    url_validator_callback,
)
from globus_automate_client.cli.helpers import (
    display_http_details,
    format_and_echo,
    verbosity_option,
)
from globus_automate_client.flows_client import (
    PROD_FLOWS_BASE_URL,
    FlowValidationError,
    create_flows_client,
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


class ActionRole(str, Enum):
    created_by = "created_by"
    monitor_by = "monitor_by"
    manage_by = "manage_by"


class ActionStatus(str, Enum):
    succeeded = "SUCCEEDED"
    failed = "FAILED"
    active = "ACTIVE"
    inactive = "INACTIVE"


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
            "JSON representation of the Flow to deploy. May be provided as a filename "
            "or a raw JSON string."
        ),
        prompt=True,
        callback=json_validator_callback,
    ),
    subtitle: str = typer.Option(
        None, help="A subtitle for the Flow providing additional, brief description.",
    ),
    description: str = typer.Option(
        None, help="A long form description of the Flow's purpose or usage."
    ),
    input_schema: str = typer.Option(
        None,
        help=(
            "A JSON representation of a JSON Schema which will be used to "
            "validate the input to the deployed Flow when it is run. "
            "If not provided, no validation will be performed on Flow input. "
            "May be provided as a filename or a raw JSON string."
        ),
        callback=json_validator_callback,
    ),
    keywords: List[str] = typer.Option(
        None,
        "--keyword",
        help="A keyword which may categorize or help discover the Flow. [repeatable]",
    ),
    visible_to: List[str] = typer.Option(
        None,
        help="A principal which may see the existence of deployed Flow. [repeatable]",
        callback=principal_validator_callback,
    ),
    administered_by: List[str] = typer.Option(
        None,
        help="A principal which may update the deployed Flow. [repeatable]",
        callback=principal_validator_callback,
    ),
    runnable_by: List[str] = typer.Option(
        None,
        help="A principal which may run an instance of the deployed Flow. [repeatable]",
        callback=principal_validator_callback,
    ),
    validate: bool = typer.Option(
        True,
        help=("(EXPERIMENTAL) Perform rudimentary validation of the flow definition."),
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL, hidden=True, callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Deploy a new Flow.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flow_dict = json.loads(definition)
    if input_schema is not None:
        input_schema_dict = json.loads(input_schema)
    else:
        input_schema_dict = None
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
    format_and_echo(result, verbose=verbose)


@app.command("update")
def flow_update(
    flow_id: str = typer.Argument(...),
    title: str = typer.Option(None, help="The Flow's title."),
    definition: str = typer.Option(
        None,
        help=(
            "JSON representation of the Flow to update. May be provided as a filename "
            "or a raw JSON string."
        ),
        callback=json_validator_callback,
    ),
    subtitle: str = typer.Option(
        None, help="A subtitle for the Flow providing additional, brief description.",
    ),
    description: str = typer.Option(
        None, help="A long form description of the Flow's purpose or usage."
    ),
    input_schema: str = typer.Option(
        None,
        help=(
            "A JSON representation of a JSON Schema which will be used to "
            "validate the input to the deployed Flow when it is run. "
            "If not provided, no validation will be performed on Flow input. "
            "May be provided as a filename or a raw JSON string."
        ),
        callback=json_validator_callback,
    ),
    keywords: List[str] = typer.Option(
        None,
        "--keyword",
        help="A keyword which may categorize or help discover the Flow. [repeatable]",
    ),
    visible_to: List[str] = typer.Option(
        None,
        help="A principal which may see the existence of deployed Flow. [repeatable]",
        callback=principal_validator_callback,
    ),
    administered_by: List[str] = typer.Option(
        None,
        help="A principal which may update the deployed Flow. [repeatable]",
        callback=principal_validator_callback,
    ),
    runnable_by: List[str] = typer.Option(
        None,
        help="A principal which may run an instance of the deployed Flow. [repeatable]",
        callback=principal_validator_callback,
    ),
    validate: bool = typer.Option(
        True,
        help=("(EXPERIMENTAL) Perform rudimentary validation of the flow definition."),
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL, hidden=True, callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Update a Flow.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flow_dict = json.loads(definition)
    if input_schema is not None:
        input_schema_dict = json.loads(input_schema)
    else:
        input_schema_dict = None
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
    if result is not None:
        format_and_echo(result, verbose=verbose)
    else:
        print("No operation to perform")


@app.command("lint")
def flow_lint(
    definition: str = typer.Option(
        ...,
        help=(
            "JSON representation of the Flow to deploy. May be provided as a filename "
            "or a raw JSON string."
        ),
        prompt=True,
        callback=json_validator_callback,
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
):
    """
    Parse and validate a Flow definition by providing visual output.
    """
    flow_dict = json.loads(definition)
    try:
        if validate:
            validate_flow_definition(flow_dict)
    except FlowValidationError as fve:
        typer.secho(str(fve), fg=typer.colors.RED)
        raise typer.Exit(code=1)
    graph = graphviz_format(flow_dict)
    if output_format == FlowDisplayFormat.json:
        format_and_echo(flow_dict)
    elif output_format == FlowDisplayFormat.graphviz:
        typer.echo(graph.source)
    else:
        graph.render(f"flows-output/graph", view=True, cleanup=True)


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
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL, hidden=True, callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    List Flows for which you have access.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flows = fc.list_flows(roles=[r.value for r in roles])
    format_and_echo(flows, verbose=verbose)


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
        PROD_FLOWS_BASE_URL, hidden=True, callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Display a deployed Flow. You must have either created the Flow or
    be present in the Flow's "visible_to" list to view it.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flow_get = fc.get_flow(flow_id)
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
        PROD_FLOWS_BASE_URL, hidden=True, callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Delete a Flow. You must either have created the Flow
    or be in the Flow's "administered_by" list.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flow_del = fc.delete_flow(flow_id)
    _format_and_display_flow(flow_del, output_format, verbose=verbose)


@app.command("run")
def flow_run(
    flow_id: str = typer.Argument(...),
    flow_input: str = typer.Option(
        None,
        help=(
            "JSON formatted input to the Flow. May be provided as a filename "
            "or a raw JSON string."
        ),
        callback=json_validator_callback,
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL, hidden=True, callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Run an instance of a Flow. The argument provides the initial state of the Flow.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    if flow_input is not None:
        flow_input_dict = json.loads(flow_input)
    else:
        flow_input_dict = {}
    response = fc.run_flow(flow_id, flow_scope, flow_input_dict)
    format_and_echo(response, verbose=verbose)


@app.command("action-list")
def flow_actions_list(
    flow_id: str = typer.Option(
        ..., help="The ID for the Flow which triggered the Action.", prompt=True,
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
        None, "--status", help="Display Actions with the selected status. [repeatable]",
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL, hidden=True, callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    List the Actions associated with a Flow.
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

    action_list = fc.list_flow_actions(
        flow_id, flow_scope, statuses=statuses_str, roles=roles_str
    )
    format_and_echo(action_list, verbose=verbose)


@app.command("action-status")
def flow_action_status(
    action_id: str = typer.Argument(...),
    flow_id: str = typer.Option(
        ..., help="The ID for the Flow which triggered the Action.", prompt=True,
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL, hidden=True, callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Retrieve a Flow's Action's status.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    response = fc.flow_action_status(flow_id, flow_scope, action_id)
    format_and_echo(response, verbose=verbose)


@app.command("action-release")
def flow_action_release(
    action_id: str = typer.Argument(...),
    flow_id: str = typer.Option(
        ..., help="The ID for the Flow which triggered the Action.", prompt=True,
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL, hidden=True, callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Retrieve a Flow's Action's status.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    response = fc.flow_action_release(flow_id, flow_scope, action_id)
    format_and_echo(response, verbose=verbose)


@app.command("action-cancel")
def flow_action_cancel(
    action_id: str = typer.Argument(...),
    flow_id: str = typer.Option(
        ..., help="The ID for the Flow which triggered the Action.", prompt=True,
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    flows_endpoint: str = typer.Option(
        PROD_FLOWS_BASE_URL, hidden=True, callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Retrieve a Flow's Action's status.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    response = fc.flow_action_cancel(flow_id, flow_scope, action_id)
    format_and_echo(response, verbose=verbose)


@app.command("action-log")
def flow_action_log(
    action_id: str = typer.Argument(...),
    flow_id: str = typer.Option(
        ..., help="The ID for the Flow which triggered the Action.", prompt=True,
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
        None, help="Set a maximum number of events from the log to return", min=0,
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
        PROD_FLOWS_BASE_URL, hidden=True, callback=flows_endpoint_envvar_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Get a log of the steps executed by a Flow's Action.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    resp = fc.flow_action_log(flow_id, flow_scope, action_id, limit, reverse)

    if verbose:
        display_http_details(resp)

    if output_format == FlowDisplayFormat.json:
        format_and_echo(resp)
    elif output_format in (FlowDisplayFormat.graphviz, FlowDisplayFormat.image):
        flow_def_resp = fc.get_flow(flow_id)
        flow_def = flow_def_resp.data["definition"]
        colors = state_colors_for_log(resp.data["entries"])
        graphviz_out = graphviz_format(flow_def, colors)

        if output_format == FlowDisplayFormat.graphviz:
            typer.echo(graphviz_out.source)
        else:
            graphviz_out.render(f"flows-output/graph", view=True, cleanup=True)


def _format_and_display_flow(
    flow_resp: GlobusHTTPResponse, output_format: FlowDisplayFormat, verbose=False
):
    """
    Diplays a flow as either JSON, graphviz, or an image
    """
    if verbose:
        display_http_details(flow_resp)

    if output_format == FlowDisplayFormat.json:
        format_and_echo(flow_resp)
    elif output_format in (FlowDisplayFormat.graphviz, FlowDisplayFormat.image):
        graphviz_out = graphviz_format(flow_resp.data["definition"])
        if output_format == FlowDisplayFormat.graphviz:
            typer.echo(graphviz_out.source)
        else:
            graphviz_out.render(f"flows-output/graph", view=True, cleanup=True)


if __name__ == "__main__":
    app()
