import typing as t

import pytest

from globus_automate_client.models import FailState, FlowValidationError

simple_fail_state = {
    "Type": "Fail",
    "Comment": "No info",
}

detailed_fail_state = {
    "Type": "Fail",
    "Comment": "No info",
    "Cause": "SomeCause",
    "Error": "SomeError",
}

extra_fields_fail_state = {
    "Type": "Fail",
    "Comment": "No info",
    "Cause": "SomeCause",
    "Error": "SomeError",
    "SomeExtraField": "SomeValue",
}

next_state_not_allowed = {
    "Type": "Fail",
    "Comment": "No info",
    "Next": "SomeState",
}


valid_state_definitions = [simple_fail_state, detailed_fail_state]
invalid_state_definitions = [extra_fields_fail_state, next_state_not_allowed]


@pytest.mark.parametrize("state_def", valid_state_definitions)
def test_valid_fail_states_pass_validation(state_def: t.Dict[str, t.Any]):
    state_model = FailState(**state_def)
    state_def_out = state_model.dict(exclude_unset=True)
    assert state_def_out == state_def


@pytest.mark.parametrize("state_def", invalid_state_definitions)
def test_invalid_fail_states_fail_validation(state_def: t.Dict[str, t.Any]):
    with pytest.raises(FlowValidationError) as ve:
        FailState(**state_def)

    assert ve.type is FlowValidationError
