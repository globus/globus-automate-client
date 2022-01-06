import typing as t

import pytest

from globus_automate_client.models import FlowDefinition, FlowValidationError

valid_start_state = {
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "End": True,
        },
    },
}

non_existant_start_state = {
    "StartAt": "DoesNotExistAsAState",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "End": True,
        },
    },
}

non_existant_next_state = {
    "StartAt": "DoesNotExistAsAState",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "Next": "SimplePass2",
        },
        "SimplePass2": {
            "Type": "Pass",
            "End": True,
        },
    },
}

multiple_end_states_defined = {
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "End": True,
        },
        "SimplePass2": {
            "Type": "Pass",
            "End": True,
        },
    },
}

both_next_and_end_states_defined = {
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "Comment": "both_next_and_end_states_defined",
            "Next": "SimplePass2",
            "End": True,
        },
    },
}

action_catch_refers_to_nonexistent_state = {
    "StartAt": "SimpleAction",
    "States": {
        "SimpleAction": {
            "Type": "Action",
            "ActionUrl": "https://actions.automate.globus.org/hello_world",
            "Parameters": {},
            "Catch": [
                {
                    "ErrorEquals": ["SomeError"],
                    "Next": "NotAState",
                }
            ],
            "End": True,
        },
    },
}

choice_state_default_refers_to_nonexistent_state = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Default": "NotAState",
            "Choices": [
                {
                    "Variable": "$.some_variable",
                    "BooleanEquals": False,
                    "Next": "FinalState",
                }
            ],
        },
        "FinalState": {
            "Type": "Pass",
            "End": True,
        },
    },
}

choice_state_rule_refers_to_nonexistent_state = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Default": "FinalState",
            "Choices": [
                {
                    "Variable": "$.some_variable",
                    "BooleanEquals": False,
                    "Next": "NotAState",
                }
            ],
        },
        "FinalState": {
            "Type": "Pass",
            "End": True,
        },
    },
}

unreferenced_state_defined = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Default": "FinalState",
            "Choices": [
                {
                    "Variable": "$.some_variable",
                    "BooleanEquals": False,
                    "Next": "NotAState",
                }
            ],
        },
        "SuperfluousState": {
            "Type": "Pass",
            "Next": "FinalState",
        },
        "FinalState": {
            "Type": "Pass",
            "End": True,
        },
    },
}

valid_flow_definitions = [valid_start_state]
invalid_flow_definitions = [
    non_existant_start_state,
    non_existant_next_state,
    multiple_end_states_defined,
    both_next_and_end_states_defined,
    action_catch_refers_to_nonexistent_state,
    choice_state_default_refers_to_nonexistent_state,
    choice_state_rule_refers_to_nonexistent_state,
    unreferenced_state_defined,
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
