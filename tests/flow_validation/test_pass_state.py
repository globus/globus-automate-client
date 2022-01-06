import typing as t

import pytest

from globus_automate_client.models import FlowDefinition, FlowValidationError

valid_pass_state_usage = {
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "End": True,
        },
    },
}

input_path_is_not_json_path = {
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "InputPath": "not_a_json_path",
            "End": True,
        },
    },
}
result_is_not_json_path = {
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "Result": "not_a_json_path",
            "End": True,
        },
    },
}
result_path_is_not_json_path = {
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "ResultPath": "not_a_json_path",
            "End": True,
        },
    },
}

parameter_key_is_json_path_values_are_not_json_path = {
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "Parameters": {"json_path_key.$": "not_a_json_path"},
            "End": True,
        },
    },
}

nested_parameter_key_is_json_path_values_are_not_json_path = {
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "Parameters": {"nested_json": {"json_path_key.$": "not_a_json_path"}},
            "End": True,
        },
    },
}

additional_fields_set_on_state = {
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "Parameters": {},
            "NonExistantStateField": True,
            "End": True,
        },
    },
}

valid_flow_definitions = [valid_pass_state_usage]
invalid_flow_definitions = [
    input_path_is_not_json_path,
    result_is_not_json_path,
    result_path_is_not_json_path,
    parameter_key_is_json_path_values_are_not_json_path,
    nested_parameter_key_is_json_path_values_are_not_json_path,
    additional_fields_set_on_state,
]


@pytest.mark.parametrize("flow_def", valid_flow_definitions)
def test_valid_flows_pass_validation(flow_def: t.Dict[str, t.Any]):
    FlowDefinition(**flow_def)


@pytest.mark.parametrize("flow_def", invalid_flow_definitions)
def test_invalid_flows_fail_validation(flow_def: t.Dict[str, t.Any]):
    with pytest.raises(FlowValidationError) as ve:
        FlowDefinition(**flow_def)

    assert ve.type is FlowValidationError
    # Assert that we're only triggering the Exception under test
    # assert len(ve.value.errors()) == 1
