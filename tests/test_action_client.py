import json
import urllib.parse
import uuid

import pytest
import responses

from globus_automate_client import action_client


@pytest.fixture
def ac():
    yield action_client.ActionClient()


@pytest.mark.parametrize(
    "data, expected",
    (
        ({"globus_auth_scope": "success"}, "success"),
        ({}, ""),
        (None, ""),
    ),
)
def test_action_scope(ac, mocked_responses, data, expected):
    """Validate the behavior of the action_scope property."""

    mocked_responses.add(
        method=responses.GET,
        url="https://actions.api.globus.org/",
        json=data,
    )
    assert ac._action_scope is None
    assert ac.action_scope == expected
    assert ac._action_scope == expected  # Instance variable
    assert ac.action_scope == expected  # Cache behavior


@pytest.mark.parametrize(
    "name, method",
    (
        ("status", "GET"),
        ("resume", "POST"),
        ("cancel", "POST"),
        ("release", "POST"),
    ),
)
def test_trivial_methods(ac, mocked_responses, name, method):
    """Validate the URL used with trivial requests."""

    action_id = "bogus"
    url = f"https://actions.api.globus.org/{action_id}/{name}"
    mocked_responses.add(method=method, url=url)
    getattr(ac, name)(action_id)  # Dynamically get and call the method by name
    assert mocked_responses.calls[0].request.url == url


@pytest.mark.parametrize("request_id", ("custom", None))
def test_run_with_request_id(ac, mocked_responses, monkeypatch, request_id):
    """Validate that run() uses a specified request ID or generates a new one."""

    url = "https://actions.api.globus.org/run"
    mocked_responses.add(method="POST", url=url)
    monkeypatch.setattr(uuid, "uuid4", lambda: "system")
    ac.run(body={}, request_id=request_id)
    if request_id is None:
        assert b"system" in mocked_responses.calls[0].request.body
    else:
        assert request_id.encode("utf8") in mocked_responses.calls[0].request.body


@pytest.mark.parametrize("force_path", ("/custom", None))
def test_run_with_force_path(ac, mocked_responses, force_path):
    """Validate that run() uses *force_path*, if specified."""

    url = f"https://actions.api.globus.org{force_path or '/run'}"
    mocked_responses.add(method="POST", url=url)
    ac.run(body={}, force_path=force_path)
    assert mocked_responses.calls[0].request.url == url


@pytest.mark.parametrize(
    "kwargs, expected",
    (
        # Managers
        ({"manage_by": ["a"]}, {"manage_by": {"a"}}),
        ({"run_managers": ["b"]}, {"manage_by": {"b"}}),
        ({"manage_by": ["a"], "run_managers": ["b"]}, {"manage_by": {"a", "b"}}),
        # Monitors
        ({"monitor_by": ["a"]}, {"monitor_by": {"a"}}),
        ({"run_monitors": ["b"]}, {"monitor_by": {"b"}}),
        ({"monitor_by": ["a"], "run_monitors": ["b"]}, {"monitor_by": {"a", "b"}}),
    ),
)
def test_run_with_managers_and_monitors(ac, mocked_responses, kwargs, expected):
    """Validate that run() uses managers and monitors, including aliases."""

    mocked_responses.add(method="POST", url="https://actions.api.globus.org/run")
    ac.run(body={}, **kwargs)
    data = json.loads(mocked_responses.calls[0].request.body.decode("utf8"))
    for key in ("monitor_by", "manage_by"):
        if key in expected:
            assert set(data[key]) == expected[key]
        else:
            assert key not in data, f"'{key}' must not be included in the request"


@pytest.mark.parametrize("reverse_order, expected", ((True, True), (False, False)))
def test_log_reverse_order(ac, mocked_responses, reverse_order, expected):
    """Validate the *reverse_order* parameter is managed correctly."""

    action_id = "bogus"
    url = f"https://actions.api.globus.org/{action_id}/log"
    mocked_responses.add(method="GET", url=url, json={})
    ac.log(action_id, reverse_order=reverse_order)
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    assert ("reverse_order" in data) is expected


@pytest.mark.parametrize(
    "marker, per_page, expected",
    (
        (None, None, {}),
        ("1:10", None, {"pagination_token": "1:10"}),
        (None, 10, {"per_page": "10"}),
        ("1:10", 10, {"pagination_token": "1:10"}),
    ),
)
def test_log_pagination(ac, mocked_responses, marker, per_page, expected):
    """Validate the *marker* and *per_page* parameters interact correctly."""

    action_id = "bogus"
    url = f"https://actions.api.globus.org/{action_id}/log"
    mocked_responses.add(method="GET", url=url, json={})
    ac.log(action_id, marker=marker, per_page=per_page)
    query: str = urllib.parse.urlparse(mocked_responses.calls[0].request.url).query
    data = dict(urllib.parse.parse_qsl(query, keep_blank_values=True))
    for key in ("pagination_token", "per_page"):
        if key in expected:
            assert data[key] == expected[key]
        else:
            assert key not in data, f"'{key}' must not appear in the query parameters"


def test_new_client():
    """Validate that new_client() instantiates classes correctly."""

    action_url = "bogus-url"
    authorizer = "bogus-authorizer"
    ac = action_client.ActionClient.new_client(
        action_url=action_url,
        authorizer=authorizer,
    )
    assert "ActionClient" in ac.app_name
    assert ac.base_url == action_url
    assert ac.authorizer == authorizer
