import typing as t

import pytest

from globus_automate_client.models import FlowDefinition, FlowValidationError

# TODO
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
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "Next": "SomeUndefinedState",
        },
        "SimplePass2": {
            "Type": "Pass",
            "End": True,
        },
    },
}

flow_defines_an_unreachable_state = {
    "StartAt": "SimplePass",
    "States": {
        "SimplePass": {
            "Type": "Pass",
            "End": True,
        },
        "UnreachableState": {
            "Type": "Pass",
            "End": True,
        },
    },
}

state_defines_next_and_end_states = {
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

action_catch_refers_to_existing_state = {
    "StartAt": "SimpleAction",
    "States": {
        "SimpleAction": {
            "Type": "Action",
            "ActionUrl": "https://actions.automate.globus.org/hello_world",
            "Parameters": {},
            "Catch": [
                {
                    "ErrorEquals": ["SomeError"],
                    "Next": "HandlerState",
                }
            ],
            "End": True,
        },
        "HandlerState": {
            "Type": "Pass",
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

choice_state_default_refers_to_existing_state = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Default": "FinalState",
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

choice_state_rule_refers_to_existing_state = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Default": "FinalState",
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

boolean_expression_choice_state_refers_to_non_existant_state = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "Choices": [
                {
                    "Or": [
                        {
                            "Variable": "$.SomePath.status",
                            "StringEquals": "FAILED",
                        },
                        {
                            "Variable": "$.SomePath.status",
                            "StringEquals": "FAILED",
                        },
                    ],
                    "Next": "NonExistantState",
                }
            ],
        },
        "FinalState": {
            "Type": "Pass",
            "End": True,
        },
    },
}


valid_flow_definitions = [
    valid_start_state,
    action_catch_refers_to_existing_state,
    choice_state_default_refers_to_existing_state,
    choice_state_rule_refers_to_existing_state,
]
invalid_flow_definitions = [
    non_existant_start_state,
    non_existant_next_state,
    flow_defines_an_unreachable_state,
    state_defines_next_and_end_states,
    action_catch_refers_to_nonexistent_state,
    choice_state_default_refers_to_nonexistent_state,
    choice_state_rule_refers_to_nonexistent_state,
    boolean_expression_choice_state_refers_to_non_existant_state,
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
