import functools
from typing import List

import typer

from globus_automate_client.cli.callbacks import (
    input_validator,
    principal_validator,
    url_validator_callback,
)
from globus_automate_client.cli.constants import OutputFormat
from globus_automate_client.cli.helpers import (
    output_format_option,
    process_input,
    verbosity_option,
)
from globus_automate_client.cli.rich_helpers import RequestRunner
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
    output_format: OutputFormat = output_format_option,
):
    """
    Introspect an Action Provider's schema.
    """
    ac = create_action_client(action_url, action_scope)
    RequestRunner(ac.introspect, format=output_format, verbose=verbose).run_and_render()


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
        help="An identifier to associate with this Action invocation request",
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
    output_format: OutputFormat = output_format_option,
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
    parsed_body = process_input(body)
    ac = create_action_client(action_url, action_scope)
    method = functools.partial(
        ac.run, parsed_body, request_id, manage_by, monitor_by, label=label
    )
    result = RequestRunner(
        method,
        format=output_format,
        verbose=verbose,
        watch=watch,
        run_once=True,
    ).run_and_render()
    if not result.is_api_error and watch:
        action_id = result.data.get("action_id")
        method = functools.partial(ac.status, action_id)
        RequestRunner(
            method,
            format=output_format,
            verbose=verbose,
            watch=watch,
            run_once=False,
        ).run_and_render()


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
    output_format: OutputFormat = output_format_option,
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
    RequestRunner(
        method, format=output_format, verbose=verbose, watch=watch, run_once=False
    ).run_and_render()


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
    output_format: OutputFormat = output_format_option,
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Continuously poll this Action until it reaches a completed state. ",
        show_default=True,
    ),
):
    """
    Resume an inactive Action by its ACTION_ID.
    """
    ac = create_action_client(action_url, action_scope=action_scope)
    if query_for_inactive_reason:
        result = RequestRunner(
            functools.partial(ac.status, action_id),
            format=output_format,
            verbose=verbose,
            watch=watch,
            run_once=True,
        ).run()

        if not result.is_api_error:
            body = result.data
            status = body.get("status")
            details = body.get("details", {})
            code = details.get("code")
            if status == "INACTIVE" and code == "ConsentRequired":
                required_scope = details.get("required_scope")
                if required_scope is not None:
                    ac = create_action_client(action_url, action_scope=required_scope)

    result = RequestRunner(
        functools.partial(ac.resume, action_id),
        format=output_format,
        verbose=verbose,
        watch=watch,
        run_once=True,
    ).run_and_render()
    if not result.is_api_error and watch:
        RequestRunner(
            functools.partial(ac.status, action_id),
            format=output_format,
            verbose=verbose,
            watch=watch,
        ).run_and_render()


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
    output_format: OutputFormat = output_format_option,
):
    """
    Terminate a running Action by its ACTION_ID.
    """
    ac = create_action_client(action_url, action_scope)
    method = functools.partial(ac.cancel, action_id)
    RequestRunner(
        method, format=output_format, verbose=verbose, watch=False, run_once=True
    ).run_and_render()


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
    output_format: OutputFormat = output_format_option,
):
    """
    Remove an Action's execution history by its ACTION_ID.
    """
    ac = create_action_client(action_url, action_scope)
    method = functools.partial(ac.release, action_id)
    RequestRunner(
        method, format=output_format, verbose=verbose, watch=False, run_once=True
    ).run_and_render()


if __name__ == "__main__":
    app()
