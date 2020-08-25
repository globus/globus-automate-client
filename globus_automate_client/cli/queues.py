from enum import Enum
from typing import List

import typer

from globus_automate_client.cli.callbacks import (
    principal_validator_callback,
    text_validator_callback,
)
from globus_automate_client.cli.helpers import format_and_echo, verbosity_option
from globus_automate_client.queues_client import create_queues_client
from globus_automate_client.token_management import CLIENT_ID


class QueueRole(str, Enum):
    admin = "admin"
    send = "sender"
    receive = "receiver"


app = typer.Typer(short_help="Manage Globus Automate Queues")


@app.command("list")
def queue_list(
    roles: List[QueueRole] = typer.Option(
        [QueueRole.admin],
        "--role",
        "-r",
        help="Display Queues where you have the selected role. [repeatable]",
        case_sensitive=False,
        show_default=True,
    ),
    verbose: bool = verbosity_option,
):
    """
    List Queues for which you have access.
    """
    qc = create_queues_client(CLIENT_ID)
    queues = qc.list_queues(roles=[r.value for r in roles])
    format_and_echo(queues, verbose=verbose)


@app.command("create")
def queue_create(
    label: str = typer.Option(..., help="A convenient name to identify the new Queue."),
    admins: List[str] = typer.Option(
        ...,
        "--admin",
        help="The Principal URNs allowed to administer the Queue. [repeatable]",
        callback=principal_validator_callback,
    ),
    senders: List[str] = typer.Option(
        ...,
        "--sender",
        help="The Principal URNs allowed to send to the Queue. [repeatable]",
        callback=principal_validator_callback,
    ),
    receivers: List[str] = typer.Option(
        ...,
        "--receiver",
        help="The Principal URNs allowed to receive from the Queue. [repeatable]",
        callback=principal_validator_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Create a new Queue.
    """
    qc = create_queues_client(CLIENT_ID)
    queues = qc.create_queue(label, admins, senders, receivers)
    format_and_echo(queues, verbose=verbose)


@app.command("update")
def queue_update(
    queue_id: str = typer.Argument(...),
    label: str = typer.Option(..., help="A convenient name to identify the new Queue."),
    admins: List[str] = typer.Option(
        ...,
        "--admin",
        help="The Principal URNs allowed to administer the Queue. [repeatable]",
        callback=principal_validator_callback,
    ),
    senders: List[str] = typer.Option(
        ...,
        "--sender",
        help="The Principal URNs allowed to send to the Queue. [repeatable]",
        callback=principal_validator_callback,
    ),
    receivers: List[str] = typer.Option(
        ...,
        "--receiver",
        help="The Principal URNs allowed to receive from the Queue. [repeatable]",
        callback=principal_validator_callback,
    ),
    delivery_timeout: int = typer.Option(
        ...,
        help=(
            "The minimum amount of time (in seconds) that the Queue Service should "
            "attempt to retry delivery of messages to the receiver_url if delivery "
            "is not initially successful"
        ),
        min=60,
        max=1209600,
    ),
    verbose: bool = verbosity_option,
):
    """
    Update a Queue's properties. Requires the admin role on the Queue.
    """
    qc = create_queues_client(CLIENT_ID)
    queues = qc.update_queue(
        queue_id, label, admins, senders, receivers, delivery_timeout
    )
    format_and_echo(queues, verbose=verbose)


@app.command("display")
def queue_display(
    queue_id: str = typer.Argument(...), verbose: bool = verbosity_option,
):
    """
    Display the description of a Queue based on its id.
    """
    qc = create_queues_client(CLIENT_ID)
    queue = qc.get_queue(queue_id)
    format_and_echo(queue, verbose=verbose)


@app.command("delete")
def queue_delete(
    queue_id: str = typer.Argument(...), verbose: bool = verbosity_option,
):
    """
    Delete a Queue based on its id. You must have either
    created the Queue or have a role defined on the Queue.
    """
    qc = create_queues_client(CLIENT_ID)
    queue = qc.delete_queue(queue_id)
    format_and_echo(queue, verbose=verbose)


@app.command("receive")
def queue_receive(
    queue_id: str = typer.Argument(...),
    max_messages: int = typer.Option(
        None, help="The maximum number of messages to retrieve from the Queue", min=0
    ),
    verbose: bool = verbosity_option,
):
    """
    Receive a message from a Queue. You must have the
    "receiver" role on the Queue to perform this action.
    """
    qc = create_queues_client(CLIENT_ID)
    queue = qc.receive_messages(queue_id, max_messages=max_messages)
    format_and_echo(queue, verbose=verbose)


@app.command("send")
def queue_send(
    queue_id: str = typer.Argument(...),
    message: str = typer.Option(
        ...,
        "--message",
        "-m",
        help="Text of the message to send. Files may be referenced by prefixing the '@' character to the value.",
        prompt=True,
        callback=text_validator_callback,
    ),
    verbose: bool = verbosity_option,
):
    """
    Send a message to a Queue. You must have the "sender" role
    on the Queue to perform this action.
    """
    qc = create_queues_client(CLIENT_ID)
    message_send = qc.send_message(queue_id, message)
    format_and_echo(message_send, verbose=verbose)
