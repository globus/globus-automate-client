import typing as t

import pytest

from globus_automate_client.models import FlowDefinition, FlowValidationError

expected_top_level_fields = {
    "StartAt": "SimplePass",
    "Comment": "This is allowed",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "Parameters": {},
            "End": True,
        },
    },
}

unexpected_top_level_fields = {
    "StartAt": "SimplePass",
    "Comment": "This is allowed",
    "SomeCustomField": "This is disallowed",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "Parameters": {},
            "End": True,
        },
    },
}

missing_start_at_field = {
    "Comment": "This is allowed",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "Parameters": {},
            "End": True,
        },
    },
}

missing_states_field = {
    "StartAt": "SimplePass",
    "Comment": "This is allowed",
}

missing_start_at_and_states_fields = {
    "Comment": "This is allowed",
}

empty_flow_definition: t.Dict[str, str] = {}

valid_flow_definitions = [expected_top_level_fields]
invalid_flow_definitions = [
    unexpected_top_level_fields,
    missing_start_at_field,
    missing_states_field,
    empty_flow_definition,
    missing_start_at_and_states_fields,
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
