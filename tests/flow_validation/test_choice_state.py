import typing as t

import pytest

from globus_automate_client.models import FlowDefinition, FlowValidationError

simple_choice_state = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "Choices": [
                {
                    "Variable": "$.SomePath.status",
                    "StringEquals": "FAILED",
                    "Next": "ChoiceAState",
                },
                {
                    "Variable": "$.SomePath.status",
                    "StringEquals": "FAILED",
                    "Next": "DefaultState",
                },
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

invalid_next_in_choice = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "Choices": [
                {
                    "Variable": "$.SomePath.status",
                    "StringEquals": "FAILED",
                    "Next": "NOT_A_STATE",
                }
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

invalid_default_for_choice = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "Choices": [
                {
                    "Variable": "$.SomePath.status",
                    "StringEquals": "FAILED",
                    "Next": "ChoiceAState",
                }
            ],
            "Default": "NotAState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}


choice_state_using_and = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "Choices": [
                {
                    "And": [
                        {
                            "Variable": "$.SomePath.status",
                            "StringEquals": "FAILED",
                        },
                        {
                            "Variable": "$.SomePath.status",
                            "StringEquals": "FAILED",
                        },
                    ],
                    "Next": "ChoiceAState",
                }
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

choice_state_using_or = {
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
                    "Next": "ChoiceAState",
                }
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

choice_state_using_not = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "Choices": [
                {
                    "Not": {
                        "Variable": "$.SomePath.status",
                        "StringEquals": "FAILED",
                    },
                    "Next": "ChoiceAState",
                }
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

choice_state_using_empty_or = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "Choices": [
                {
                    "Or": [],
                    "Next": "ChoiceAState",
                }
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

choice_state_using_empty_and = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "Choices": [
                {
                    "And": [],
                    "Next": "ChoiceAState",
                }
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

choice_state_using_and_and_or = {
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
                    "Next": "ChoiceAState",
                },
                {
                    "And": [
                        {
                            "Variable": "$.SomePath.status",
                            "StringEquals": "FAILED",
                        },
                        {
                            "Variable": "$.SomePath.status",
                            "StringEquals": "FAILED",
                        },
                    ],
                    "Next": "ChoiceAState",
                },
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

empty_choices_for_choice_state = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "Choices": [],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

extra_fields_set_on_choice_state = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "ThisIsAnExtraField": True,
            "Choices": [
                {
                    "Variable": "$.SomePath.status",
                    "StringEquals": "FAILED",
                    "Next": "ChoiceAState",
                },
                {
                    "Variable": "$.SomePath.status",
                    "StringEquals": "FAILED",
                    "Next": "DefaultState",
                },
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

choice_state_using_or_where_next_is_defined = {
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
                            "Next": "ChoiceAState",
                        },
                        {
                            "Variable": "$.SomePath.status",
                            "StringEquals": "FAILED",
                        },
                    ],
                    "Next": "ChoiceAState",
                }
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

choice_state_using_not_where_next_is_defined = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "Choices": [
                {
                    "Not": {
                        "Variable": "$.SomePath.status",
                        "StringEquals": "FAILED",
                        "Next": "ChoiceAState",
                    },
                    "Next": "ChoiceAState",
                }
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}

choice_state_with_invalid_comparison_operator = {
    "StartAt": "ChoiceState",
    "States": {
        "ChoiceState": {
            "Type": "Choice",
            "Comment": "No info",
            "Choices": [
                {
                    "Variable": "$.SomePath.status",
                    "NOT_AN_OPERATOR": "FAILED",
                    "Next": "ChoiceAState",
                },
            ],
            "Default": "DefaultState",
        },
        "DefaultState": {
            "Type": "Fail",
        },
        "ChoiceAState": {
            "Type": "Fail",
        },
    },
}


valid_flow_definitions = [
    simple_choice_state,
    choice_state_using_and,
    choice_state_using_or,
    choice_state_using_not,
]
invalid_flow_definitions = [
    invalid_next_in_choice,
    invalid_default_for_choice,
    choice_state_using_empty_or,
    choice_state_using_empty_and,
    empty_choices_for_choice_state,
    extra_fields_set_on_choice_state,
    choice_state_using_or_where_next_is_defined,
    choice_state_using_not_where_next_is_defined,
    choice_state_with_invalid_comparison_operator,
]


@pytest.mark.parametrize("flow_def", valid_flow_definitions)
def test_valid_flows_pass_validation(flow_def: t.Dict[str, t.Any]):
    FlowDefinition(**flow_def)


@pytest.mark.parametrize("flow_def", invalid_flow_definitions)
def test_invalid_flows_fail_validation(flow_def: t.Dict[str, t.Any]):
    with pytest.raises(FlowValidationError) as ve:
        FlowDefinition(**flow_def)

    assert ve.type is FlowValidationError
    # assert False, ve.value.errors()
