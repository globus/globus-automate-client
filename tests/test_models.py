import json
import pathlib

import pytest
from pydantic import ValidationError

from globus_automate_client.flow_model import (
    FlowDefinition,
    GlobusValidationException,
    NextOrEnd,
)


def test_next_or_end():
    try:
        ne = NextOrEnd()
        print(ne)
    except ValidationError as ve:
        print(ve)


flow_def = {
    "StartAt": "ActionState",
    "Comment": "My Flow",
    "States": {
        "ActionState": {
            "Type": "Action",
            "ActionUrl": "http://foo.bar",
            "InputPath": "foo",
            "Next": "EvalState",
        },
        "EvalState": {
            "Type": "ExpressionEval",
            "Parameters": {"foo.$": "aaa"},
            "ResultPath": "$.foo",
            "Next": "PassState",
        },
        "PassState": {
            "Type": "Pass",
            "End": True,
            "Parameters": {"ref.$": ["$.not_a_ref"]},
        },
    },
}


file_path = (pathlib.Path(__file__).parent / "files/flow_validation/").resolve()


def use_filename(path: pathlib.Path):
    """Generate a nicer test ID using an incoming filename."""
    return path.name


@pytest.mark.parametrize("filename", file_path.glob("*.valid.json"))
def test_valid_definition(filename: pathlib.Path):
    fd = FlowDefinition.from_json(filename.read_text())
    print(fd)


@pytest.mark.parametrize("filename", file_path.glob("*.invalid.json"))
def test_invalid_definition(filename: pathlib.Path):
    with pytest.raises(GlobusValidationException) as gve:
        fd = FlowDefinition.from_json(filename.read_text())
        print(fd)
    print(str(gve))
