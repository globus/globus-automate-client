import typing as t

import pytest

from globus_automate_client.models import ActionState, FlowValidationError

action_state_with_catchers_with_invalid_result_path = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "Parameters": {},
    "ResultPath": "$.some_path",
    "End": True,
    "ExceptionOnActionFailure": True,
    "Catch": [
        {
            "ErrorEquals": ["ErrorA", "ErrorB"],
            "Next": "TerminalState",
            "ResultPath": "NOT_A_JSON_PATH",
        }
    ],
}
action_state_with_catchers_with_empty_errors = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "Parameters": {},
    "ResultPath": "$.some_path",
    "End": True,
    "ExceptionOnActionFailure": True,
    "Catch": [
        {
            "ErrorEquals": [],
            "Next": "TerminalState",
        }
    ],
}

action_state_with_catchers_with_extra_fields = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "Parameters": {},
    "ResultPath": "$.some_path",
    "End": True,
    "ExceptionOnActionFailure": True,
    "Catch": [
        {
            "ErrorEquals": ["ErrorA"],
            "Next": "TerminalState",
            "ThisIsAnExtraField": True,
        }
    ],
}


action_state_with_non_boolean_exception_on_fail = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "Parameters": {},
    "ResultPath": "$.some_path",
    "End": True,
    "ExceptionOnActionFailure": "True",
}

invalid_action_url = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "localhost:5000",
    "Parameters": {},
    "ResultPath": "$.some_path",
    "End": True,
}

postgresql_action_url = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "pgsql://localhost:5000",
    "Parameters": {},
    "ResultPath": "$.some_path",
    "End": True,
}
missing_parameters_and_input_path = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "ResultPath": "$.some_path",
    "End": True,
}


input_path_is_not_json_path = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "InputPath": "NOT_JSON_PATH",
    "ResultPath": "$.some_path",
    "End": True,
}

result_path_is_not_json_path = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "ResultPath": "NOT_JSON_PATH",
    "End": True,
}

parameters_are_non_dict = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "Parameters": True,
    "ResultPath": "$.some_path",
    "End": True,
}


nested_parameters_with_invalid_json_path_value = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "Parameters": {"a_json_path.$": "not_a_json_path"},
    "ResultPath": "$.some_path",
    "End": True,
}

missing_action_url = {
    "Type": "Action",
    "Comment": "No info",
    "Parameters": True,
    "ResultPath": "$.some_path",
    "End": True,
}

simple_action_state: t.Dict[str, t.Any] = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "Parameters": {},
    "ResultPath": "$.some_path",
    "End": True,
}

action_state_with_catcher: t.Dict[str, t.Any] = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "Parameters": {},
    "ResultPath": "$.some_path",
    "End": True,
    "ExceptionOnActionFailure": True,
    "Catch": [
        {
            "ErrorEquals": ["ErrorA", "ErrorB"],
            "Next": "TerminalState",
        }
    ],
}

action_state_with_multiple_catchers: t.Dict[str, t.Any] = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "Parameters": {},
    "ResultPath": "$.some_path",
    "End": True,
    "ExceptionOnActionFailure": True,
    "Catch": [
        {
            "ErrorEquals": ["ErrorA", "ErrorB"],
            "Next": "TerminalState",
        },
        {
            "ErrorEquals": ["ErrorC"],
            "Next": "TerminalState",
        },
    ],
}

nested_parameters_with_json_path_syntax: t.Dict[str, t.Any] = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "Parameters": {"a_json_path.$": "$.a_json_path"},
    "ResultPath": "$.some_path",
    "End": True,
}

action_state_with_exception_on_fail: t.Dict[str, t.Any] = {
    "Type": "Action",
    "Comment": "No info",
    "ActionUrl": "http://localhost:5000",
    "Parameters": {},
    "ResultPath": "$.some_path",
    "End": True,
    "ExceptionOnActionFailure": True,
}


valid_state_definitions = [
    action_state_with_catcher,
    action_state_with_multiple_catchers,
    simple_action_state,
    nested_parameters_with_json_path_syntax,
    action_state_with_exception_on_fail,
]

invalid_state_definitions = [
    invalid_action_url,
    postgresql_action_url,
    missing_parameters_and_input_path,
    result_path_is_not_json_path,
    input_path_is_not_json_path,
    parameters_are_non_dict,
    nested_parameters_with_invalid_json_path_value,
    missing_action_url,
    action_state_with_non_boolean_exception_on_fail,
    action_state_with_catchers_with_empty_errors,
    action_state_with_catchers_with_invalid_result_path,
    action_state_with_catchers_with_extra_fields,
]


@pytest.mark.parametrize("state_def", valid_state_definitions)
def test_valid_action_states_pass_validation(state_def: t.Dict[str, t.Any]):
    state_model = ActionState(**state_def)
    state_def_out = state_model.dict(exclude_unset=True)
    assert state_def_out == state_def


@pytest.mark.parametrize("state_def", invalid_state_definitions)
def test_invalid_action_states_fail_validation(state_def: t.Dict[str, t.Any]):
    with pytest.raises(FlowValidationError) as ve:
        ActionState(**state_def)

    assert ve.type is FlowValidationError
