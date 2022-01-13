import typing as t

import pytest

from globus_automate_client.models import FlowDefinition, FlowValidationError

simple_action_state = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "ActionUrl": "http://localhost:5000",
            "Parameters": {},
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}

action_state_with_catcher = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
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
        },
        "TerminalState": {"Type": "Fail"},
    },
}

action_state_with_multiple_catchers = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
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
        },
        "TerminalState": {"Type": "Fail"},
    },
}

action_state_with_catchers_with_invalid_result_path = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
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
        },
        "TerminalState": {"Type": "Fail"},
    },
}

action_state_with_catchers_with_empty_errors = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
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
        },
        "TerminalState": {"Type": "Fail"},
    },
}

action_state_with_catchers_with_undefined_next = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
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
                }
            ],
        },
    },
}

action_state_with_exception_on_fail = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "ActionUrl": "http://localhost:5000",
            "Parameters": {},
            "ResultPath": "$.some_path",
            "End": True,
            "ExceptionOnActionFailure": True,
        },
    },
}


action_state_with_non_boolean_exception_on_fail = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "ActionUrl": "http://localhost:5000",
            "Parameters": {},
            "ResultPath": "$.some_path",
            "End": True,
            "ExceptionOnActionFailure": "True",
        },
    },
}

invalid_action_url = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "ActionUrl": "localhost:5000",
            "Parameters": {},
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}

postgresql_action_url = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "ActionUrl": "pgsql://localhost:5000",
            "Parameters": {},
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}

missing_parameters_and_input_path = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "ActionUrl": "http://localhost:5000",
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}


input_path_is_not_json_path = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "ActionUrl": "http://localhost:5000",
            "InputPath": "NOT_JSON_PATH",
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}

result_path_is_not_json_path = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "ActionUrl": "http://localhost:5000",
            "ResultPath": "NOT_JSON_PATH",
            "End": True,
        },
    },
}

parameters_are_non_dict = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "ActionUrl": "http://localhost:5000",
            "Parameters": True,
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}

nested_parameters_with_json_path_syntax = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "ActionUrl": "http://localhost:5000",
            "Parameters": {"a_json_path.$": "$.a_json_path"},
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}


nested_parameters_with_invalid_json_path_value = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "ActionUrl": "http://localhost:5000",
            "Parameters": {"a_json_path.$": "not_a_json_path"},
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}

missing_action_url = {
    "StartAt": "ActionState",
    "States": {
        "ActionState": {
            "Type": "Action",
            "Comment": "No info",
            "Parameters": True,
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}

valid_flow_definitions = [
    simple_action_state,
    nested_parameters_with_json_path_syntax,
    action_state_with_exception_on_fail,
    action_state_with_catcher,
    action_state_with_multiple_catchers,
]
invalid_flow_definitions = [
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
    action_state_with_catchers_with_undefined_next,
    action_state_with_catchers_with_invalid_result_path,
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
