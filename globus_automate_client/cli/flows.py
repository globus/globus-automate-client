import functools
import json
from enum import Enum
from typing import Any, List, Mapping, Optional, Union

import typer
import yaml
from globus_sdk import GlobusAPIError, GlobusHTTPResponse

from globus_automate_client.cli.auth import CLIENT_ID
from globus_automate_client.cli.callbacks import (
    flow_input_validator,
    flows_endpoint_envvar_callback,
    input_validator,
    principal_or_all_authenticated_users_validator,
    principal_or_public_validator,
    principal_validator,
    url_validator_callback,
)
from globus_automate_client.cli.constants import (
    FlowDisplayFormat,
    InputFormat,
    OutputFormat,
)
from globus_automate_client.cli.helpers import (
    flow_log_runner,
    format_and_echo,
    parse_query_options,
    process_input,
    request_runner,
    verbosity_option,
)
from globus_automate_client.cli.rich_rendering import live_content
from globus_automate_client.client_helpers import create_flows_client
from globus_automate_client.flows_client import (
    FlowValidationError,
    validate_flow_definition,
)
from globus_automate_client.graphviz_rendering import graphviz_format


class FlowRole(str, Enum):
    created_by = "created_by"
    visible_to = "visible_to"
    runnable_by = "runnable_by"
    administered_by = "administered_by"


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

_flows_env_var_option = typer.Option(
    None,
    hidden=True,
    callback=flows_endpoint_envvar_callback,
)


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
        help="A principal which may view this Flow. The principal value is the user's "
        "or group's UUID prefixed with either 'urn:globus:groups:id:' or "
        "'urn:globus:auth:identity:'. The special value of 'public' may be used to "
        "indicate that any user can view this Flow. [repeatable]",
        callback=principal_or_public_validator,
    ),
    administered_by: List[str] = typer.Option(
        None,
        help="A principal which may update the deployed Flow. The principal value is the "
        "user's or group's UUID prefixed with either 'urn:globus:groups:id:' or "
        "'urn:globus:auth:identity:'. [repeatable]",
        callback=principal_validator,
    ),
    runnable_by: List[str] = typer.Option(
        None,
        help="A principal which may run an instance of the deployed Flow. The principal "
        "value is the user's or group's UUID prefixed with either "
        "'urn:globus:groups:id:' or 'urn:globus:auth:identity:'. The special value of "
        "'all_authenticated_users' may be used to indicate that any authenticated user "
        "can invoke this flow. [repeatable]",
        callback=principal_or_all_authenticated_users_validator,
    ),
    subscription_id: Optional[str] = typer.Option(
        None,
        help="The Globus Subscription which will be used to make this flow managed.",
    ),
    validate: bool = typer.Option(
        True,
        help=("(EXPERIMENTAL) Perform rudimentary validation of the flow definition."),
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = _flows_env_var_option,
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
            subscription_id,
            input_schema_dict,
            validate_definition=validate,
        )
    except GlobusAPIError as err:
        result = err
    format_and_echo(result, verbose=verbose)


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
        help="A principal which may view this Flow. The principal value is the user's "
        "or group's UUID prefixed with either 'urn:globus:groups:id:' or "
        "'urn:globus:auth:identity:'. The special value of 'public' may be used to "
        "indicate that any user can view this Flow. [repeatable]",
        callback=principal_or_public_validator,
    ),
    administered_by: List[str] = typer.Option(
        None,
        help="A principal which may update the deployed Flow. The principal value is the "
        "user's or group's UUID prefixed with either 'urn:globus:groups:id:' or "
        "'urn:globus:auth:identity:' [repeatable]",
        callback=principal_validator,
    ),
    runnable_by: List[str] = typer.Option(
        None,
        help="A principal which may run an instance of the deployed Flow. The principal "
        "value is the user's or group's UUID prefixed with either "
        "'urn:globus:groups:id:' or 'urn:globus:auth:identity:'. The special value of "
        "'all_authenticated_users' may be used to indicate that any authenticated user "
        "can invoke this flow. [repeatable]",
        callback=principal_or_all_authenticated_users_validator,
    ),
    subscription_id: Optional[str] = typer.Option(
        None,
        help="The Globus Subscription which will be used to make this flow managed.",
    ),
    validate: bool = typer.Option(
        True,
        help=("(EXPERIMENTAL) Perform rudimentary validation of the flow definition."),
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = _flows_env_var_option,
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
            subscription_id,
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
        validate_flow_definition(flow_dict)
    except FlowValidationError as fve:
        typer.secho(str(fve), fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho("No issues found in the Flow definition.", fg=typer.colors.GREEN)


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
    flows_endpoint: str = _flows_env_var_option,
    filters: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        help="A filtering criteria in the form 'key=value' to apply to the "
        "resulting Flow listing. The key indicates the filter, the value "
        "indicates the pattern to match. Multiple patterns for a single key may "
        "be specified as a comma seperated string, the results for which will "
        "represent a logical OR. If multiple filters are applied, the returned "
        "data will be the result of a logical AND between them. [repeatable]",
    ),
    orderings: Optional[List[str]] = typer.Option(
        None,
        "--orderby",
        help="An ordering criteria in the form 'key=value' to apply to the resulting "
        "Flow listing. The key indicates the field to order on, and the value is "
        "either ASC, for ascending order, or DESC, for descending order. The first "
        "ordering criteria will be used to sort the data, subsequent ordering criteria "
        "will further sort ties. [repeatable]",
    ),
    verbose: bool = verbosity_option,
    output_format: OutputFormat = typer.Option(
        OutputFormat.json,
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
    parsed_filters = parse_query_options(filters)
    parsed_orderings = parse_query_options(orderings)

    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    try:
        response = fc.list_flows(
            roles=[r.value for r in roles],
            marker=marker,
            per_page=per_page,
            filters=parsed_filters,
            orderings=parsed_orderings,
        )
    except GlobusAPIError as err:
        response = err

    format_and_echo(response, output_format.get_dumper(), verbose=verbose)


@app.command("display")
def flow_display(
    flow_id: str = typer.Argument("", show_default=False),
    flow_definition: str = typer.Option(
        "",
        help=(
            "JSON or YAML representation of the Flow to display. May be provided as a filename "
            "or a raw string representing a JSON object or YAML definition."
        ),
        callback=input_validator,
        show_default=False,
    ),
    output_format: FlowDisplayFormat = typer.Option(
        FlowDisplayFormat.json,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = _flows_env_var_option,
    verbose: bool = verbosity_option,
):
    """
    Visualize a local or deployed Flow defintion. If providing a Flows's ID, You
    must have either created the Flow or be present in the Flow's "visible_to"
    list to view it.
    """
    if not flow_definition and not flow_id:
        raise typer.BadParameter("Either FLOW_ID or --flow_definition should be set.")
    if flow_definition and flow_id:
        raise typer.BadParameter(
            "Only one of FLOW_ID or --flow_definition should be set."
        )

    if flow_id:
        fc = create_flows_client(CLIENT_ID, flows_endpoint)
        try:
            flow_get = fc.get_flow(flow_id)
        except GlobusAPIError as err:
            format_and_echo(err, verbose=verbose)
            typer.Exit(1)
        flow_definition = flow_get.data["definition"]
    else:
        flow_definition = json.loads(flow_definition)

    _format_and_display_flow(flow_definition, output_format, verbose=verbose)


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
    flows_endpoint: str = _flows_env_var_option,
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
    manage_by: List[str] = typer.Option(
        None,
        help="A principal which may change the execution of the Flow instace. The "
        "principal value is the user's or group's UUID prefixed with either "
        "'urn:globus:groups:id:' or 'urn:globus:auth:identity:' [repeatable]",
        callback=principal_validator,
    ),
    monitor_by: List[str] = typer.Option(
        None,
        help="A principal which may monitory the execution of the Flow instace. The "
        "principal value is the user's or group's UUID prefixed with either "
        "'urn:globus:groups:id:' or 'urn:globus:auth:identity:' [repeatable]",
        callback=principal_validator,
    ),
    flows_endpoint: str = _flows_env_var_option,
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
    ),
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Continuously poll this Action until it reaches a completed state.",
        show_default=True,
    ),
):
    """
    Run an instance of a Flow. The argument provides the initial state of the Flow.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flow_input_dict = _process_flow_input(flow_input, input_format)
    method = functools.partial(
        fc.run_flow,
        flow_id,
        flow_scope,
        flow_input_dict,
        monitor_by=monitor_by,
        manage_by=manage_by,
        label=label,
    )

    with live_content:
        # Set watch to false here to immediately return after running the Action
        response = request_runner(method, output_format, verbose, False)

        if watch and isinstance(response, GlobusHTTPResponse):
            action_id = response.data.get("action_id")
            method = functools.partial(
                fc.flow_action_status, flow_id, flow_scope, action_id
            )
            request_runner(method, output_format, verbose, watch)


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
    filters: Optional[List[str]] = typer.Option(
        None,
        "--filter",
        help="A filtering criteria in the form 'key=value' to apply to the "
        "resulting Action listing. The key indicates the filter, the value "
        "indicates the pattern to match. Multiple patterns for a single key may "
        "be specified as a comma seperated string, the results for which will "
        "represent a logical OR. If multiple filters are applied, the returned "
        "data will be the result of a logical AND between them. [repeatable]",
    ),
    orderings: Optional[List[str]] = typer.Option(
        None,
        "--orderby",
        help="An ordering criteria in the form 'key=value' to apply to the resulting "
        "Flow listing. The key indicates the field to order on, and the value is "
        "either ASC, for ascending order, or DESC, for descending order. The first "
        "ordering criteria will be used to sort the data, subsequent ordering criteria "
        "will further sort ties. [repeatable]",
    ),
    flows_endpoint: str = _flows_env_var_option,
    verbose: bool = verbosity_option,
):
    """
    List a Flow definition's discrete invocations.
    """
    parsed_filters = parse_query_options(filters)
    parsed_orderings = parse_query_options(orderings)
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
            filters=parsed_filters,
            orderings=parsed_orderings,
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
    flows_endpoint: str = _flows_env_var_option,
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Continuously poll this Action until it reaches a completed state.",
        show_default=True,
    ),
    verbose: bool = verbosity_option,
):
    """
    Display the status for a Flow definition's particular invocation.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    method = functools.partial(fc.flow_action_status, flow_id, flow_scope, action_id)

    with live_content:
        request_runner(method, OutputFormat.json, verbose, watch)


@app.command("action-resume")
def flow_action_resume(
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
    query_for_inactive_reason: bool = typer.Option(
        True,
        help=(
            "Should the Action first be queried to determine the reason for the "
            "resume, and prompt for additional consent if needed."
        ),
    ),
    flows_endpoint: str = _flows_env_var_option,
    verbose: bool = verbosity_option,
):
    """Resume a Flow in the INACTIVE state. If query-for-inactive-reason is set, and the
    Flow Action is in an INACTIVE state due to requiring additional Consent, the required
    Consent will be determined and you may be prompted to allow Consent using the Globus
    Auth web interface.

    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    try:
        if query_for_inactive_reason:
            result = fc.flow_action_status(flow_id, flow_scope, action_id)
            body = result.data
            status = body.get("status")
            details = body.get("details", {})
            code = details.get("code")
            if status == "INACTIVE" and code == "ConsentRequired":
                flow_scope = details.get("required_scope")
        result = fc.flow_action_resume(flow_id, flow_scope, action_id)
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
    flows_endpoint: str = _flows_env_var_option,
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
    flows_endpoint: str = _flows_env_var_option,
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
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Continuously poll this Action until it reaches a completed state. "
        "Using this option will report only the latest state available."
        "Only JSON and YAML output formats are supported.",
        show_default=True,
    ),
    flows_endpoint: str = _flows_env_var_option,
    verbose: bool = verbosity_option,
):
    """
    Get a log of the steps executed by a Flow definition's invocation.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    method = functools.partial(
        fc.flow_action_log,
        flow_id,
        flow_scope,
        action_id,
        limit,
        reverse,
        marker,
        per_page,
    )

    if watch and output_format in {FlowDisplayFormat.json, FlowDisplayFormat.yaml}:
        with live_content:
            flow_log_runner(method, output_format, verbose, watch)
        raise typer.Exit()

    try:
        resp = method()
    except GlobusAPIError as err:
        resp = err

    if output_format in {FlowDisplayFormat.json, FlowDisplayFormat.yaml}:
        format_and_echo(resp, output_format.get_dumper(), verbose=verbose)
    else:
        if isinstance(resp, GlobusHTTPResponse):
            flow_def = fc.get_flow(flow_id)
            dumper = output_format.get_dumper()
            dumper(resp, flow_def)
        else:
            format_and_echo(resp, verbose=verbose)


def _format_and_display_flow(
    flow_resp: Union[GlobusHTTPResponse, dict],
    output_format: FlowDisplayFormat,
    verbose=False,
):
    """
    Diplays a flow as either JSON, graphviz, or an image
    """
    if output_format in (FlowDisplayFormat.json, FlowDisplayFormat.yaml):
        format_and_echo(flow_resp, output_format.get_dumper())
    elif output_format in (FlowDisplayFormat.graphviz, FlowDisplayFormat.image):
        if isinstance(flow_resp, GlobusHTTPResponse):
            flow_resp = flow_resp.data["definition"]

        graphviz_out = graphviz_format(flow_resp)
        if output_format == FlowDisplayFormat.graphviz:
            typer.echo(graphviz_out.source)
        else:
            graphviz_out.render("flows-output/graph", view=True, cleanup=True)


if __name__ == "__main__":
    app()
