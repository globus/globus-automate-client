import json
import uuid

import typer

from .callbacks import json_validator_callback, url_validator_callback
from .helpers import format_and_echo, get_action_client_for_args, verbosity_option

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
):
    """
    Introspect an Action Provider's schema.
    """
    ac = get_action_client_for_args(action_url, action_scope)
    if ac is not None:
        result = ac.introspect()
        format_and_echo(result, verbose=verbose)
    return None


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
        callback=json_validator_callback,
    ),
    request_id: str = typer.Option(
        None, help=("An identifier to associate with this Action invocation request"),
    ),
    verbose: bool = verbosity_option,
):
    """
    Launch an Action.
    """
    ac = get_action_client_for_args(action_url, action_scope)
    if ac is None:
        typer.echo("Failed to get credentials. Was the scope provided?")
    else:
        body = json.loads(body)
        result = ac.run(body, request_id)
        format_and_echo(result, verbose=verbose)
    return None


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
):
    """
    Query an Action's status by its ACTION_ID.
    """
    ac = get_action_client_for_args(action_url, action_scope)
    if ac is None:
        typer.echo("Failed to get credentials. Was the scope provided?")
    else:
        result = ac.status(action_id)
        format_and_echo(result, verbose=verbose)
    return None


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
):
    """
    Terminate a running Action by its ACTION_ID.
    """
    ac = get_action_client_for_args(action_url, action_scope)
    if ac is None:
        typer.echo("Failed to get credentials. Was the scope provided?")
    else:
        result = ac.cancel(action_id)
        format_and_echo(result, verbose=verbose)
    return None


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
):
    """
    Remove an Action's execution history by its ACTION_ID.
    """
    ac = get_action_client_for_args(action_url, action_scope)
    if ac is None:
        typer.echo("Failed to get credentials. Was the scope provided?")
    else:
        result = ac.release(action_id)
        format_and_echo(result, verbose=verbose)
    return None


if __name__ == "__main__":
    app()
