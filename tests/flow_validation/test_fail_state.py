import typing as t

import pytest

from globus_automate_client.models import FlowDefinition, FlowValidationError

simple_fail_state = {
    "StartAt": "InstantFail",
    "States": {
        "InstantFail": {
            "Type": "Fail",
            "Comment": "No info",
        },
    },
}

detailed_fail_state = {
    "StartAt": "InstantFail",
    "States": {
        "InstantFail": {
            "Type": "Fail",
            "Comment": "No info",
            "Cause": "SomeCause",
            "Error": "SomeError",
        },
    },
}

extra_fields_fail_state = {
    "StartAt": "InstantFail",
    "States": {
        "InstantFail": {
            "Type": "Fail",
            "Comment": "No info",
            "Cause": "SomeCause",
            "Error": "SomeError",
            "SomeExtraField": "SomeValue",
        },
    },
}

next_state_not_allowed = {
    "StartAt": "InstantFail",
    "States": {
        "InstantFail": {
            "Type": "Fail",
            "Comment": "No info",
            "Next": "SomeState",
        },
        "SomeState": {"Type": "Pass", "End": True},
    },
}


valid_flow_definitions = [simple_fail_state, detailed_fail_state]
invalid_flow_definitions = [extra_fields_fail_state, next_state_not_allowed]


@pytest.mark.parametrize("flow_def", valid_flow_definitions)
def test_valid_flows_pass_validation(flow_def: t.Dict[str, t.Any]):
    FlowDefinition(**flow_def)


@pytest.mark.parametrize("flow_def", invalid_flow_definitions)
def test_invalid_flows_fail_validation(flow_def: t.Dict[str, t.Any]):
    with pytest.raises(FlowValidationError) as ve:
        FlowDefinition(**flow_def)

    assert ve.type is FlowValidationError
