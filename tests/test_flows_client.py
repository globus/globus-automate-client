import json
import os
import pathlib

import pytest
import yaml

from globus_automate_client import flows_client


@pytest.mark.parametrize(
    "d, names, stop_names, expected, message",
    (
        # Empty inputs and outputs
        ({}, set(), None, set(), "nothing should be returned"),
        ({}, {"i"}, None, set(), "nothing should be returned"),
        ({}, set(), {"x"}, set(), "nothing should be returned"),
        ({}, {"i"}, {"x"}, set(), "nothing should be returned"),
        ({"i": "1"}, set(), None, set(), "nothing should be returned"),
        ({"i": 123}, {"i"}, None, set(), "nothing should be returned"),
        ({"i": [123]}, {"i"}, None, set(), "nothing should be returned"),
        ({"x": "1"}, {"i"}, None, set(), "nothing should be returned"),
        ({"x": "1"}, set(), {"x"}, set(), "nothing should be returned"),
        #
        # Corner case behavior
        ({"x": "1"}, {"x"}, {"x"}, {"1"}, "failed to find str (corner case)"),
        #
        # Test includes
        ({"i": "1"}, {"i"}, None, {"1"}, "failed to find top-level str"),
        ({"i": {"i": "1"}}, {"i"}, None, {"1"}, "failed to find str in dict"),
        ({"i": ["1"]}, {"i"}, None, {"1"}, "failed to find str in list"),
        ({"i": ["1", "2"]}, {"i"}, None, {"1", "2"}, "failed to find values in list"),
        ({"i": ["1", {"i": "2"}]}, {"i"}, None, {"1", "2"}, "failed to find values"),
        ({"i": [{"i": "1"}]}, {"i"}, None, {"1"}, "failed to find str in list->dict"),
        #
        # Test excludes
        ({"x": {"i": "1"}}, {"i"}, {"x"}, set(), "found str in excluded dict"),
    ),
)
def test_all_vals_for_keys(d, names, stop_names, expected, message):
    """Validate values are found or ignored correctly."""

    assert flows_client._all_vals_for_keys(names, d, stop_names) == expected, message


def test_validate_flow_definition_valid():
    """Confirm that valid and well-formed schema raise no errors."""

    schema = {
        "StartAt": "perfect",
        "States": {
            "perfect": {
                "Type": "Pass",
                "End": True,
            },
        },
    }
    flows_client.validate_flow_definition(schema)


def test_validate_flow_definition_multiple_validity_errors():
    """Confirm that validity checks can report multiple errors."""

    schema = {
        # "StartAt" is missing
        "States": {
            "bogus": {},
        },
    }
    with pytest.raises(flows_client.FlowValidationError) as raised:
        flows_client.validate_flow_definition(schema)
    assert "'StartAt' is a required property" in raised.value.args[0]
    assert "'States.bogus'" in raised.value.args[0]


def test_validate_flow_definition_multiple_ill_formed_errors():
    """Confirm that well-formed checks can report multiple errors."""

    schema = {
        "StartAt": "undefined",
        "States": {
            "unreferenced": {
                "Type": "Pass",
                "End": True,
            },
        },
    }
    with pytest.raises(flows_client.FlowValidationError) as raised:
        flows_client.validate_flow_definition(schema)
    assert "not referenced" in raised.value.args[0]
    assert "not defined" in raised.value.args[0]


input_schemas = pathlib.Path(__file__).parent.rglob("../examples/**/*schema.*")


@pytest.mark.parametrize("filename", input_schemas)
def test_validate_input_schema(filename):
    """Confirm that example input schemas all validate correctly."""

    if "invalid" in filename.name:
        pytest.xfail(f"{filename} is invalid according to its filename")
    with filename.open() as file:
        if filename.suffix == ".json":
            schema = json.load(file)
        else:  # filename.suffix == ".yaml"
            schema = yaml.safe_load(file)
    flows_client.validate_input_schema(schema)


@pytest.mark.parametrize("schema", (None, set()))
def test_validate_input_schema_bad_type(schema):
    """Confirm that a bad input type results in failures."""

    with pytest.raises(flows_client.FlowValidationError):
        flows_client.validate_input_schema(schema)


def test_validate_input_schema_multiple_failures():
    """Confirm that an invalid schema can report multiple errors."""

    schema = {
        "properties": {
            "trouble": {
                "type": "bogus",
            },
        },
        "required": False,
    }
    with pytest.raises(flows_client.FlowValidationError) as raised:
        flows_client.validate_input_schema(schema)
    assert "'properties.trouble.type' invalid" in raised.value.args[0]
    assert "'required' invalid" in raised.value.args[0]


@pytest.mark.parametrize(
    "value, expected",
    (
        (None, "https://flows.globus.org"),
        ("prod", "https://flows.globus.org"),
        ("bogus", ValueError),
    ),
)
def test_get_flows_base_url_for_environment_known(monkeypatch, value, expected):
    """Verify that env variables and base URL's are associated correctly."""

    monkeypatch.setattr(os.environ, "get", lambda x: value)
    if expected is ValueError:
        with pytest.raises(ValueError):
            flows_client._get_flows_base_url_for_environment()
    else:
        assert flows_client._get_flows_base_url_for_environment() == expected
