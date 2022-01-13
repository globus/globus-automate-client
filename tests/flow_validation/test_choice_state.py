import typing as t

import pytest

from globus_automate_client.models import ChoiceState, FlowValidationError

simple_choice_state = {
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
}


choice_state_using_and = {
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
}

choice_state_using_or = {
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
}

choice_state_using_not = {
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
}

choice_state_using_empty_or = {
    "Type": "Choice",
    "Comment": "No info",
    "Choices": [
        {
            "Or": [],
            "Next": "ChoiceAState",
        }
    ],
    "Default": "DefaultState",
}

choice_state_using_empty_and = {
    "Type": "Choice",
    "Comment": "No info",
    "Choices": [
        {
            "And": [],
            "Next": "ChoiceAState",
        }
    ],
    "Default": "DefaultState",
}

choice_state_using_and_and_or = {
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
}

empty_choices_for_choice_state = {
    "Type": "Choice",
    "Comment": "No info",
    "Choices": [],
    "Default": "DefaultState",
}

extra_fields_set_on_choice_state = {
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
}

choice_state_using_or_where_next_is_defined = {
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
}

choice_state_using_not_where_next_is_defined = {
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
}

choice_state_with_invalid_comparison_operator = {
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
}

choice_state_without_default = {
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
}

choice_state_with_simple_nested_boolean_condition = {
    "Type": "Choice",
    "Comment": "No info",
    "Choices": [
        {
            "Not": {"Not": {"Variable": "$.key", "StringEquals": "value"}},
            "Next": "ChoiceAState",
        }
    ],
    "Default": "DefaultState",
}

choice_state_with_conjunctive_nested_boolean_condition = {
    "Type": "Choice",
    "Comment": "No info",
    "Choices": [
        {
            "Not": {
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
            },
            "Next": "ChoiceAState",
        }
    ],
    "Default": "DefaultState",
}

choice_state_with_conjunctive_nested_boolean_condition_using_next = {
    "Type": "Choice",
    "Comment": "No info",
    "Choices": [
        {
            "Not": {
                "Or": [
                    {
                        "Variable": "$.SomePath.status",
                        "StringEquals": "FAILED",
                        "Next": "DefaultState",
                    },
                    {
                        "Variable": "$.SomePath.status",
                        "StringEquals": "FAILED",
                    },
                ],
            },
            "Next": "ChoiceAState",
        }
    ],
    "Default": "DefaultState",
}

choice_state_with_conjunctive_nested_boolean_condition_with_extra_fields = {
    "Type": "Choice",
    "Comment": "No info",
    "Choices": [
        {
            "Not": {
                "Or": [
                    {
                        "Variable": "$.SomePath.status",
                        "StringEquals": "FAILED",
                        "ThisIsAnExtraField": True,
                    },
                    {
                        "Variable": "$.SomePath.status",
                        "StringEquals": "FAILED",
                    },
                ],
            },
            "Next": "ChoiceAState",
        }
    ],
    "Default": "DefaultState",
}


valid_state_definitions = [
    simple_choice_state,
    choice_state_using_and,
    choice_state_using_or,
    choice_state_using_not,
    choice_state_without_default,
    choice_state_with_simple_nested_boolean_condition,
    choice_state_with_conjunctive_nested_boolean_condition,
]
invalid_state_definitions = [
    choice_state_using_empty_or,
    choice_state_using_empty_and,
    empty_choices_for_choice_state,
    extra_fields_set_on_choice_state,
    choice_state_using_or_where_next_is_defined,
    choice_state_using_not_where_next_is_defined,
    choice_state_with_invalid_comparison_operator,
    choice_state_with_conjunctive_nested_boolean_condition_using_next,
    choice_state_with_conjunctive_nested_boolean_condition_with_extra_fields,
]


@pytest.mark.parametrize("state_def", valid_state_definitions)
def test_valid_choice_states_pass_validation(state_def: t.Dict[str, t.Any]):
    state_model = ChoiceState(**state_def)
    state_def_out = state_model.dict(exclude_unset=True)
    assert state_def_out == state_def


@pytest.mark.parametrize("state_def", invalid_state_definitions)
def test_invalid_choice_states_fail_validation(state_def: t.Dict[str, t.Any]):
    with pytest.raises(FlowValidationError) as ve:
        ChoiceState(**state_def)

    assert ve.type is FlowValidationError
