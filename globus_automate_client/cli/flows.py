import functools
import uuid
from typing import List, Optional

import typer

from globus_automate_client.cli.auth import CLIENT_ID
from globus_automate_client.cli.callbacks import (
    flow_input_validator,
    input_validator,
    principal_or_all_authenticated_users_validator,
    principal_or_public_validator,
    principal_validator,
    url_validator_callback,
)
from globus_automate_client.cli.constants import (
    ActionRole,
    ActionRoleAllNames,
    ActionStatus,
    FlowRole,
    FlowRoleAllNames,
    ImageOutputFormat,
    ListingOutputFormat,
    OutputFormat,
    RunLogOutputFormat,
)
from globus_automate_client.cli.helpers import (
    flows_env_var_option,
    make_role_param,
    output_format_option,
    parse_query_options,
    process_input,
    verbosity_option,
)
from globus_automate_client.cli.rich_helpers import (
    FlowListDisplayFields,
    LogCompletionDetector,
    RequestRunner,
    RunEnumerateDisplayFields,
    RunListDisplayFields,
    RunLogDisplayFields,
)
from globus_automate_client.cli.rich_rendering import live_content
from globus_automate_client.client_helpers import create_flows_client
from globus_automate_client.flows_client import (
    RUN_STATUS_SCOPE,
    FlowValidationError,
    validate_flow_definition,
)

app = typer.Typer(short_help="Manage Globus Automate Flows")


_principal_description = (
    "The principal value is the user's Globus Auth username or their identity "
    "UUID in the form urn:globus:auth:identity:<UUID>. A Globus Group may also be "
    "used using the form urn:globus:groups:id:<GROUP_UUID>."
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
    flow_viewer: List[str] = typer.Option(
        None,
        help=(
            "A principal which may view this Flow. "
            + _principal_description
            + " The special value of 'public' may be used to "
            "indicate that any user can view this Flow. [repeatable]"
        ),
        callback=principal_or_public_validator,
        hidden=False,
    ),
    # viewer and visible_to are aliases for the full flow_viewer
    viewer: List[str] = typer.Option(
        None,
        callback=principal_or_public_validator,
        hidden=True,
    ),
    visible_to: List[str] = typer.Option(
        None,
        callback=principal_or_public_validator,
        hidden=True,
    ),
    flow_starter: List[str] = typer.Option(
        None,
        help=(
            "A principal which may run an instance of the deployed Flow. "
            + _principal_description
            + "The special value of "
            "'all_authenticated_users' may be used to indicate that any authenticated user "
            "can invoke this flow. [repeatable]"
        ),
        callback=principal_or_all_authenticated_users_validator,
    ),
    # starter and runnable_by are aliases for the full flow_starter
    starter: List[str] = typer.Option(
        None, callback=principal_or_all_authenticated_users_validator, hidden=True
    ),
    runnable_by: List[str] = typer.Option(
        None, callback=principal_or_all_authenticated_users_validator, hidden=True
    ),
    flow_administrator: List[str] = typer.Option(
        None,
        help=(
            "A principal which may update the deployed Flow. "
            + _principal_description
            + "[repeatable]"
        ),
        callback=principal_validator,
    ),
    # administrator and administered_by are aliases for the full flow_administrator
    administrator: List[str] = typer.Option(
        None, callback=principal_validator, hidden=True
    ),
    administered_by: List[str] = typer.Option(
        None, callback=principal_validator, hidden=True
    ),
    subscription_id: Optional[str] = typer.Option(
        None,
        help="The Id of the Globus Subscription which will be used to make this flow managed.",
    ),
    validate: bool = typer.Option(
        True,
        help="(EXPERIMENTAL) Perform rudimentary validation of the flow definition.",
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = flows_env_var_option,
    verbose: bool = verbosity_option,
    output_format: OutputFormat = output_format_option,
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help=(
            "Do a dry run of deploying the flow to test your definition without"
            " actually making changes."
        ),
    ),
):
    """
    Deploy a new Flow.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flow_dict = process_input(definition)
    input_schema_dict = process_input(input_schema)

    method = functools.partial(
        fc.deploy_flow,
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
        dry_run=dry_run,
    )
    RequestRunner(method, format=output_format, verbose=verbose).run_and_render()


@app.command("get")
def flow_get(
    flow_id: uuid.UUID = typer.Argument(..., help="A deployed Flow's ID"),
    output_format: OutputFormat = output_format_option,
    verbose: bool = verbosity_option,
    flows_endpoint: str = flows_env_var_option,
):
    """
    Get a Flow's definition as it exists on the Flows service.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    method = functools.partial(fc.get_flow, str(flow_id))
    RequestRunner(method, format=output_format, verbose=verbose).run_and_render()


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
    flow_viewer: List[str] = typer.Option(
        None,
        help="A principal which may view this Flow. "
        + _principal_description
        + "The special value of 'public' may be used to "
        "indicate that any user can view this Flow. [repeatable]",
        callback=principal_or_public_validator,
    ),
    viewer: List[str] = typer.Option(
        None, callback=principal_or_public_validator, hidden=True
    ),
    visible_to: List[str] = typer.Option(
        None, callback=principal_or_public_validator, hidden=True
    ),
    flow_starter: List[str] = typer.Option(
        None,
        help="A principal which may run an instance of the deployed Flow. "
        + _principal_description
        + " The special value of "
        "'all_authenticated_users' may be used to indicate that any "
        "authenticated user can invoke this flow. [repeatable]",
        callback=principal_or_all_authenticated_users_validator,
    ),
    starter: List[str] = typer.Option(
        None, callback=principal_or_all_authenticated_users_validator, hidden=True
    ),
    runnable_by: List[str] = typer.Option(
        None, callback=principal_or_all_authenticated_users_validator, hidden=True
    ),
    flow_administrator: List[str] = typer.Option(
        None,
        help="A principal which may update the deployed Flow. "
        + _principal_description
        + "[repeatable]",
        callback=principal_validator,
    ),
    administrator: List[str] = typer.Option(
        None, callback=principal_validator, hidden=True
    ),
    administered_by: List[str] = typer.Option(
        None, callback=principal_validator, hidden=True
    ),
    assume_ownership: bool = typer.Option(
        False,
        "--assume-ownership",
        help="Assume the ownership of the Flow. This can only be performed by user's "
        "in the flow_administrators role.",
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
    flows_endpoint: str = flows_env_var_option,
    verbose: bool = verbosity_option,
    output_format: OutputFormat = output_format_option,
):
    """
    Update a Flow.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flow_dict = process_input(definition)
    input_schema_dict = process_input(input_schema)

    method = functools.partial(
        fc.update_flow,
        flow_id,
        flow_dict,
        title,
        subtitle,
        description,
        keywords,
        flow_viewer,
        flow_starter,
        flow_administrator,
        subscription_id,
        input_schema_dict,
        validate_definition=validate,
        visible_to=visible_to,
        runnable_by=runnable_by,
        administered_by=administered_by,
    )
    RequestRunner(method, format=output_format, verbose=verbose).run_and_render()


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
):
    """
    Parse and validate a Flow definition by providing visual output.
    """
    flow_dict = process_input(definition)

    try:
        validate_flow_definition(flow_dict)
    except FlowValidationError as fve:
        typer.secho(str(fve), fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho("No issues found in the Flow definition.", fg=typer.colors.GREEN)


@app.command("list")
def flow_list(
    roles: List[FlowRoleAllNames] = typer.Option(
        [FlowRole.flow_owner],
        "--role",
        "-r",
        help=(
            "Display Flows where you have at least the selected role. "
            "Precedence of roles is: flow_viewer, flow_starter, flow_administrator, "
            "flow_owner. Thus, by specifying, for example, flow_starter, all flows "
            "for which you hvae flow_starter, flow_administrator, or flow_owner roles "
            "will be displayed. Values visible_to, runnable_by, administered_by and "
            "created_by are deprecated. [repeatable use deprecated as the lowest "
            "precedence value provided will determine the flows displayed.]"
        ),
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
    flows_endpoint: str = flows_env_var_option,
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
    output_format: ListingOutputFormat = typer.Option(
        ListingOutputFormat.table,
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
        help="Continuously poll for new Flows.",
        show_default=True,
    ),
):
    """
    List Flows for which you have access.
    """
    parsed_filters = parse_query_options(filters)
    parsed_orderings = parse_query_options(orderings)
    role_param = make_role_param(roles)

    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    method = functools.partial(
        fc.list_flows,
        marker=marker,
        per_page=per_page,
        filters=parsed_filters,
        orderings=parsed_orderings,
        **role_param,
    )
    with live_content:
        RequestRunner(
            method,
            format=output_format,
            verbose=verbose,
            watch=watch,
            fields=FlowListDisplayFields,
        ).run_and_render()


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
    output_format: ImageOutputFormat = typer.Option(
        ImageOutputFormat.json,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = flows_env_var_option,
):
    """
    Visualize a local or deployed Flow defintion. If providing a Flows's ID, You
    must have either created the Flow or be present in the Flow's "flow_viewers"
    list to view it.
    """
    if not flow_definition and not flow_id:
        raise typer.BadParameter("Either FLOW_ID or --flow_definition should be set.")
    if flow_definition and flow_id:
        raise typer.BadParameter(
            "Only one of FLOW_ID or --flow_definition should be set."
        )

    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    rr = RequestRunner(
        functools.partial(fc.get_flow, flow_id),
        format=output_format,
        verbose=False,
        watch=False,
    )

    if flow_id:
        result = rr.run()
        if result.is_api_error:
            rr.format = (
                output_format
                if output_format in {ImageOutputFormat.json, ImageOutputFormat.yaml}
                else ImageOutputFormat.json
            )
            rr.render(result)
            raise typer.Exit(1)
        else:
            flow_dict = result.data["definition"]
    else:
        flow_dict = process_input(flow_definition)

    if output_format in {ImageOutputFormat.json, ImageOutputFormat.yaml}:
        rr.render_as_result(flow_dict, client=fc, status_code=result.result.http_status)
    else:
        output_format.visualize(flow_dict)


@app.command("delete")
def flow_delete(
    flow_id: str = typer.Argument(...),
    output_format: OutputFormat = output_format_option,
    flows_endpoint: str = flows_env_var_option,
    verbose: bool = verbosity_option,
):
    """
    Delete a Flow. You must be in the Flow's "flow_administrators" list.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    method = functools.partial(fc.delete_flow, flow_id)
    RequestRunner(
        method,
        format=output_format,
        verbose=verbose,
    ).run_and_render()


@app.command("run")
def flow_run(
    flow_id: str = typer.Argument(...),
    flow_input: str = typer.Option(
        ...,
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
    run_manager: List[str] = typer.Option(
        None,
        help="A principal which may change the execution of the Flow instance. "
        + _principal_description
        + " [repeatable]",
        callback=principal_validator,
    ),
    manage_by: List[str] = typer.Option(
        None, callback=principal_validator, hidden=True
    ),
    run_monitor: List[str] = typer.Option(
        None,
        help="A principal which may monitor the execution of the Flow instance. "
        + _principal_description
        + " [repeatable]",
        callback=principal_validator,
    ),
    monitor_by: List[str] = typer.Option(
        None, callback=principal_validator, hidden=True
    ),
    flows_endpoint: str = flows_env_var_option,
    verbose: bool = verbosity_option,
    output_format: ListingOutputFormat = typer.Option(
        None,
        "--format",
        "-f",
        help=(
            "Output display format."
            " If --watch is enabled then the default is 'table',"
            " otherwise 'json' is the default."
        ),
        case_sensitive=False,
        show_default=False,
    ),
    label: str = typer.Option(
        ...,
        "--label",
        "-l",
        help="Label to mark this run.",
    ),
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help=(
            "Continuously poll this Action until it reaches a completed state."
            " If enabled the default output format is 'table'."
        ),
        show_default=True,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help=(
            "Do a dry run with your input to this flow to test the input without"
            " actually running anything."
        ),
    ),
):
    """
    Run an instance of a Flow. The argument provides the initial state of the Flow.
    You must be in the Flow's "flow_starters" list.
    """

    if not output_format:
        # Default to JSON if the user did not specify an output format.
        # However, if watch is enabled, default to tabular output.
        output_format = ListingOutputFormat.json
        if watch:
            output_format = ListingOutputFormat.table

    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    flow_input_dict = process_input(flow_input)
    method = functools.partial(
        fc.run_flow,
        flow_id,
        flow_scope,
        flow_input_dict,
        run_monitors=run_monitor,
        run_managers=run_manager,
        label=label,
        dry_run=dry_run,
        monitor_by=monitor_by,
        manage_by=manage_by,
    )
    with live_content:
        result = RequestRunner(
            method,
            format=output_format,
            verbose=verbose,
            watch=watch,
            fields=RunLogDisplayFields,
            run_once=True,
        ).run_and_render()

        if not result.is_api_error and watch:
            action_id = result.data.get("action_id")
            return flow_action_log(
                action_id=action_id,
                flow_id=flow_id,
                flow_scope=flow_scope,
                reverse=False,
                limit=100,
                marker=None,
                per_page=50,
                output_format=output_format,
                watch=watch,
                flows_endpoint=flows_endpoint,
                verbose=verbose,
            )


@app.command("action-list")
@app.command("run-list")
def flow_actions_list(
    flow_id: Optional[str] = typer.Option(
        None,
        help="The ID for the Flow which triggered the Action. If not present runs "
        "from all Flows will be displayed.",
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    roles: List[ActionRoleAllNames] = typer.Option(
        None,
        "--role",
        help=(
            "Display Actions/Runs where you have at least the selected role. "
            "Precedence of roles is: run_monitor, run_manager, "
            "run_owner. Thus, by specifying, for example, run_manager, all runs "
            "for which you hvae run_manager or run_owner roles "
            "will be displayed. [repeatable use deprecated as the lowest precedence "
            "value provided will determine the flows displayed.]"
        ),
    ),
    statuses: List[ActionStatus] = typer.Option(
        [],
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
    flows_endpoint: str = flows_env_var_option,
    verbose: bool = verbosity_option,
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Continuously poll for new Actions.",
        show_default=True,
    ),
    output_format: ListingOutputFormat = typer.Option(
        ListingOutputFormat.table,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
):
    """
    List a Flow definition's discrete invocations.
    """
    parsed_filters = parse_query_options(filters)
    parsed_orderings = parse_query_options(orderings)
    statuses_str = [s.value for s in statuses]
    role_param = make_role_param(roles)

    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    callable = functools.partial(
        fc.list_flow_actions,
        flow_id=flow_id,
        flow_scope=flow_scope,
        statuses=statuses_str,
        marker=marker,
        per_page=per_page,
        filters=parsed_filters,
        orderings=parsed_orderings,
        **role_param,
    )
    with live_content:
        RequestRunner(
            callable,
            format=output_format,
            verbose=verbose,
            watch=watch,
            fields=RunListDisplayFields,
        ).run_and_render()


@app.command("action-status")
@app.command("run-status")
def flow_action_status(
    action_id: str = typer.Argument(...),
    flow_id: str = typer.Option(
        None,
        help="The ID for the Flow which triggered the Action.",
    ),
    flow_scope: str = typer.Option(
        None,
        help="The scope this Flow uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    flows_endpoint: str = flows_env_var_option,
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Continuously poll this Action until it reaches a completed state.",
        show_default=True,
    ),
    output_format: OutputFormat = output_format_option,
    verbose: bool = verbosity_option,
):
    """
    Display the status for a Flow definition's particular invocation.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    method = functools.partial(fc.flow_action_status, flow_id, flow_scope, action_id)
    with live_content:
        RequestRunner(
            method, format=output_format, verbose=verbose, watch=watch
        ).run_and_render()


@app.command("action-resume")
@app.command("run-resume")
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
    flows_endpoint: str = flows_env_var_option,
    output_format: OutputFormat = output_format_option,
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Continuously poll this Action until it reaches a completed state.",
        show_default=True,
    ),
    verbose: bool = verbosity_option,
):
    """Resume a Flow in the INACTIVE state. If query-for-inactive-reason is set, and the
    Flow Action is in an INACTIVE state due to requiring additional Consent, the required
    Consent will be determined and you may be prompted to allow Consent using the Globus
    Auth web interface.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    if query_for_inactive_reason:
        result = RequestRunner(
            functools.partial(fc.flow_action_status, flow_id, flow_scope, action_id),
            format=output_format,
            verbose=verbose,
            watch=watch,
            run_once=True,
        ).run_and_render()
        if not result.is_api_error:
            body = result.data
            status = body.get("status")
            details = body.get("details", {})
            code = details.get("code")
            if status == "INACTIVE" and code == "ConsentRequired":
                flow_scope = details.get("required_scope")

    with live_content:
        result = RequestRunner(
            functools.partial(fc.flow_action_resume, flow_id, flow_scope, action_id),
            format=output_format,
            verbose=verbose,
            watch=watch,
            run_once=True,
        ).run_and_render()
        if not result.is_api_error and watch:
            RequestRunner(
                functools.partial(
                    fc.flow_action_status, flow_id, flow_scope, action_id
                ),
                format=output_format,
                verbose=verbose,
                watch=watch,
            ).run_and_render()


@app.command("action-release")
@app.command("run-release")
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
    output_format: OutputFormat = output_format_option,
    flows_endpoint: str = flows_env_var_option,
    verbose: bool = verbosity_option,
):
    """
    Remove execution history for a particular Flow definition's invocation.
    After this, no further information about the run can be accessed.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    method = functools.partial(fc.flow_action_release, flow_id, flow_scope, action_id)
    RequestRunner(
        method, format=output_format, verbose=verbose, watch=False
    ).run_and_render()


@app.command("action-cancel")
@app.command("run-cancel")
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
    output_format: OutputFormat = output_format_option,
    flows_endpoint: str = flows_env_var_option,
    verbose: bool = verbosity_option,
):
    """
    Cancel an active execution for a particular Flow definition's invocation.
    """
    fc = create_flows_client(CLIENT_ID, flows_endpoint)
    method = functools.partial(fc.flow_action_cancel, flow_id, flow_scope, action_id)
    RequestRunner(
        method, format=output_format, verbose=verbose, watch=False
    ).run_and_render()


@app.command("action-log")
@app.command("run-log")
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
        False,
        "--reverse",
        help="Display logs starting from most recent and proceeding in reverse chronological order",
        show_default=True,
    ),
    limit: int = typer.Option(
        None,
        help="Set a maximum number of events from the log to return",
        min=1,
        max=100,
    ),
    marker: Optional[str] = typer.Option(
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
    output_format: RunLogOutputFormat = typer.Option(
        RunLogOutputFormat.table,
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
        help=(
            "Continuously poll this Action until it reaches a completed state."
            " Using this option will report only the latest state available."
        ),
        show_default=True,
    ),
    flows_endpoint: str = flows_env_var_option,
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
    rr = RequestRunner(
        method,
        format=output_format,
        verbose=verbose,
        watch=watch,
        fields=RunLogDisplayFields,
        detector=LogCompletionDetector,
    )
    with live_content:
        if output_format in {
            RunLogOutputFormat.json,
            RunLogOutputFormat.yaml,
            RunLogOutputFormat.table,
        }:
            rr.run_and_render()
        else:
            result = rr.run()
            if not result.is_api_error:
                flow_def = fc.get_flow(flow_id)
                output_format.visualize(result.result, flow_def)
            else:
                rr.format = RunLogOutputFormat.json
                rr.render(result)


@app.command("action-enumerate")
@app.command("run-enumerate")
def flow_action_enumerate(
    roles: List[ActionRoleAllNames] = typer.Option(
        [ActionRole.run_owner],
        "--role",
        help="Display Actions/Runs where you have at least the selected role. "
        "Precedence of roles is: run_monitor, run_manager, run_owner. "
        "Thus, by specifying, for example, run_manager, all flows "
        "for which you hvae run_manager or run_owner roles "
        "will be displayed. Values monitored_by, managed_by and created_by "
        "are deprecated. [repeatable use deprecated as the lowest "
        "precedence value provided will determine the Actions/Runs displayed.]",
    ),
    statuses: List[ActionStatus] = typer.Option(
        [],
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
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Continuously poll for new Actions.",
        show_default=True,
    ),
    output_format: ListingOutputFormat = typer.Option(
        ListingOutputFormat.table,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
    flows_endpoint: str = flows_env_var_option,
    verbose: bool = verbosity_option,
):
    """
    Retrieve all Flow Runs you have access to view.
    """
    parsed_filters = parse_query_options(filters)
    parsed_orderings = parse_query_options(orderings)
    statuses_str = [s.value for s in statuses]
    role_param = make_role_param(roles)
    fc = create_flows_client(CLIENT_ID, flows_endpoint, RUN_STATUS_SCOPE)
    method = functools.partial(
        fc.enumerate_actions,
        statuses=statuses_str,
        marker=marker,
        per_page=per_page,
        filters=parsed_filters,
        orderings=parsed_orderings,
        **role_param,
    )
    with live_content:
        RequestRunner(
            method,
            format=output_format,
            verbose=verbose,
            watch=watch,
            fields=RunEnumerateDisplayFields,
        ).run_and_render()


@app.command("action-update")
@app.command("run-update")
def flow_action_update(
    action_id: str = typer.Argument(...),
    run_manager: Optional[List[str]] = typer.Option(
        None,
        help="A principal which may change the execution of the Run."
        + _principal_description
        + " [repeatable]",
        callback=principal_validator,
    ),
    run_monitor: Optional[List[str]] = typer.Option(
        None,
        help="A principal which may monitor the execution of the Run."
        + _principal_description
        + " [repeatable]",
        callback=principal_validator,
    ),
    flows_endpoint: str = flows_env_var_option,
    verbose: bool = verbosity_option,
    output_format: OutputFormat = output_format_option,
):
    """
    Update a Run on the Flows service
    """
    run_manager = run_manager if run_manager else None
    run_monitor = run_monitor if run_monitor else None
    fc = create_flows_client(CLIENT_ID, flows_endpoint, RUN_STATUS_SCOPE)
    RequestRunner(
        functools.partial(
            fc.flow_action_update,
            action_id,
            run_managers=run_manager,
            run_monitors=run_monitor,
        ),
        format=output_format,
        verbose=verbose,
    ).run_and_render()


if __name__ == "__main__":
    app()
