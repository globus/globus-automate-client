import json
import os
import pathlib
import urllib.parse
from typing import Any, Dict, Union, cast
from unittest.mock import Mock

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
        (None, flows_client.PROD_FLOWS_BASE_URL),
        ("prod", flows_client.PROD_FLOWS_BASE_URL),
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


def test_deploy_flow_data_construction(fc, mocked_responses):
    """Verify the flow JSON data is constructed correctly."""

    mocked_responses.add("POST", f"{flows_client.PROD_FLOWS_BASE_URL}/flows")
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
def test_deploy_flow_only_exclude_input_schema_if_none(
    fc, mocked_responses, input_schema, expected
):
    """Verify the *input_schema* is not excluded even if it's false-y."""

    mocked_responses.add("POST", f"{flows_client.PROD_FLOWS_BASE_URL}/flows")
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

    url = f"{flows_client.PROD_FLOWS_BASE_URL}/{path}"
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

    mocked_responses.add("POST", f"{flows_client.PROD_FLOWS_BASE_URL}/flows")
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


@pytest.mark.parametrize("method", ("deploy_flow", "update_flow"))
def test_invalid_flow_definition_failure(fc, method):
    """Verify that an invalid flow definition triggers a failure."""

    with pytest.raises(flows_client.FlowValidationError):
        getattr(fc, method)(
            flow_id="bogus-id",
            flow_definition={"bogus": True},
            title="title",
            validate_definition=True,
        )


@pytest.mark.parametrize("method", ("deploy_flow", "update_flow"))
def test_invalid_input_schema_failure(fc, method):
    """Verify that an invalid input schema triggers a failure."""

    with pytest.raises(flows_client.FlowValidationError):
        getattr(fc, method)(
            flow_id="bogus-id",
            flow_definition=VALID_FLOW_DEFINITION,
            input_schema={"required": False},
            title="title",
            validate_definition=False,
            validate_schema=True,
        )


def test_update_flow_data_construction(fc, mocked_responses):
    """Verify the flow JSON data is constructed correctly."""

    mocked_responses.add("PUT", f"{flows_client.PROD_FLOWS_BASE_URL}/flows/bogus")
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
    fc.update_flow(
        # Arguments that affect the JSON data
        flow_id="bogus",
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
    )
    data = json.loads(mocked_responses.calls[0].request.body)
    assert data == expected


@pytest.mark.parametrize("input_schema, expected", ((None, False), ({}, True)))
def test_update_flow_exclude_most_false_values(
    fc, mocked_responses, input_schema, expected
):
    """Verify the *input_schema* is not excluded even if it's false-y."""

    mocked_responses.add("PUT", f"{flows_client.PROD_FLOWS_BASE_URL}/flows/bogus")
    fc.update_flow(
        # *input_schema* is being tested for inclusion/exclusion.
        input_schema=input_schema,
        # These are false-y and will always be excluded.
        subtitle="",
        description=None,
        # Mandatory arguments, but not under test.
        flow_id="bogus",
        flow_definition=VALID_FLOW_DEFINITION,
        title="--title--",
        validate_definition=False,
        validate_schema=False,
    )
    data = json.loads(mocked_responses.calls[0].request.body)
    assert "subtitle" in data
    assert "description" not in data
    assert ("input_schema" in data) is expected


def test_update_flow_aliases(fc, mocked_responses):
    """Verify that viewer/starter/admin aliases are still supported."""

    mocked_responses.add("PUT", f"{flows_client.PROD_FLOWS_BASE_URL}/flows/bogus")
    fc.update_flow(
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
        flow_id="bogus",
        flow_definition=VALID_FLOW_DEFINITION,
        title="",
        validate_definition=False,
        validate_schema=False,
    )
    data = json.loads(mocked_responses.calls[0].request.body)
    assert set(data["flow_viewers"]) == {"v1", "v2", "v3", "v4"}
    assert set(data["flow_starters"]) == {"s1", "s2", "s3", "s4"}
    assert set(data["flow_administrators"]) == {"a1", "a2", "a3", "a4"}


def test_get_flow(fc, mocked_responses):
    """Verify the URL that is used to get a flow definition."""

    url = f"{flows_client.PROD_FLOWS_BASE_URL}/flows/bogus"
    mocked_responses.add("GET", url)
    fc.get_flow("bogus")
    assert mocked_responses.calls[0].request.url == url


@pytest.mark.parametrize(
    "role, roles, expected, message",
    (
        (None, None, {}, "parameters incorrectly included"),
        # role
        ("", None, {}, "false-y *role* must not be included"),
        ("1", None, {"filter_role": "1"}, "*role* must be included"),
        # roles
        (None, tuple(), {}, "false-y *roles* must not be included"),
        (None, ("2", "3"), {"filter_roles": "2,3"}, "*roles* must be included"),
        # Precedence
        ("1", ("2", "3"), {"filter_role": "1"}, "*role* must override *roles*"),
    ),
)
def test_list_flows_role_precedence(
    fc, mocked_responses, role, roles, expected, message
):
    """Verify the *role* and *roles* precedence rules."""

    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/flows")
    fc.list_flows(role=role, roles=roles)
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    for key in ("filter_role", "filter_roles"):
        if key in expected:
            assert key in data, message
            assert data[key] == expected[key], f"*{key}* value does not match"
        else:
            assert key not in data, message


@pytest.mark.parametrize(
    "marker, per_page, expected, message",
    (
        (None, None, {}, "parameters incorrectly included"),
        # marker
        ("", None, {}, "false-y *marker* must not be included"),
        ("m", None, {"pagination_token": "m"}, "*marker* must be included"),
        # per_page
        (None, 0, {}, "false-y *per_page* must not be included"),
        (None, 10, {"per_page": "10"}, "*per_page* must be included"),
        # Precedence
        ("m", 10, {"pagination_token": "m"}, "*marker* must override *per_page*"),
    ),
)
def test_list_flows_pagination_parameters(
    fc, mocked_responses, marker, per_page, expected, message
):
    """Verify *marker* and *per_page* precedence rules."""

    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/flows")
    fc.list_flows(marker=marker, per_page=per_page)
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    for key in ("pagination_token", "per_page"):
        if key in expected:
            assert key in data, message
            assert data[key] == expected[key], f"*{key}* value does not match"
        else:
            assert key not in data, message


def test_list_flows_filters(fc, mocked_responses):
    """Verify that filters are applied to the query parameters."""

    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/flows")
    fc.list_flows(role="role", filters={"1": "2", "filter_role": "bogus"})
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    assert data["1"] == "2", "*filters* were not applied to the query"
    assert data["filter_role"] == "role", "*filters* overwrote *role*"


def test_list_flows_orderings(fc, mocked_responses):
    """Verify that orderings are serialized as expected."""

    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/flows")
    fc.list_flows(orderings={"shape": "asc", "color": "DESC", "bogus": "undefined"})
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    assert set(data["orderby"].split(",")) == {
        "shape asc",
        "color DESC",
        "bogus undefined",
    }


def test_delete_flow(fc, mocked_responses):
    """Verify the URL used when deleting a flow."""

    url = f"{flows_client.PROD_FLOWS_BASE_URL}/flows/bogus"
    mocked_responses.add("DELETE", url)
    fc.delete_flow("bogus")
    assert mocked_responses.calls[0].request.url == url


def test_scope_for_flow(fc, mocked_responses):
    """Verify that scopes can be introspected.

    This method relies entirely on ActionClient code.
    """

    mocked_responses.add(
        method="GET",
        url=f"{flows_client.PROD_FLOWS_BASE_URL}/flows/bogus-id",
        json={"globus_auth_scope": "bogus-scope"},
    )
    assert fc.scope_for_flow("bogus-id") == "bogus-scope"


def test_get_authorizer_for_flow_found_in_extras(fc):
    """Verify that an authorizer can be found in *extras*."""

    authorizer = fc._get_authorizer_for_flow("1", "2", {"authorizer": "extra"})
    assert authorizer == "extra", "authorizer not found in *extras* parameter"


@pytest.mark.parametrize(
    "flow_scope, expected",
    (
        (None, "dynamic-lookup"),
        ("", ""),
        ("passed-value", "passed-value"),
    ),
)
def test_get_authorizer_for_flow_scope_lookup(fc, monkeypatch, flow_scope, expected):
    """Verify that scopes are dynamically looked up as needed."""

    monkeypatch.setattr(fc, "scope_for_flow", lambda _: "dynamic-lookup")
    monkeypatch.setattr(fc, "get_authorizer_callback", lambda **x: x)
    result = cast(dict, fc._get_authorizer_for_flow("bogus", flow_scope, {}))
    assert result["flow_scope"] == expected


@pytest.mark.parametrize("dry_run, expected", ((False, "run"), (True, "dry-run")))
def test_run_flow_dry_run(fc, mocked_responses, dry_run, expected):
    """Verify the *dry_run* parameter affects the URL path."""

    url = f"{flows_client.PROD_FLOWS_BASE_URL}/flows/bogus-id/{expected}"
    mocked_responses.add("POST", url)
    fc.run_flow(
        # *dry_run* is being tested.
        dry_run=dry_run,
        # These parameters are necessary but irrelevant.
        flow_id="bogus-id",
        flow_scope="bogus-scope",
        flow_input={},
        authorizer=fc.authorizer,
    )
    assert mocked_responses.calls[0].request.url == url


@pytest.mark.parametrize(
    "run_monitors, monitor_by, run_managers, manage_by, expected, message",
    (
        (None, None, None, None, {}, "empty values should be excluded"),
        # Monitors
        ([], None, None, None, {}, "false-y run_monitors must be excluded"),
        (None, [], None, None, {}, "false-y monitor_by must be excluded"),
        (
            ["mon1", "mon2"],
            None,
            None,
            None,
            {"monitor_by": ["mon1", "mon2"]},
            "run_monitors must be included",
        ),
        (
            None,
            ["mon3"],
            None,
            None,
            {"monitor_by": ["mon3"]},
            "monitor_by must be included",
        ),
        (
            ["mon1", "mon2"],
            ["mon3"],
            None,
            None,
            {"monitor_by": ["mon1", "mon2", "mon3"]},
            "monitor agents must be combined",
        ),
        # Managers
        (None, None, [], None, {}, "false-y run_managers must be excluded"),
        (None, None, None, [], {}, "false-y manage_by must be excluded"),
        (
            None,
            None,
            ["man1", "man2"],
            None,
            {"manage_by": ["man1", "man2"]},
            "run_managers must be included",
        ),
        (
            None,
            None,
            None,
            ["man3"],
            {"manage_by": ["man3"]},
            "manage_by must be included",
        ),
        (
            None,
            None,
            ["man1", "man2"],
            ["man3"],
            {"manage_by": ["man1", "man2", "man3"]},
            "manager agents must be combined",
        ),
    ),
)
def test_run_flow_aliases(
    fc,
    mocked_responses,
    run_monitors,
    monitor_by,
    run_managers,
    manage_by,
    expected,
    message,
):
    """Verify the monitor and manager aliases are functional."""

    mocked_responses.add(
        method="POST",
        url=f"{flows_client.PROD_FLOWS_BASE_URL}/flows/bogus-id/run",
        json={},
    )
    fc.run_flow(
        # These parameters are being tested.
        run_monitors=run_monitors,
        monitor_by=monitor_by,
        run_managers=run_managers,
        manage_by=manage_by,
        # These parameters are necessary but irrelevant.
        flow_id="bogus-id",
        flow_scope="bogus-scope",
        flow_input={},
        authorizer=fc.authorizer,
    )
    data = json.loads(mocked_responses.calls[0].request.body or "{}")
    for key in ("manage_by", "monitor_by"):
        if key in expected:
            assert key in data, f"*{key}* must be in the submitted data"
            assert set(data[key]) == set(expected[key])
        else:
            assert key not in data, f"*{key}* must not be in the submitted data"


@pytest.mark.parametrize(
    "role, roles, expected, message",
    (
        (None, None, {}, "parameters incorrectly included"),
        # role
        ("", None, {}, "false-y *role* must not be included"),
        ("1", None, {"filter_role": "1"}, "*role* must be included"),
        # roles
        (None, tuple(), {}, "false-y *roles* must not be included"),
        (None, ("2", "3"), {"filter_roles": "2,3"}, "*roles* must be included"),
        # Precedence
        ("1", ("2", "3"), {"filter_role": "1"}, "*role* must override *roles*"),
    ),
)
def test_enumerate_runs_role_precedence(
    fc, mocked_responses, monkeypatch, role, roles, expected, message
):
    """Verify the *role* and *roles* precedence rules."""

    monkeypatch.setattr(fc, "get_authorizer_callback", lambda **x: fc.authorizer)
    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/runs")
    fc.enumerate_runs(role=role, roles=roles)
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    for key in ("filter_role", "filter_roles"):
        if key in expected:
            assert key in data, message
            assert data[key] == expected[key], f"*{key}* value does not match"
        else:
            assert key not in data, message


@pytest.mark.parametrize(
    "marker, per_page, expected, message",
    (
        (None, None, {}, "parameters incorrectly included"),
        # marker
        ("", None, {}, "false-y *marker* must not be included"),
        ("m", None, {"pagination_token": "m"}, "*marker* must be included"),
        # per_page
        (None, 0, {}, "false-y *per_page* must not be included"),
        (None, 10, {"per_page": "10"}, "*per_page* must be included"),
        # Precedence
        ("m", 10, {"pagination_token": "m"}, "*marker* must override *per_page*"),
    ),
)
def test_enumerate_runs_pagination_parameters(
    fc, mocked_responses, monkeypatch, marker, per_page, expected, message
):
    """Verify *marker* and *per_page* precedence rules."""

    monkeypatch.setattr(fc, "get_authorizer_callback", lambda **x: fc.authorizer)
    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/runs")
    fc.enumerate_runs(marker=marker, per_page=per_page)
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    for key in ("pagination_token", "per_page"):
        if key in expected:
            assert key in data, message
            assert data[key] == expected[key], f"*{key}* value does not match"
        else:
            assert key not in data, message


def test_enumerate_runs_filters(fc, mocked_responses, monkeypatch):
    """Verify that filters are applied to the query parameters."""

    monkeypatch.setattr(fc, "get_authorizer_callback", lambda **x: fc.authorizer)
    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/runs")
    fc.enumerate_runs(role="role", filters={"1": "2", "filter_role": "bogus"})
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    assert data["1"] == "2", "*filters* were not applied to the query"
    assert data["filter_role"] == "role", "*filters* overwrote *role*"


def test_enumerate_runs_orderings(fc, mocked_responses, monkeypatch):
    """Verify that orderings are serialized as expected."""

    monkeypatch.setattr(fc, "get_authorizer_callback", lambda **x: fc.authorizer)
    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/runs")
    fc.enumerate_runs(orderings={"shape": "asc", "color": "DESC", "bogus": "bad"})
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    assert set(data["orderby"].split(",")) == {
        "shape asc",
        "color DESC",
        "bogus bad",
    }


def test_enumerate_runs_statuses(fc, mocked_responses, monkeypatch):
    """Verify that orderings are serialized as expected."""

    monkeypatch.setattr(fc, "get_authorizer_callback", lambda **x: fc.authorizer)
    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/runs")
    fc.enumerate_runs(statuses=("SUCCEEDED", "FAILED"))
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    assert set(data["filter_status"].split(",")) == {"SUCCEEDED", "FAILED"}


@pytest.mark.parametrize(
    "role, roles, expected, message",
    (
        (None, None, {}, "parameters incorrectly included"),
        # role
        ("", None, {}, "false-y *role* must not be included"),
        ("1", None, {"filter_role": "1"}, "*role* must be included"),
        # roles
        (None, tuple(), {}, "false-y *roles* must not be included"),
        (None, ("2", "3"), {"filter_roles": "2,3"}, "*roles* must be included"),
        # Precedence
        ("1", ("2", "3"), {"filter_role": "1"}, "*role* must override *roles*"),
    ),
)
def test_list_flow_runs_role_precedence(
    fc, mocked_responses, role, roles, expected, message
):
    """Verify the *role* and *roles* precedence rules."""

    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/flows/-/runs")
    fc.list_flow_runs(
        "-",
        role=role,
        roles=roles,
        authorizer=fc.authorizer,
    )
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    for key in ("filter_role", "filter_roles"):
        if key in expected:
            assert key in data, message
            assert data[key] == expected[key], f"*{key}* value does not match"
        else:
            assert key not in data, message


@pytest.mark.parametrize(
    "marker, per_page, expected, message",
    (
        (None, None, {}, "parameters incorrectly included"),
        # marker
        ("", None, {}, "false-y *marker* must not be included"),
        ("m", None, {"pagination_token": "m"}, "*marker* must be included"),
        # per_page
        (None, 0, {}, "false-y *per_page* must not be included"),
        (None, 10, {"per_page": "10"}, "*per_page* must be included"),
        # Precedence
        ("m", 10, {"pagination_token": "m"}, "*marker* must override *per_page*"),
    ),
)
def test_list_flow_runs_pagination_parameters(
    fc, mocked_responses, marker, per_page, expected, message
):
    """Verify *marker* and *per_page* precedence rules."""

    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/flows/-/runs")
    fc.list_flow_runs(
        "-",
        marker=marker,
        per_page=per_page,
        authorizer=fc.authorizer,
    )
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    for key in ("pagination_token", "per_page"):
        if key in expected:
            assert key in data, message
            assert data[key] == expected[key], f"*{key}* value does not match"
        else:
            assert key not in data, message


def test_list_flow_runs_filters(fc, mocked_responses):
    """Verify that filters are applied to the query parameters."""

    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/flows/-/runs")
    fc.list_flow_runs(
        "-",
        role="role",
        filters={"1": "2", "filter_role": "bogus"},
        authorizer=fc.authorizer,
    )
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    assert data["1"] == "2", "*filters* were not applied to the query"
    assert data["filter_role"] == "role", "*filters* overwrote *role*"


def test_list_flow_runs_orderings(fc, mocked_responses):
    """Verify that orderings are serialized as expected."""

    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/flows/-/runs")
    fc.list_flow_runs(
        "-",
        orderings={"shape": "asc", "color": "DESC", "bogus": "bad"},
        authorizer=fc.authorizer,
    )
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    assert set(data["orderby"].split(",")) == {
        "shape asc",
        "color DESC",
        "bogus bad",
    }


def test_list_flow_runs_statuses(fc, mocked_responses):
    """Verify that orderings are serialized as expected."""

    mocked_responses.add("GET", f"{flows_client.PROD_FLOWS_BASE_URL}/flows/-/runs")
    fc.list_flow_runs(
        "-",
        statuses=("SUCCEEDED", "FAILED"),
        authorizer=fc.authorizer,
    )
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    assert set(data["filter_status"].split(",")) == {"SUCCEEDED", "FAILED"}


def test_list_flow_runs_call_enumerate_runs(fc, monkeypatch):
    """Verify that calls to enumerate_runs() pass all variables."""

    expected = {
        # Explicit
        "statuses": "--statuses--",
        "roles": "--roles--",
        "marker": "--marker--",
        "per_page": "--per_page--",
        "filters": "--filters--",
        "orderings": "--orderings--",
        "role": "--role--",
        # Implicit kwargs
        "authorizer": "--authorizer--",
    }
    additional = {
        "flow_id": None,
        "flow_scope": "--flow_scope--",
    }

    mock = Mock()
    monkeypatch.setattr(fc, "enumerate_runs", mock)
    fc.list_flow_runs(**expected, **additional)
    mock.assert_called_once_with(**expected)


@pytest.mark.parametrize(
    "run_managers, run_monitors, expected, message",
    (
        (None, None, {}, "empty values should be excluded"),
        # Managers
        ([], None, {"run_managers": []}, "false-y run_managers must be included"),
        (["1"], None, {"run_managers": ["1"]}, "run_managers must be included"),
        # Monitors
        (None, [], {"run_monitors": []}, "false-y run_monitors must be included"),
        (None, ["1"], {"run_monitors": ["1"]}, "run_monitors must be included"),
    ),
)
def test_flow_action_update_managers_and_monitors(
    fc, mocked_responses, run_managers, run_monitors, expected, message
):
    """Verify that managers and monitors are unconditionally included."""

    mocked_responses.add("PUT", f"{flows_client.PROD_FLOWS_BASE_URL}/runs/bogus-id")
    fc.flow_action_update(
        # These arguments are being tested.
        run_managers=run_managers,
        run_monitors=run_monitors,
        # Mandatory but irrelevant to the test.
        action_id="bogus-id",
        authorizer=fc.authorizer,
    )
    data = json.loads(mocked_responses.calls[0].request.body)
    for key in ("run_managers", "run_monitors"):
        if key in expected:
            assert key in data, f"*{key}* must be included in the JSON data"
            assert data[key] == expected[key], message
        else:
            assert key not in data, f"*{key}* must not be included in the JSON data"


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


@pytest.mark.parametrize("method", ("status", "log", "cancel", "release", "resume"))
def test_action_client_pass_through_calls(fc, method, monkeypatch):
    """Verify that the correct ActionClient methods are called.

    There is no other validation performed except that the correct
    ActionClient method is called.
    """

    mock = Mock()
    monkeypatch.setattr(flows_client.ActionClient, "new_client", lambda *_, **__: mock)
    getattr(fc, f"flow_action_{method}")(
        flow_id="bogus-id",
        flow_scope="bogus-scope",
        flow_action_id="bogus-action-id",
        authorizer=fc.authorizer,
    )
    getattr(mock, method).assert_called_once()
