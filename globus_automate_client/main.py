from argparse import ArgumentParser
import sys
import uuid
import json
from os import path
from typing import Any, List, Optional, Tuple, Dict
from globus_sdk import AccessTokenAuthorizer, NativeAppAuthClient
from globus_sdk.exc import GlobusAPIError

from .action_client import ActionClient, create_action_client
from .flows_client import create_flows_client
from .token_management import get_access_token_for_scope
from .helpers import subcommand, argument, clear_internal_args, json_parse_args

CLIENT_ID = "e6c75d97-532a-4c88-b031-8584a319fa3e"

cli = ArgumentParser(add_help=False)
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


def get_action_client_for_args(args) -> Optional[ActionClient]:
    action_url = args.action_url
    action_scope = args.action_scope
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


@subcommand(action_scoped_args, parent=subparsers)
def action_provider_introspect(args):
    ac = create_action_client(args.action_url, "NoTokenNeeded")
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
    ],
    parent=subparsers,
)
def flow_deploy(args):
    fc = create_flows_client(CLIENT_ID)
    flow_defn = read_arg_content_from_file(vars(args)["definition"][0])
    flow_dict = json.loads(flow_defn)
    return fc.deploy_flow(flow_dict, args.visible_to, args.runnable_by)


@subcommand([], parent=subparsers)
def flows_list(args):
    fc = create_flows_client(CLIENT_ID)
    flows = fc.list_flows()
    return flows


@subcommand(
    [argument("flow-id", help="Id of flow to display", nargs=1)], parent=subparsers
)
def flow_display(args):
    fc = create_flows_client(CLIENT_ID)
    flow_id = vars(args)["flow-id"][0]
    return fc.get_flow(flow_id)


@subcommand(
    flow_scoped_args
    + [argument("flow-input", help="JSON format input to the flow", nargs=1)],
    parent=subparsers,
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
        argument("action-id", help="flow execution id to return status for", nargs=1),
    ],
    parent=subparsers,
)
def flow_action_log(args):
    fc = create_flows_client(CLIENT_ID)
    flow_id = args.flow_id
    flow_scope = args.flow_scope
    reverse_order = args.reverse_order
    limit = args.limit
    action_id = vars(args)["action-id"][0]
    return fc.flow_action_log(flow_id, flow_scope, action_id, limit, reverse_order)


def main():
    args = cli.parse_args()
    try:
        ret = args.func(args)
        if ret is not None:
            ret_string = json.dumps(ret.data, indent=2)
            print(ret_string)
    except GlobusAPIError as gae:
        print(f"Request failed due to {str(gae)}")
    except AttributeError:
        # Would occur if no func is provided on the invocation
        cli.print_help(sys.stderr)


if __name__ == "__main__":
    main()
