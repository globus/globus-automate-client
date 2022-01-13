import typing as t

import pytest

from globus_automate_client.models import ExpressionEvalState, FlowValidationError

simple_eval_state = {
    "Type": "ExpressionEval",
    "Comment": "No info",
    "Parameters": None,
    "ResultPath": "$.some_path",
    "End": True,
}

nested_parameters_with_json_path_syntax = {
    "Type": "ExpressionEval",
    "Comment": "No info",
    "Parameters": {"nested_json_path.$": "$.some_path"},
    "ResultPath": "$.some_path",
    "End": True,
}


nested_parameters_with_invalid_json_path_value = {
    "Type": "ExpressionEval",
    "Comment": "No info",
    "Parameters": {"invalid_json_path_indicator.$": "$$$$some_path"},
    "ResultPath": "$.some_path",
    "End": True,
}

missing_next_and_end = {
    "Type": "ExpressionEval",
    "Comment": "No info",
    "Parameters": None,
    "ResultPath": "$.some_path",
}

result_path_is_non_jsonpath = {
    "Type": "ExpressionEval",
    "Comment": "No info",
    "Parameters": None,
    "ResultPath": "NOT_JSON_PATH",
    "End": True,
}

parameters_are_non_dict = {
    "Type": "ExpressionEval",
    "Comment": "No info",
    "Parameters": "None",
    "ResultPath": "$.some_path",
    "End": True,
}

extra_fields_set = {
    "Type": "ExpressionEval",
    "Comment": "No info",
    "Parameters": None,
    "ResultPath": "$.some_path",
    "End": True,
    "Endd": True,
}

valid_state_definitions = [simple_eval_state, nested_parameters_with_json_path_syntax]
invalid_state_definitions = [
    missing_next_and_end,
    result_path_is_non_jsonpath,
    parameters_are_non_dict,
    extra_fields_set,
    nested_parameters_with_invalid_json_path_value,
]


@pytest.mark.parametrize("state_def", valid_state_definitions)
def test_valid_expression_eval_states_pass_validation(state_def: t.Dict[str, t.Any]):
    state_model = ExpressionEvalState(**state_def)
    state_def_out = state_model.dict(exclude_unset=True)
    assert state_def_out == state_def


@pytest.mark.parametrize("state_def", invalid_state_definitions)
def test_invalid_expression_eval_states_fail_validation(state_def: t.Dict[str, t.Any]):
    with pytest.raises(FlowValidationError) as ve:
        ExpressionEvalState(**state_def)

    assert ve.type is FlowValidationError
