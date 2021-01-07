import json
from enum import Enum
from typing import Any, List, Mapping

import typer
import yaml

from globus_automate_client.cli.callbacks import (
    input_validator_callback,
    principal_validator,
    url_validator_callback,
)
from globus_automate_client.cli.helpers import format_and_echo, verbosity_option
from globus_automate_client.client_helpers import create_action_client

app = typer.Typer(short_help="Manage Globus Automate Actions")


class ActionInputFormat(str, Enum):
    json = "json"
    yaml = "yaml"


class ActionOutputFormat(str, Enum):
    json = "json"
    yaml = "yaml"


# Constant to reduce if statements making the selection
# used in calls to format_and_echo
DUMPERS = {
    ActionOutputFormat.json: json.dumps,
    ActionOutputFormat.yaml: yaml.dump,
}


def _process_action_body(
    body: str, input_format: ActionInputFormat
) -> Mapping[str, Any]:
    """
    Turn input strings into dicts per input format type (ActionInputFormat)
    """
    action_dict = None
    if input_format is ActionInputFormat.json:
        try:
            action_dict = json.loads(body)
        except json.JSONDecodeError as e:
            raise typer.BadParameter(f"Invalid JSON: {e}")
    elif input_format is ActionInputFormat.yaml:
        try:
            action_dict = yaml.safe_load(body)
        except Exception as e:
            raise typer.BadParameter(f"Invalid YAML: {e}")

    return action_dict


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
    output_format: ActionOutputFormat = typer.Option(
        ActionOutputFormat.json,
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
    if ac is not None:
        result = ac.introspect()
        format_and_echo(result, DUMPERS[output_format], verbose=verbose)
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
        callback=input_validator_callback,
    ),
    request_id: str = typer.Option(
        None,
        help=("An identifier to associate with this Action invocation request"),
    ),
    manage_by: List[str] = typer.Option(
        None,
        help="A principal which may change the execution of the Action. [repeatable]",
        callback=principal_validator,
    ),
    monitor_by: List[str] = typer.Option(
        None,
        help="A principal which may view the state of the Action. [repeatable]",
        callback=principal_validator,
    ),
    verbose: bool = verbosity_option,
    output_format: ActionOutputFormat = typer.Option(
        ActionOutputFormat.json,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
    input_format: ActionInputFormat = typer.Option(
        ActionInputFormat.json,
        "--input",
        "-i",
        help="Input format.",
        case_sensitive=False,
        show_default=True,
    ),
):
    """
    Launch an Action.
    """
    ac = create_action_client(action_url, action_scope)
    if ac:
        parsed_body = _process_action_body(body, input_format)
        result = ac.run(parsed_body, request_id, manage_by, monitor_by)
        format_and_echo(result, DUMPERS[output_format], verbose=verbose)
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
    output_format: ActionOutputFormat = typer.Option(
        ActionOutputFormat.json,
        "--format",
        "-f",
        help="Output display format.",
        case_sensitive=False,
        show_default=True,
    ),
):
    """
    Query an Action's status by its ACTION_ID.
    """
    ac = create_action_client(action_url, action_scope)
    if ac:
        result = ac.status(action_id)
        format_and_echo(result, DUMPERS[output_format], verbose=verbose)
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
    output_format: ActionOutputFormat = typer.Option(
        ActionOutputFormat.json,
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
    if ac:
        result = ac.cancel(action_id)
        format_and_echo(result, DUMPERS[output_format], verbose=verbose)
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
    output_format: ActionOutputFormat = typer.Option(
        ActionOutputFormat.json,
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
    if ac:
        result = ac.release(action_id)
        format_and_echo(result, DUMPERS[output_format], verbose=verbose)
    return None


if __name__ == "__main__":
    app()
