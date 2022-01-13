import typing as t

import pytest

from globus_automate_client.models import FlowValidationError, PassState

valid_pass_state_usage = {
    "Type": "Pass",
    "End": True,
}

input_path_is_not_json_path = {
    "Type": "Pass",
    "InputPath": "not_a_json_path",
    "End": True,
}

result_is_not_json_path = {
    "Type": "Pass",
    "Result": "not_a_json_path",
    "End": True,
}

result_path_is_not_json_path = {
    "Type": "Pass",
    "ResultPath": "not_a_json_path",
    "End": True,
}

parameter_key_is_json_path_values_are_not_json_path = {
    "Type": "Pass",
    "Parameters": {"json_path_key.$": "not_a_json_path"},
    "End": True,
}

nested_parameter_key_is_json_path_values_are_not_json_path = {
    "Type": "Pass",
    "Parameters": {"nested_json": {"json_path_key.$": "not_a_json_path"}},
    "End": True,
}

additional_fields_set_on_state = {
    "Type": "Pass",
    "Parameters": {},
    "NonExistantStateField": True,
    "End": True,
}

valid_state_definitions = [valid_pass_state_usage]
invalid_state_definitions = [
    input_path_is_not_json_path,
    result_is_not_json_path,
    result_path_is_not_json_path,
    parameter_key_is_json_path_values_are_not_json_path,
    nested_parameter_key_is_json_path_values_are_not_json_path,
    additional_fields_set_on_state,
]


@pytest.mark.parametrize("state_def", valid_state_definitions)
def test_valid_pass_states_pass_validation(state_def: t.Dict[str, t.Any]):
    state_model = PassState(**state_def)
    state_def_out = state_model.dict(exclude_unset=True)
    assert state_def_out == state_def


@pytest.mark.parametrize("state_def", invalid_state_definitions)
def test_invalid_pass_states_fail_validation(state_def: t.Dict[str, t.Any]):
    with pytest.raises(FlowValidationError) as ve:
        PassState(**state_def)

    assert ve.type is FlowValidationError
