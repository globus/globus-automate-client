import functools
from enum import Enum
from typing import List

import typer

from globus_automate_client.cli.auth import CLIENT_ID
from globus_automate_client.cli.callbacks import input_validator, principal_validator
from globus_automate_client.cli.constants import OutputFormat
from globus_automate_client.cli.helpers import output_format_option, verbosity_option
from globus_automate_client.cli.rich_helpers import RequestRunner
from globus_automate_client.queues_client import create_queues_client


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
    output_format: OutputFormat = output_format_option,
    verbose: bool = verbosity_option,
):
    """
    List Queues for which you have access.
    """
    qc = create_queues_client(CLIENT_ID)
    method = functools.partial(qc.list_queues, roles=[r.value for r in roles])
    RequestRunner(
        method, format=output_format, verbose=verbose, watch=False
    ).run_and_render()


@app.command("create")
def queue_create(
    label: str = typer.Option(..., help="A convenient name to identify the new Queue."),
    admins: List[str] = typer.Option(
        ...,
        "--admin",
        help="The Principal URNs allowed to administer the Queue. [repeatable]",
        callback=principal_validator,
    ),
    senders: List[str] = typer.Option(
        ...,
        "--sender",
        help="The Principal URNs allowed to send to the Queue. [repeatable]",
        callback=principal_validator,
    ),
    receivers: List[str] = typer.Option(
        ...,
        "--receiver",
        help="The Principal URNs allowed to receive from the Queue. [repeatable]",
        callback=principal_validator,
    ),
    delivery_timeout: int = typer.Option(
        60,  # TODO Update this default timeout once Queue's default is updated
        help=(
            "The minimum amount of time (in seconds) that the Queue Service should "
            "wait for a message-delete request after delivering a message before "
            "making the message visible for receiving by other consumers once "
            "again. If used in conjunction with 'receiver_url' this value "
            "represents the minimum amount of time (in seconds) that the Queue "
            "Service should attempt to retry delivery of messages to the "
            "'receiver_url' if delivery is not initially successful"
        ),
        min=1,
        max=1209600,
        show_default=True,
    ),
    output_format: OutputFormat = output_format_option,
    verbose: bool = verbosity_option,
):
    """
    Create a new Queue.
    """
    qc = create_queues_client(CLIENT_ID)
    method = functools.partial(
        qc.create_queue, label, admins, senders, receivers, delivery_timeout
    )
    RequestRunner(method, format=output_format, verbose=verbose).run_and_render()


@app.command("update")
def queue_update(
    queue_id: str = typer.Argument(...),
    label: str = typer.Option(..., help="A convenient name to identify the new Queue."),
    admins: List[str] = typer.Option(
        ...,
        "--admin",
        help="The Principal URNs allowed to administer the Queue. [repeatable]",
        callback=principal_validator,
    ),
    senders: List[str] = typer.Option(
        ...,
        "--sender",
        help="The Principal URNs allowed to send to the Queue. [repeatable]",
        callback=principal_validator,
    ),
    receivers: List[str] = typer.Option(
        ...,
        "--receiver",
        help="The Principal URNs allowed to receive from the Queue. [repeatable]",
        callback=principal_validator,
    ),
    delivery_timeout: int = typer.Option(
        ...,
        help=(
            "The minimum amount of time (in seconds) that the Queue Service should "
            "wait for a message-delete request after delivering a message before "
            "making the message visible for receiving by other consumers once "
            "again. If used in conjunction with 'receiver_url' this value "
            "represents the minimum amount of time (in seconds) that the Queue "
            "Service should attempt to retry delivery of messages to the "
            "'receiver_url' if delivery is not initially successful"
        ),
        min=1,
        max=1209600,
    ),
    visibility_timeout: int = typer.Option(
        30,
        min=1,
        max=43200,
    ),
    output_format: OutputFormat = output_format_option,
    verbose: bool = verbosity_option,
):
    """
    Update a Queue's properties. Requires the admin role on the Queue.
    """
    qc = create_queues_client(CLIENT_ID)
    method = functools.partial(
        qc.update_queue,
        queue_id,
        label,
        admins,
        senders,
        receivers,
        delivery_timeout,
        visibility_timeout,
    )
    RequestRunner(method, format=output_format, verbose=verbose).run_and_render()


@app.command("display")
def queue_display(
    queue_id: str = typer.Argument(...),
    output_format: OutputFormat = output_format_option,
    verbose: bool = verbosity_option,
):
    """
    Display the description of a Queue based on its id.
    """
    qc = create_queues_client(CLIENT_ID)
    RequestRunner(
        functools.partial(qc.get_queue, queue_id), format=output_format, verbose=verbose
    ).run_and_render()


@app.command("delete")
def queue_delete(
    queue_id: str = typer.Argument(...),
    output_format: OutputFormat = output_format_option,
    verbose: bool = verbosity_option,
):
    """
    Delete a Queue based on its id. You must have either
    created the Queue or have a role defined on the Queue.
    """
    qc = create_queues_client(CLIENT_ID)
    RequestRunner(
        functools.partial(qc.delete_queue, queue_id),
        format=output_format,
        verbose=verbose,
    ).run_and_render()


@app.command("message-receive")
def queue_receive(
    queue_id: str = typer.Argument(...),
    max_messages: int = typer.Option(
        None, help="The maximum number of messages to retrieve from the Queue", min=0
    ),
    output_format: OutputFormat = output_format_option,
    verbose: bool = verbosity_option,
):
    """
    Receive a message from a Queue. You must have the
    "receiver" role on the Queue to perform this action.
    """
    qc = create_queues_client(CLIENT_ID)
    RequestRunner(
        functools.partial(qc.receive_messages, queue_id, max_messages=max_messages),
        format=output_format,
        verbose=verbose,
    ).run_and_render()


@app.command("message-send")
def queue_send(
    queue_id: str = typer.Argument(...),
    message: str = typer.Option(
        ...,
        "--message",
        "-m",
        help="Text of the message to send. Files may also be referenced.",
        prompt=True,
        callback=input_validator,
    ),
    output_format: OutputFormat = output_format_option,
    verbose: bool = verbosity_option,
):
    """
    Send a message to a Queue. You must have the "sender" role
    on the Queue to perform this action.
    """
    qc = create_queues_client(CLIENT_ID)
    RequestRunner(
        functools.partial(qc.send_message, queue_id, message),
        format=output_format,
        verbose=verbose,
    ).run_and_render()


@app.command("message-delete")
def queue_delete_message(
    queue_id: str = typer.Argument(...),
    receipt_handle: List[str] = typer.Option(
        ...,
        help=(
            "A receipt_handle value returned by a previous call to "
            "receive message. [repeatable]"
        ),
    ),
    output_format: OutputFormat = output_format_option,
    verbose: bool = verbosity_option,
):
    """
    Notify a Queue that a message has been processed.
    """
    qc = create_queues_client(CLIENT_ID)
    RequestRunner(
        functools.partial(qc.delete_messages, queue_id, receipt_handle),
        format=output_format,
        verbose=verbose,
    ).run_and_render()
