import json
import os
import pathlib
from typing import Any, Dict, Union

import pytest
import yaml

from globus_automate_client import flows_client

VALID_FLOW_DEFINITION = {
    "StartAt": "perfect",
    "States": {
        "perfect": {
            "Type": "Pass",
            "End": True,
        },
    },
}


@pytest.fixture
def fc():
    client = flows_client.FlowsClient("client", flows_client.AccessTokenAuthorizer)
    original_authorizer = client.authorizer
    yield client
    assert client.authorizer is original_authorizer


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

    flows_client.validate_flow_definition(VALID_FLOW_DEFINITION)


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


def test_use_temporary_authorizer(fc):
    """Verify the authorizer instance variable is swapped temporarily."""

    original = fc.authorizer
    replacement = flows_client.AccessTokenAuthorizer("bogus")

    with fc.use_temporary_authorizer(replacement):
        assert fc.authorizer is replacement
    assert fc.authorizer is original

    with pytest.raises(ValueError):
        with fc.use_temporary_authorizer(replacement):
            assert fc.authorizer is replacement
            raise ValueError
    assert fc.authorizer is original


def test_deploy_flow_data_construction(fc, mocked_responses):
    """Verify the flow JSON data is constructed correctly."""

    mocked_responses.add("POST", "https://flows.api.globus.org/flows")
    expected: Dict[str, Union[str, Dict[str, Any]]] = {
        "definition": VALID_FLOW_DEFINITION,
        "input_schema": {"Comment": "flow-input-schema"},
        "title": "--title--",
        "subtitle": "--subtitle--",
        "description": "--description--",
        "keywords": "--keywords--",
        "flow_viewers": ["--flow_viewers--"],
        "flow_starters": ["--flow_starters--"],
        "flow_administrators": ["--flow_administrators--"],
        "subscription_id": "--subscription_id--",
    }
    fc.deploy_flow(
        # Arguments that affect the JSON data
        flow_definition=expected["definition"],
        input_schema=expected["input_schema"],
        title=expected["title"],
        subtitle=expected["subtitle"],
        description=expected["description"],
        keywords=expected["keywords"],
        flow_viewers=expected["flow_viewers"],
        flow_starters=expected["flow_starters"],
        flow_administrators=expected["flow_administrators"],
        subscription_id=expected["subscription_id"],
        # Other arguments
        validate_definition=True,
        validate_schema=True,
        dry_run=False,
    )
    data = json.loads(mocked_responses.calls[0].request.body)
    assert data == expected


@pytest.mark.parametrize("input_schema, expected", ((None, False), ({}, True)))
def test_deploy_flow_exclude_most_false_values(
    fc, mocked_responses, input_schema, expected
):
    """Verify the *input_schema* is not excluded even if it's false-y."""

    mocked_responses.add("POST", "https://flows.api.globus.org/flows")
    fc.deploy_flow(
        # Included arguments
        flow_definition=VALID_FLOW_DEFINITION,
        title="--title--",
        input_schema=input_schema,
        # Excluded arguments
        subtitle="",
        description=None,
        # Other arguments
        validate_definition=False,
        validate_schema=False,
        dry_run=False,
    )
    data = json.loads(mocked_responses.calls[0].request.body)
    assert "subtitle" not in data
    assert "description" not in data
    assert ("input_schema" in data) is expected


@pytest.mark.parametrize("dry_run, path", ((False, "flows"), (True, "flows/dry-run")))
def test_deploy_flow_dry_run(fc, mocked_responses, dry_run, path):
    """Verify the *dry_run* parameter affects the URL path."""

    url = f"https://flows.api.globus.org/{path}"
    mocked_responses.add("POST", url)
    fc.deploy_flow(
        flow_definition=VALID_FLOW_DEFINITION,
        title="bogus",
        validate_schema=False,
        dry_run=dry_run,
    )
    assert mocked_responses.calls[0].request.url == url


def test_deploy_flow_aliases(fc, mocked_responses):
    """Verify that viewer/starter/admin aliases are still supported."""

    mocked_responses.add("POST", "https://flows.api.globus.org/flows")
    fc.deploy_flow(
        # Flow viewers and aliases
        flow_viewers=["v1", "v2"],
        visible_to=["v3"],
        viewers=["v4"],
        # Flow starters and aliases
        flow_starters=["s1", "s2"],
        runnable_by=["s3"],
        starters=["s4"],
        # Flow admins and aliases
        flow_administrators=["a1", "a2"],
        administered_by=["a3"],
        administrators=["a4"],
        # Everything below is mandatory but irrelevant to this test.
        flow_definition=VALID_FLOW_DEFINITION,
        title="",
        validate_definition=False,
        validate_schema=False,
    )
    data = json.loads(mocked_responses.calls[0].request.body)
    assert set(data["flow_viewers"]) == {"v1", "v2", "v3", "v4"}
    assert set(data["flow_starters"]) == {"s1", "s2", "s3", "s4"}
    assert set(data["flow_administrators"]) == {"a1", "a2", "a3", "a4"}
