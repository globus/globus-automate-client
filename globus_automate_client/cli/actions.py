import functools
from typing import List

import typer
from globus_sdk import GlobusAPIError

from globus_automate_client.cli.callbacks import (
    input_validator,
    principal_validator,
    url_validator_callback,
)
from globus_automate_client.cli.constants import InputFormat, OutputFormat
from globus_automate_client.cli.helpers import (
    format_and_echo,
    process_input,
    request_runner,
    verbosity_option,
)
from globus_automate_client.cli.rich_rendering import live_content
from globus_automate_client.client_helpers import create_action_client

app = typer.Typer(short_help="Manage Globus Automate Actions")


@app.command("introspect")
def action_introspect(
    action_url: str = typer.Option(
        ...,
        help="The url at which the target Action Provider is located.",
        prompt=True,
        callback=url_validator_callback,
    ),
    action_scope: str = typer.Option(
        None,
        help="The scope this Action Provider uses to authenticate requests.",
        callback=url_validator_callback,
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
    Introspect an Action Provider's schema.
    """
    ac = create_action_client(action_url, action_scope)
    try:
        result = ac.introspect()
    except GlobusAPIError as err:
        result = err
    format_and_echo(result, output_format.get_dumper(), verbose=verbose)


@app.command("run")
def action_run(
    action_url: str = typer.Option(
        ...,
        help="The url at which the target Action Provider is located.",
        prompt=True,
        callback=url_validator_callback,
    ),
    action_scope: str = typer.Option(
        None,
        help="The scope this Action Provider uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    body: str = typer.Option(
        ...,
        "--body",
        "-b",
        help=(
            "The body to supply to the Action Provider. Can be a filename or raw "
            "JSON string."
        ),
        prompt=True,
        callback=input_validator,
    ),
    request_id: str = typer.Option(
        None,
        help=("An identifier to associate with this Action invocation request"),
    ),
    manage_by: List[str] = typer.Option(
        None,
        help="A principal which may change the execution of the Action. The principal "
        "is the user's or group's UUID prefixed with either 'urn:globus:groups:id:' "
        "or 'urn:globus:auth:identity:' [repeatable]",
        callback=principal_validator,
    ),
    monitor_by: List[str] = typer.Option(
        None,
        help="A principal which may view the state of the Action. The principal "
        "is the user's or group's UUID prefixed with either 'urn:globus:groups:id:' "
        "or 'urn:globus:auth:identity:' [repeatable]",
        callback=principal_validator,
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
        help="Optional label to mark this execution of the action.",
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
    Launch an Action.
    """
    parsed_body = process_input(body, input_format)
    ac = create_action_client(action_url, action_scope)
    method = functools.partial(
        ac.run, parsed_body, request_id, manage_by, monitor_by, label=label
    )

    with live_content:
        # Set watch to false here to immediately return after running the Action
        result = request_runner(method, output_format, verbose, False)

        if watch and not isinstance(result, GlobusAPIError):
            action_id = result.data.get("action_id")
            method = functools.partial(ac.status, action_id)
            request_runner(method, output_format, verbose, watch)


@app.command("status")
def action_status(
    action_url: str = typer.Option(
        ...,
        help="The url at which the target Action Provider is located.",
        prompt=True,
        callback=url_validator_callback,
    ),
    action_scope: str = typer.Option(
        None,
        help="The scope this Action Provider uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    action_id: str = typer.Argument(...),
    verbose: bool = verbosity_option,
    output_format: OutputFormat = typer.Option(
        OutputFormat.json,
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
        help="Continuously poll this Action until it reaches a completed state. ",
        show_default=True,
    ),
):
    """
    Query an Action's status by its ACTION_ID.
    """
    ac = create_action_client(action_url, action_scope)
    method = functools.partial(ac.status, action_id)
    with live_content:
        request_runner(method, output_format, verbose, watch)


@app.command("resume")
def action_resume(
    action_url: str = typer.Option(
        ...,
        help="The url at which the target Action Provider is located.",
        prompt=True,
        callback=url_validator_callback,
    ),
    action_scope: str = typer.Option(
        None,
        help="The scope this Action Provider uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    query_for_inactive_reason: bool = typer.Option(
        True,
        help=(
            "Should the Action first be queried to determine the reason for the "
            "resume, and prompt for additional consent if needed."
        ),
    ),
    action_id: str = typer.Argument(...),
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
    Resume an inactive Action by its ACTION_ID.
    """
    ac = create_action_client(action_url, action_scope=action_scope)
    try:
        if query_for_inactive_reason:
            result = ac.status(action_id)
            body = result.data
            status = body.get("status")
            details = body.get("details", {})
            code = details.get("code")
            if status == "INACTIVE" and code == "ConsentRequired":
                required_scope = details.get("required_scope")
                if required_scope is not None:
                    ac = create_action_client(action_url, action_scope=required_scope)
        result = ac.resume(action_id)
    except GlobusAPIError as err:
        result = err
    format_and_echo(result, output_format.get_dumper(), verbose=verbose)


@app.command("cancel")
def action_cancel(
    action_url: str = typer.Option(
        ...,
        help="The url at which the target Action Provider is located.",
        prompt=True,
        callback=url_validator_callback,
    ),
    action_scope: str = typer.Option(
        None,
        help="The scope this Action Provider uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    action_id: str = typer.Argument(...),
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
    Terminate a running Action by its ACTION_ID.
    """
    ac = create_action_client(action_url, action_scope)
    try:
        result = ac.cancel(action_id)
    except GlobusAPIError as err:
        result = err
    format_and_echo(result, output_format.get_dumper(), verbose=verbose)


@app.command("release")
def action_release(
    action_url: str = typer.Option(
        ...,
        help="The url at which the target Action Provider is located.",
        prompt=True,
        callback=url_validator_callback,
    ),
    action_scope: str = typer.Option(
        None,
        help="The scope this Action Provider uses to authenticate requests.",
        callback=url_validator_callback,
    ),
    action_id: str = typer.Argument(...),
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
    Remove an Action's execution history by its ACTION_ID.
    """
    ac = create_action_client(action_url, action_scope)
    try:
        result = ac.release(action_id)
    except GlobusAPIError as err:
        result = err
    format_and_echo(result, output_format.get_dumper(), verbose=verbose)


if __name__ == "__main__":
    app()
