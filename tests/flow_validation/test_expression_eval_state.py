import typing as t

import pytest

from globus_automate_client.models import FlowDefinition, FlowValidationError

simple_eval_state = {
    "StartAt": "ExpressionEval",
    "States": {
        "ExpressionEval": {
            "Type": "ExpressionEval",
            "Comment": "No info",
            "Parameters": None,
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}

nested_parameters_with_json_path_syntax = {
    "StartAt": "ExpressionEval",
    "States": {
        "ExpressionEval": {
            "Type": "ExpressionEval",
            "Comment": "No info",
            "Parameters": {"nested_json_path.$": "$.some_path"},
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}


nested_parameters_with_invalid_json_path_value = {
    "StartAt": "ExpressionEval",
    "States": {
        "ExpressionEval": {
            "Type": "ExpressionEval",
            "Comment": "No info",
            "Parameters": {"invalid_json_path_indicator.$": "$$$$some_path"},
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}

missing_next_and_end = {
    "StartAt": "ExpressionEval",
    "States": {
        "ExpressionEval": {
            "Type": "ExpressionEval",
            "Comment": "No info",
            "Parameters": None,
            "ResultPath": "$.some_path",
        },
    },
}

result_path_is_non_jsonpath = {
    "StartAt": "ExpressionEval",
    "States": {
        "ExpressionEval": {
            "Type": "ExpressionEval",
            "Comment": "No info",
            "Parameters": None,
            "ResultPath": "NOT_JSON_PATH",
            "End": True,
        },
    },
}

parameters_are_non_dict = {
    "StartAt": "ExpressionEval",
    "States": {
        "ExpressionEval": {
            "Type": "ExpressionEval",
            "Comment": "No info",
            "Parameters": "None",
            "ResultPath": "$.some_path",
            "End": True,
        },
    },
}

extra_fields_set = {
    "StartAt": "ExpressionEval",
    "States": {
        "ExpressionEval": {
            "Type": "ExpressionEval",
            "Comment": "No info",
            "Parameters": None,
            "ResultPath": "$.some_path",
            "End": True,
            "Endd": True,
        },
    },
}


valid_flow_definitions = [simple_eval_state, nested_parameters_with_json_path_syntax]
invalid_flow_definitions = [
    missing_next_and_end,
    result_path_is_non_jsonpath,
    parameters_are_non_dict,
    extra_fields_set,
    nested_parameters_with_invalid_json_path_value,
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
