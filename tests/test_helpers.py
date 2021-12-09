import pytest

from globus_automate_client import helpers


@pytest.mark.parametrize(
    "args, expected, message",
    (
        # Null
        ((None, {}), None, "If nothing is specified, None must be returned"),
        #
        # List with no dict keys
        (([], {}), set(), "empty list identity not maintained"),
        ((["1"], {}), {"1"}, "list identity not maintained"),
        ((["1", "1"], {}), {"1"}, "deduplication not performed"),
        ((["1", "2"], {}), {"1", "2"}, "unique items missing"),
        #
        # Dict with no list
        ((None, {}, "-"), None, "dict without matching key must return None"),
        ((None, {"k": ["1"]},), None, "dict with no key specified must return None"),
        ((None, {"k": ["1"]}, "-"), None, "dict without matching key must return None"),
        ((None, {"k": ["1"]}, "k"), {"1"}, "dict with matching key must be added"),
        ((None, {"k": ["1", "1"]}, "k"), {"1"}, "dict values must be de-duped"),
        (
            (None, {"k1": ["1"], "k2": ["1"]}, "k1", "k2"),
            {"1"},
            "dict values must be de-duped",
        ),
        (
            (None, {"k1": ["1"], "k2": ["2"]}, "k1", "k2"),
            {"1", "2"},
            "dict values must all be added",
        ),
        #
        # Dict with scalar values
        ((None, {"k": "1"}, "k"), {"1"}, "scalar value must be added"),
        (
            (None, {"k1": "1", "k2": "1"}, "k1", "k2"),
            {"1"},
            "scalar values must be de-duped",
        ),
        #
        # List combined with a dict
        ((["1"], {"k": ["2"]}, "-"), {"1"}, "combo w/o matching key must not be added"),
        ((["1"], {"k": ["2"]}, "k"), {"1", "2"}, "combo w/ matching key must be added"),
        ((["1"], {"k": ["1"]}, "k"), {"1"}, "combo values must be de-duplicated"),
        ((["1"], {"k": "2"}, "k"), {"1", "2"}, "combo w/ scalar value must be added"),
        # Multiple values
        (
            (["1", "2"], {"k1": "3", "k2": ["4"], "k3": "5"}, "k2", "k3", "-"),
            {"1", "2", "4", "5"},
            "all values must be found",
        ),
    ),
)
def test_merge_keywords(args, expected, message):
    """Validate globus_automate_client.helpers.merge_lists()."""

    original_key_count = len(args[1])
    result = helpers.merge_keywords(*args)
    final_key_count = len(args[1])
    expected_key_count = original_key_count - (len(args) - 2)
    if "-" in args:
        expected_key_count += 1  # One key was bogus
    if expected is None:
        assert result is None, message
        assert final_key_count == original_key_count, "dict unexpectedly modified"
    else:
        assert result is not None, "*result* must not be None"
        assert set(result) == expected, message
        assert final_key_count == expected_key_count, "dicts not modified correctly"
