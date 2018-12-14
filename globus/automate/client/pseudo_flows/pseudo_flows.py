from typing import Any, Dict, List, Optional
import time
from globus.automate.client.token_management import get_access_token_for_scope
from globus.automate.client.action_client import ActionClient, create_action_client
from graphviz import Digraph
import json

_known_scopes: Dict[str, str] = {
    "https://actions.automate.globus.org/Transfer": "https://auth.globus.org/scopes/helloworld.actions.automate.globus.org/globus_transfer_action_all",
    "http://actions.automate.globus.org/HelloWorld": "https://auth.globus.org/scopes/helloworld.actions.automate.globus.org/run_status_release",
    "http://localhost:5000/HelloWorld": "https://auth.globus.org/scopes/helloworld.actions.automate.globus.org/run_status_release",
    "http://localhost:5000/Transfer": "https://auth.globus.org/scopes/helloworld.actions.automate.globus.org/globus_transfer_action_all",
}


def load_from_file(file_name: str) -> Dict[str, Any]:
    with open(file_name, "r") as ff:
        flow_def = json.load(ff)
    return flow_def


def load_from_json(json_str: str) -> Dict[str, Any]:
    return json.loads(json_str)


def flow_to_digraph(
    flow_def: Dict[str, Any],
    skip_types: List[str] = [],
    color_states: Dict[str, str] = {},
) -> Digraph:
    gr = Digraph(comment=flow_def.get("Comment"))
    gr.node("Start")
    gr.node("End")
    first_node = flow_def["StartAt"]
    gr.edge("Start", first_node)
    states = flow_def["States"]
    for state_name, state_def in states.items():
        if state_def.get("Type") in skip_types:
            continue
        node_options = {"shape": "box"}
        if state_name in color_states:
            node_options["color"] = color_states[state_name]
        label = state_def.get("Comment", state_name)
        gr.node(state_name, label, **node_options)
        if "Next" in state_def:
            gr.edge(state_name, state_def["Next"])
        elif "End" in state_def:
            gr.edge(state_name, "End")
        catchers = state_def.get("Catch", [])
        for catcher in catchers:
            gr.edge(
                state_name,
                catcher["Next"],
                label=str(catcher["ErrorEquals"]),
                color="red",
                style="dotted",
            )
    return gr


def scopes_for_flow(flow_def: Dict[str, Any]) -> Dict[str, str]:
    states = flow_def["States"]
    flow_scopes: Dict[str, str] = {}
    for state_name, state_def in states.items():
        state_type = state_def.get("Type")
        if state_type == "Action":
            action_resource = state_def.get("Resource")
            if action_resource not in flow_scopes:
                scope = _known_scopes.get(action_resource)
                if scope is not None:
                    flow_scopes[action_resource] = scope
                else:
                    # TODO: Could do some form of introspect, but not implemented yet
                    pass
    return flow_scopes


def access_tokens_for_flow(flow_def: Dict[str, Any], client_id: str) -> Dict[str, str]:
    scope_map = scopes_for_flow(flow_def)
    tokens: Dict[str, str] = {}
    for action_resource, scope in scope_map.items():
        token = get_access_token_for_scope(scope, client_id)
        tokens[action_resource] = token

    return tokens


def get_path_in_dict(
    path: str, in_dict: Dict[str, Any], create_if_missing: bool = False
) -> Any:
    path_parts = path.split(".")
    for path_elem in path_parts[1:]:
        if path_elem in in_dict:
            in_dict = in_dict[path_elem]
        elif create_if_missing:
            new_tree: Dict[str, Any] = dict()
            in_dict[path_elem] = new_tree
            in_dict = new_tree
        else:
            print(f"Path Element {path_elem} not found in dict {in_dict}")
            return None

    return in_dict


def run_state(
    state: Dict[str, Any], flow_state: Dict[str, Any], tokens: Dict[str, str]
) -> str:
    state_type = state.get("Type")
    if state_type == "Action":
        action_resource = state.get("Resource")
        token = tokens.get(action_resource)
        client = create_action_client(action_resource, token)
        input_path = state.get("InputPath", "$")
        action_input = get_path_in_dict(input_path, flow_state)
        if action_input is None:
            return "FAILED"
        result_path = state.get("ResultPath", "$")
        action_result = get_path_in_dict(
            result_path, flow_state, create_if_missing=True
        )
        print(f"Running Action {action_resource} with input {action_input}")
        run_result = client.run(action_input)
        print(f"Got back Action State {run_result}")
        for key, val in run_result.data.items():
            action_result[key] = val
        action_result["__resource__"] = action_resource
        return action_result["status"]
    elif state_type == "ActionWait":
        result_path = state.get("ResultPath", "$")
        print(f"DEBUG result_path := {result_path}")

        action_result = get_path_in_dict(result_path, flow_state)
        action_id = action_result.get("action_id")
        print(f"Checking status on action {action_id}")
        action_resource = action_result["__resource__"]
        status = action_result.get("status")
        client = None
        sleep_time = 1
        while status not in ("SUCCEEDED", "FAILED"):
            sleep_time = sleep_time * 1.2
            print(f"DEBUG sleep_time := {sleep_time}")
            if sleep_time > 32:
                sleep_time = 32
            if client is None:
                token = tokens.get(action_resource)
                client = create_action_client(action_resource, token)
            status_result = client.status(action_id)
            print(f"Got Back Status: {status_result}")
            action_result.clear()
            for key, val in status_result.data.items():
                action_result[key] = val
            action_result["__resource__"] = action_resource
            status = action_result.get("status")
            if status not in ("SUCCEEDED", "FAILED"):
                time.sleep(sleep_time)
        if client is not None:
            print(f"Releasing action_id {action_id}")
            client.release(action_id)
        return status

    else:
        print(f"Unexpected state type {state_type}")
        return "FATAL"


def run_flow(
    flow_def: Dict[str, Any], input_state: Dict[str, Any], client_id: str
) -> None:
    tokens = access_tokens_for_flow(flow_def, client_id)
    states = flow_def["States"]
    cur_state_name = flow_def.get("StartAt")
    cur_state = states.get(cur_state_name)
    done = False
    while cur_state_name is not None and cur_state is not None:
        display_as = cur_state.get("Comment")
        if display_as is None:
            display_as = cur_state_name
        print(f"Entering state {display_as}")
        state_result = run_state(cur_state, input_state, tokens)
        print(f"State returned status result {state_result}")
        if state_result in ("SUCCEEDED", "ACTIVE", "INACTIVE"):
            if cur_state.get("End", False) is True:
                break
            next_state_name = cur_state.get("Next")
            print(f"Next state will be {next_state_name}")
            cur_state_name = next_state_name
            cur_state = states.get(cur_state_name)
            if cur_state is None:
                print(f"No state for Next {cur_state_name} defined in flow")
                break
            time.sleep(1)
        else:
            print(f"Got error state {state_result}, exiting...")
            break
    return input_state
