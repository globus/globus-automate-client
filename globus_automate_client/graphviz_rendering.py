import json
from typing import Any, Dict, List, Mapping, Optional

from graphviz import Digraph

_SHAPE_TYPES = {
    "Choice": {"shape": "diamond"},
    "Action": {"shape": "box"},
    "Succeed": {"shape": "box", "style": "rounded"},
}

_COLOR_PRECEDENCE = ["", "yellow", "orange", "green", "red"]


def json_to_label_text(json_dict: Mapping[str, Any]) -> str:
    label_text = json.dumps(json_dict, indent=1)
    label_text = label_text.replace("\n", '<br ALIGN="LEFT"/>')
    return label_text


def state_colors_for_log(flow_action_log_entries: List[Mapping]) -> Dict[str, str]:
    color_dict: Dict[str, str] = {}
    for log_entry in flow_action_log_entries:
        state_name = log_entry.get("details", {}).get("state_name")
        if state_name is not None:
            code = log_entry.get("code", "")
            cur_state_color_precedence = _COLOR_PRECEDENCE.index(
                color_dict.get(state_name, "")
            )
            color = ""
            if code.endswith("Completed"):
                color = "green"
            elif code.endswith("Started"):
                color = "yellow"
            elif code == "ActionPolled":
                color = "orange"
            if _COLOR_PRECEDENCE.index(color) > cur_state_color_precedence:
                color_dict[state_name] = color

    return color_dict


def graphviz_format(
    flow: Dict[str, Any], state_colors: Optional[Dict[str, str]] = None
) -> Digraph:
    states = flow.get("States")
    graph = Digraph()

    if state_colors is None:
        state_colors = {}

    if isinstance(states, dict):
        for state_name, state_def in states.items():
            state_type = state_def.get("Type")
            # At least on Choice, Default also exists as a next state name
            next_state = state_def.get("Next", state_def.get("Default"))
            node_params = _SHAPE_TYPES.get(state_type, {"shape": "ellipse"})
            node_params["label"] = state_name
            parameters = state_def.get("Parameters")
            if parameters:
                parameter_text = json_to_label_text(parameters)
                node_params["label"] = node_params["label"] + "<br/>" + parameter_text
            else:
                input_path = state_def.get("InputPath")
                if input_path:
                    node_params["label"] = (
                        node_params["label"] + "<br/>" + f"InputPath: {input_path}"
                    )
            if state_name in state_colors:
                node_params["fillcolor"] = state_colors[state_name]
                node_params["style"] = "filled"
            node_params["label"] = "<" + node_params["label"] + '<br ALIGN="LEFT"/>>'
            graph.node(state_name, **node_params)
            if next_state:
                graph.edge(state_name, next_state)
            choices = state_def.get("Choices", [])
            for choice in choices:
                choice_next = choice.pop("Next")
                choice_text = "<" + json_to_label_text(choice) + '<br ALIGN="LEFT"/>>'
                graph.edge(state_name, choice_next, label=choice_text, style="dotted")

    return graph
