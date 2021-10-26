import pytest

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
