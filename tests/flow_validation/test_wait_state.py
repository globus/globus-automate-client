import typing as t

import pytest

from globus_automate_client.models import FlowDefinition, FlowValidationError

valid_wait_state = {
    "StartAt": "SimpleWait",
    "States": {
        "SimpleWait": {
            "Type": "Wait",
            "Comment": "Simply Waiting",
            "Seconds": 1,
            "End": True,
        },
    },
}


multiple_wait_time_fields_set = {
    "StartAt": "SimpleWait",
    "States": {
        "SimpleWait": {
            "Type": "Wait",
            "Comment": "Simply Waiting",
            "Seconds": 1,
            "SecondsPath": "$.some_path",
            "End": True,
        },
    },
}

no_wait_time_fields_set = {
    "StartAt": "SimpleWait",
    "States": {
        "SimpleWait": {
            "Type": "Wait",
            "Comment": "Simply Waiting",
            "End": True,
        },
    },
}

unexpected_fields_set = {
    "StartAt": "SimpleWait",
    "States": {
        "SimpleWait": {
            "Type": "Wait",
            "Comment": "Simply Waiting",
            "Seconds": 1,
            "ThisFieldIsUnexpected": True,
            "End": True,
        },
    },
}


input_path_is_not_json_path = {
    "StartAt": "SimpleWait",
    "States": {
        "SimpleWait": {
            "Type": "Wait",
            "Comment": "Simply Waiting",
            "Seconds": 2,
            "InputPath": "not_json_path",
            "End": True,
        },
    },
}
output_path_is_not_json_path = {
    "StartAt": "SimpleWait",
    "States": {
        "SimpleWait": {
            "Type": "Wait",
            "Comment": "Simply Waiting",
            "Seconds": 1,
            "OutputPath": "not_json_path",
            "End": True,
        },
    },
}
seconds_path_is_not_json_path = {
    "StartAt": "SimpleWait",
    "States": {
        "SimpleWait": {
            "Type": "Wait",
            "Comment": "Simply Waiting",
            "SecondsPath": "not_json_path",
            "End": True,
        },
    },
}
timestamp_path_is_not_json_path = {
    "StartAt": "SimpleWait",
    "States": {
        "SimpleWait": {
            "Type": "Wait",
            "Comment": "Simply Waiting",
            "TimestampPath": "not_json_path",
            "End": True,
        },
    },
}

valid_flow_definitions = [valid_wait_state]
invalid_flow_definitions = [
    multiple_wait_time_fields_set,
    no_wait_time_fields_set,
    unexpected_fields_set,
    input_path_is_not_json_path,
    output_path_is_not_json_path,
    seconds_path_is_not_json_path,
    timestamp_path_is_not_json_path,
]


@pytest.mark.parametrize("flow_def", valid_flow_definitions)
def test_valid_flows_pass_validation(flow_def: t.Dict[str, t.Any]):
    flow_model = FlowDefinition(**flow_def)
    flow_def_out = flow_model.dict(exclude_unset=True)
    assert flow_def_out == flow_def


@pytest.mark.parametrize("flow_def", invalid_flow_definitions)
def test_invalid_flows_fail_validation(flow_def: t.Dict[str, t.Any]):
    with pytest.raises(FlowValidationError) as ve:
        FlowDefinition(**flow_def)

    assert ve.type is FlowValidationError
