import json
import sys
import tempfile
import uuid
from argparse import ArgumentParser
from typing import Optional

from globus_sdk import AccessTokenAuthorizer, GlobusHTTPResponse
from globus_sdk.exc import GlobusAPIError
from graphviz import Digraph

from .action_client import ActionClient, create_action_client
from .flows_client import create_flows_client
from .queues_client import create_queues_client
from .graphviz_rendering import graphviz_format, state_colors_for_log
from .helpers import argument, clear_internal_args, json_parse_args, subcommand
from .token_management import get_access_token_for_scope

CLIENT_ID = "e6c75d97-532a-4c88-b031-8584a319fa3e"

cli = ArgumentParser(add_help=True)
subparsers = cli.add_subparsers(dest="subcommand")
action_scoped_args = [
    argument("--action-scope", help="The Globus Auth scope associated with the Action"),
    argument(
        "--action-url", help="The base URL used for accessing the Action", required=True
    ),
]

flow_scoped_args = [
    argument("--flow-id", help="Id of flow to execute", required=True),
    argument("--flow-scope", help="Scope of the flow to execute"),
]

output_format_argument = argument(
    "--format",
    help="Format to display output",
    choices=["json", "graphviz", "image"],
    default="json",
)


def get_action_client_for_args(args) -> Optional[ActionClient]:
    action_url = args.action_url
    action_scope = args.action_scope
    if action_url is None or action_scope is None:
        return None
    access_token = get_access_token_for_scope(action_scope, CLIENT_ID)
    if access_token is not None:
        ac = create_action_client(action_url, access_token)
        return ac
    return None


def read_arg_content_from_file(arg_val: str) -> str:
    if arg_val.startswith("@"):
        arg_file_name = arg_val[1:]
        with open(arg_file_name, "r") as arg_file:
            arg_val = arg_file.read()
    return arg_val


@subcommand(
    action_scoped_args,
    parent=subparsers,
    help=(
        "Display the descriptive information for the Action Provider including its required request input schema."
    ),
)
def action_provider_introspect(args):
    ac = get_action_client_for_args(args)
    if ac is None:
        # We don't have a token, but try anyway in case this action provider
        # is publicly visible without authentication.
        ac = create_action_client(args.action_url, "NoTokenAvailable")
    return ac.introspect()


@subcommand(
    action_scoped_args
    + [
        argument(
            "--body",
            required=True,
            help="JSON Format for the body of the Action to run",
        )
    ],
    parent=subparsers,
    help=("Run an action rooted at the Action URL using the Action scope."),
)
def action_run(args):
    ac = get_action_client_for_args(args)
    if ac is not None:
        body = read_arg_content_from_file(args.body)
        body = json.loads(body)
        req_id = str(uuid.uuid4())
        run_ret = ac.run(body, req_id)
        return run_ret
    return None


@subcommand(
    action_scoped_args
    + [argument("action-id", help="action_id value to return status for", nargs=1)],
    parent=subparsers,
    help=(
        "Get the status of an action which has already been run and has not yet been released."
    ),
)
def action_status(args):
    ac = get_action_client_for_args(args)
    if ac is not None:
        action_id = vars(args)["action-id"][0]
        return ac.status(action_id)
    return None


@subcommand(
    action_scoped_args
    + [argument("action-id", help="action_id value to cancel", nargs=1)],
    parent=subparsers,
    help=(
        "Cancel an action which has already been run. If the action has completed, this has no effect."
    ),
)
def action_cancel(args):
    ac = get_action_client_for_args(args)
    if ac is not None:
        action_id = vars(args)["action-id"][0]
        return ac.cancel(action_id)
    return None


@subcommand(
    action_scoped_args
    + [argument("action-id", help="action_id value to release status for", nargs=1)],
    parent=subparsers,
    help=(
        "Inform the Action Provider that it need not retain state for the provided action id. Subsequent calls with the same action id will fail as if the action id never existed."
    ),
)
def action_release(args):
    ac = get_action_client_for_args(args)
    if ac is not None:
        action_id = vars(args)["action-id"][0]
        return ac.release(action_id)
    return None


@subcommand(
    [
        argument(
            "--visible-to",
            help=(
                "The set of principals (identities or groups) which may see the "
                "existence of the Flow once it is deployed"
            ),
            nargs="*",
        ),
        argument(
            "--runnable-by",
            help=(
                "The set of principals (identities or groups) which may see the "
                "run the deployed Flow."
            ),
            nargs="*",
        ),
        argument(
            "--definition",
            help="JSON representation of the flow to deploy. May be provided as the "
            "value or by reference to a file name with an '@' prefix.",
            nargs=1,
        ),
        argument("--title", help="The title of the Flow", required=True),
        argument(
            "--subtitle",
            help="A subtitle for the flow providing additional, brief description",
            nargs="?",
        ),
        argument(
            "--description",
            help="A long form description of the flow's purpose or usage",
            nargs="?",
        ),
        argument(
            "--keywords",
            help=(
                "A list of keywords which may categorize or help discovery of the flow"
            ),
            nargs="*",
        ),
        argument(
            "--administered_by",
            help=(
                "The set of principals (identities or groups) which may update "
                "the deployed Flow."
            ),
            nargs="*",
        ),
    ],
    parent=subparsers,
    help=(
        "Deploy a new flow to the Flows service. The returned Id field may be used for further operations on the flow."
    ),
)
def flow_deploy(args):
    fc = create_flows_client(CLIENT_ID)
    flow_defn = read_arg_content_from_file(vars(args)["definition"][0])
    flow_dict = json.loads(flow_defn)
    return fc.deploy_flow(
        flow_dict,
        args.title,
        args.subtitle,
        args.description,
        args.keywords,
        args.visible_to,
        args.runnable_by,
        args.administered_by,
    )


@subcommand(
    [
        output_format_argument,
        argument(
            "flow-definition",
            help="JSON Representation of the Flow Definition to be evaluated",
            nargs=1,
        ),
    ],
    parent=subparsers,
    help=(
        "Locally parse the Flow definition and do rudimentry checking on its validity. "
        "Provide output in graphviz or image format to help with visualizing the Flow."
    ),
)
def flow_lint(args):
    flow_defn = read_arg_content_from_file(vars(args)["flow-definition"][0])
    flow_dict = json.loads(flow_defn)
    graph = graphviz_format(flow_dict)
    if args.format == "json":
        return json.dumps(flow_dict, indent=2)
    elif args.format == "graphviz":
        return graph.source
    else:
        return graph


@subcommand(
    [
        argument(
            "--roles",
            type=str,
            nargs="+",
            metavar="ROLE",
            help=(
                "Your Flow role values to display in the list. Possible values are: "
                "created_by, visible_to, runnable_by, administered_by"
            ),
        )
    ],
    parent=subparsers,
    help=("List Flows you have deployed or for which you have access."),
)
def flows_list(args):
    fc = create_flows_client(CLIENT_ID)
    flows = fc.list_flows(roles=args.roles)
    return flows


@subcommand(
    [
        argument(
            "--statuses",
            type=str,
            nargs="+",
            metavar="STATUS",
            help=(
                "The Action Status values to display. Possible values are "
                "SUCCEEDED, FAILED, ACTIVE, INACTIVE"
            ),
        ),
        argument(
            "--roles",
            type=str,
            nargs="+",
            metavar="ROLE",
            help=(
                "Your role values to display in the list. Possible values are: "
                "created_by, monitor_by, manage_by"
            ),
        ),
        argument("--flow-scope", help="Scope of the flow to list actions"),
        argument("flow-id", help="Id of flow to display", nargs=1),
    ],
    parent=subparsers,
    help=("List flows you have deployed or for which you have access."),
)
def flow_actions_list(args):
    fc = create_flows_client(CLIENT_ID)
    flow_id = vars(args)["flow-id"][0]
    flow_scope = args.flow_scope
    action_list = fc.list_flow_actions(
        flow_id, flow_scope, statuses=args.statuses, roles=args.roles
    )
    return action_list


@subcommand(
    [
        output_format_argument,
        argument("flow-id", help="Id of flow to display", nargs=1),
    ],
    parent=subparsers,
    help=(
        "Display the description of a Flow based on its id. You must have either created the Flow or be present in the visible_to list of the Flow to view it."
    ),
)
def flow_display(args):
    fc = create_flows_client(CLIENT_ID)
    flow_id = vars(args)["flow-id"][0]
    flow_get = fc.get_flow(flow_id)
    if args.format == "json":
        return flow_get
    elif args.format in ("graphviz", "image"):
        graphviz_out = graphviz_format(flow_get.data["definition"])
        if args.format == "graphviz":
            return graphviz_out.source
        else:
            return graphviz_out


@subcommand(
    [
        output_format_argument,
        argument("--flow-scope", help="Scope of the flow to execute"),
        argument("flow-id", help="Id of flow to display", nargs=1),
    ],
    parent=subparsers,
    help=(
        "Delete a Flow. You must either have created the Flow or be in the Flow's administrated_by list."
    ),
)
def flow_delete(args):
    fc = create_flows_client(CLIENT_ID)
    flow_id = vars(args)["flow-id"][0]
    flow_scope = args.flow_scope
    flow_del = fc.delete_flow(flow_id, flow_scope)
    if args.format == "json":
        if not flow_del.data:
            # empty response---don't print, otherwise it shows `null`
            return None
        return flow_del
    elif args.format in ("graphviz", "image"):
        graphviz_out = graphviz_format(flow_del.data["definition"])
        if args.format == "graphviz":
            return graphviz_out.source
        else:
            return graphviz_out


@subcommand(
    flow_scoped_args
    + [argument("flow-input", help="JSON format input to the Flow", nargs=1)],
    parent=subparsers,
    help=(
        "Run an instance of a Flow. The argument provides the initial state of the Flow."
    ),
)
def flow_run(args):
    fc = create_flows_client(CLIENT_ID)
    flow_input = read_arg_content_from_file(vars(args)["flow-input"][0])
    flow_input_dict = json.loads(flow_input)
    flow_id = args.flow_id
    flow_scope = args.flow_scope
    return fc.run_flow(flow_id, flow_scope, flow_input_dict)


@subcommand(
    flow_scoped_args
    + [argument("action-id", help="flow execution id to return status for", nargs=1)],
    parent=subparsers,
    help=(
        "Retrieve the status of a running Flow Action. The most recent state executed in the Flow will be displayed."
    ),
)
def flow_action_status(args):
    fc = create_flows_client(CLIENT_ID)
    flow_id = args.flow_id
    flow_scope = args.flow_scope
    action_id = vars(args)["action-id"][0]
    return fc.flow_action_status(flow_id, flow_scope, action_id)


@subcommand(
    flow_scoped_args
    + [
        argument(
            "--reverse-order",
            help="If present return log entries starting from most recent and proceeding in reverse time sequence",
            dest="reverse_order",
            action="store_true",
        ),
        argument(
            "--no-reverse-order",
            help="If present return log entries starting from the first entry and proceeding forward in time. This is the default behavior if neither --no-reverse-order nor --reverse-order are present.",
            dest="reverse_order",
            action="store_false",
        ),
        argument(
            "--limit",
            help="Set a maximum number of events from the log to return",
            type=int,
            default=10,
        ),
        output_format_argument,
        argument("action-id", help="flow execution id to return status for", nargs=1),
    ],
    parent=subparsers,
    help=("Get a log of the most recent steps executed by a Flow action."),
)
def flow_action_log(args):
    fc = create_flows_client(CLIENT_ID)
    flow_id = args.flow_id
    flow_scope = args.flow_scope
    reverse_order = args.reverse_order
    limit = args.limit
    action_id = vars(args)["action-id"][0]
    resp = fc.flow_action_log(flow_id, flow_scope, action_id, limit, reverse_order)
    if args.format == "json":
        return resp
    elif args.format in ("graphviz", "image"):
        flow_def_resp = fc.get_flow(flow_id)
        flow_def = flow_def_resp.data["definition"]
        colors = state_colors_for_log(resp.data["entries"])
        graphviz_out = graphviz_format(flow_def, colors)
        if args.format == "graphviz":
            return graphviz_out.source
        else:
            return graphviz_out


@subcommand(
    [
        argument(
            "--roles",
            type=str,
            nargs="+",
            metavar="ROLE",
            help=(
                "Your queues role values to display in the list. Possible values are: "
                "admin, send, receive"
            ),
        )
    ],
    parent=subparsers,
    help=("List queues you have created or for which you have access."),
)
def queues_list(args):
    qc = create_queues_client(CLIENT_ID)
    queues = qc.list_queues(roles=args.roles)
    return queues


@subcommand(
    [
        argument(
            "--label",
            type=str,
            required=True,
            help="A convenient name to identify the new Queue.",
        ),
        argument(
            "--admins",
            type=str,
            nargs="+",
            metavar="ADMIN_URN",
            help=("The Principal URNs allowed to administer the Queue."),
        ),
        argument(
            "--senders",
            type=str,
            nargs="+",
            metavar="SENDER_URN",
            help=("The Principal URNs allowed to send to the Queue."),
        ),
        argument(
            "--receivers",
            type=str,
            nargs="+",
            metavar="RECEIVER_URN",
            help=("The Principal URNs allowed to receive from the Queue."),
        ),
    ],
    parent=subparsers,
    help=("Create a new Queue"),
)
def queue_create(args):
    qc = create_queues_client(CLIENT_ID)
    label = args.label
    admins = args.admins
    senders = args.senders
    receivers = args.receivers

    queues = qc.create_queue(label, admins, senders, receivers)
    return queues


@subcommand(
    [
        argument(
            "--label",
            type=str,
            required=False,
            help="A convenient name to identify the new Queue.",
        ),
        argument(
            "--admins",
            type=str,
            nargs="*",
            metavar="ADMIN_URN",
            help=("The Principal URNs allowed to administer the Queue."),
        ),
        argument(
            "--senders",
            type=str,
            nargs="*",
            metavar="SENDER_URN",
            help=("The Principal URNs allowed to send to the Queue."),
        ),
        argument(
            "--receivers",
            type=str,
            nargs="*",
            metavar="RECEIVER_URN",
            help=("The Principal URNs allowed to receive from the Queue."),
        ),
        argument("--queue-id", help="Id of Queue to update", nargs=1),
    ],
    parent=subparsers,
    help=("Update properties of a Queue. Requires having the admin role."),
)
def queue_update(args):
    qc = create_queues_client(CLIENT_ID)
    label = args.label
    admins = args.admins
    senders = args.senders
    receivers = args.receivers
    queue_id = args.queue_id[0]

    queues = qc.update_queue(queue_id, label, admins, senders, receivers)
    return queues


@subcommand(
    [argument("queue-id", help="Id of Queue to display", nargs=1)],
    parent=subparsers,
    help=(
        "Display the description of a Queue based on its id. You must have either created the Queue or have a role defined on the Queue."
    ),
)
def queue_display(args):
    qc = create_queues_client(CLIENT_ID)
    queue_id = vars(args)["queue-id"][0]
    queue = qc.get_queue(queue_id)
    return queue


@subcommand(
    [argument("queue-id", help="Id of Queue to delete", nargs=1)],
    parent=subparsers,
    help=(
        "Delete a Queue based on its id. You must have either created the Queue or have a role defined on the Queue."
    ),
)
def queue_delete(args):
    qc = create_queues_client(CLIENT_ID)
    queue_id = vars(args)["queue-id"][0]
    queue = qc.delete_queue(queue_id)
    return queue


@subcommand(
    [
        argument(
            "--max-messages",
            help="The maximum number of messages to retrieve from the Queue",
            type=int,
            default=1,
        ),
        argument("queue-id", help="Id of queue to read from", nargs=1),
    ],
    parent=subparsers,
    help=(
        "Receive a message from a Queue. You must have the receive role of the Queue to be permitted to perform this action."
    ),
)
def queue_receive(args):
    qc = create_queues_client(CLIENT_ID)
    max_messages = args.max_messages
    queue_id = vars(args)["queue-id"][0]
    queue = qc.receieve_messages(queue_id, max_messages=max_messages)
    return queue


@subcommand(
    [
        argument("--queue-id", help="Id of the Queue to send to", required=True),
        argument(
            "message",
            help="Text of the message to send. Files may be referenced by prefixing the '@' character to the value.",
            nargs=1,
        ),
    ],
    parent=subparsers,
    help=(
        "Send a message to a Queue. You must have the send role of the Queue to be permitted to perform this action."
    ),
)
def queue_send(args):
    qc = create_queues_client(CLIENT_ID)
    queue_id = args.queue_id
    message = read_arg_content_from_file(vars(args)["message"][0])
    message_send = qc.send_message(queue_id, message)
    return message_send


def main():
    args = cli.parse_args()
    if args.subcommand is None:
        cli.print_help(sys.stderr)
        return
    try:
        ret = args.func(args)
        if isinstance(ret, GlobusHTTPResponse):
            json_string = json.dumps(ret.data, indent=2)
            print(json_string)
        elif isinstance(ret, str):
            print(ret)
        elif isinstance(ret, Digraph):
            ret.view(tempfile.mktemp(".png"))
    except GlobusAPIError as gae:
        print(f"Request failed due to {str(gae)}")
    except AttributeError as ae:
        print(f"Request failed due to {str(ae)}")


if __name__ == "__main__":
    main()
