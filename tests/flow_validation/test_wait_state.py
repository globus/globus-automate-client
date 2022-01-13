import typing as t

import pytest

from globus_automate_client.models import FlowValidationError, WaitState

valid_wait_state = {
    "Type": "Wait",
    "Comment": "Simply Waiting",
    "Seconds": 1,
    "End": True,
}

multiple_wait_time_fields_set = {
    "Type": "Wait",
    "Comment": "Simply Waiting",
    "Seconds": 1,
    "SecondsPath": "$.some_path",
    "End": True,
}

no_wait_time_fields_set = {
    "Type": "Wait",
    "Comment": "Simply Waiting",
    "End": True,
}

unexpected_fields_set = {
    "Type": "Wait",
    "Comment": "Simply Waiting",
    "Seconds": 1,
    "ThisFieldIsUnexpected": True,
    "End": True,
}

input_path_is_not_json_path = {
    "Type": "Wait",
    "Comment": "Simply Waiting",
    "Seconds": 2,
    "InputPath": "not_json_path",
    "End": True,
}

output_path_is_not_json_path = {
    "Type": "Wait",
    "Comment": "Simply Waiting",
    "Seconds": 1,
    "OutputPath": "not_json_path",
    "End": True,
}

seconds_path_is_not_json_path = {
    "Type": "Wait",
    "Comment": "Simply Waiting",
    "SecondsPath": "not_json_path",
    "End": True,
}

timestamp_path_is_not_json_path = {
    "Type": "Wait",
    "Comment": "Simply Waiting",
    "TimestampPath": "not_json_path",
    "End": True,
}


valid_state_definitions = [valid_wait_state]
invalid_state_definitions = [
    multiple_wait_time_fields_set,
    no_wait_time_fields_set,
    unexpected_fields_set,
    input_path_is_not_json_path,
    output_path_is_not_json_path,
    seconds_path_is_not_json_path,
    timestamp_path_is_not_json_path,
]


@pytest.mark.parametrize("state_def", valid_state_definitions)
def test_valid_wait_states_pass_validation(state_def: t.Dict[str, t.Any]):
    state_model = WaitState(**state_def)
    state_def_out = state_model.dict(exclude_unset=True)
    assert state_def_out == state_def


@pytest.mark.parametrize("state_def", invalid_state_definitions)
def test_invalid_wait_states_fail_validation(state_def: t.Dict[str, t.Any]):
    with pytest.raises(FlowValidationError) as ve:
        WaitState(**state_def)

    assert ve.type is FlowValidationError
