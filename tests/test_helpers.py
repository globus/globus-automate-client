import pytest

from globus_automate_client import helpers


@pytest.mark.parametrize(
    "args, expected, message",
    (
        # List
        (([],), set(), "empty list identity not maintained"),
        (([1],), {1}, "list identity not maintained"),
        (([1, 1],), {1}, "in-list deduplication not performed"),
        (([1], [1]), {1}, "cross-list deduplication not performed"),
        (([1, 2],), {1, 2}, "unique items missing"),
        # Dictionary
        (({}, "k"), None, "dict with no matching key must return None"),
        (({"k": [1]},), None, "dict w/o matching key specified must return None"),
        (({"k": [1]}, "k"), {1}, "dict w/o list and w/ matching key must be added"),
        (([1], {"k": [2]}, "k"), {1, 2}, "dict with matching key must be added"),
        (([1], {"k": [1]}, "k"), {1}, "dict values must be de-duplicated"),
        (([1], {"k": 2}, "k"), {1}, "scalar value in dict must be ignored"),
        # Multiple values
        (
            ([1, 2], [2, 3], {"k1": [4], "k2": [5], "k3": [6]}, "k2", "k3", "bogus"),
            {1, 2, 3, 5, 6},
            "all values must be found",
        ),
    ),
)
def test_merge_lists(args, expected, message):
    """Validate globus_automate_client.helpers.merge_lists()."""

    original_lengths = sum(len(d) for d in args if isinstance(d, dict))
    result = helpers.merge_lists(*args)
    final_lengths = sum(len(d) for d in args if isinstance(d, dict))
    if expected is None:
        assert result is None, message
        assert original_lengths == final_lengths, "dicts modified despite no matches"
    else:
        assert result is not None, "*result* must not be None"
        assert set(result) == expected, message
        if original_lengths:
            assert original_lengths > final_lengths, "dicts not modified"


@pytest.mark.parametrize(
    "pop, args, expected, message",
    (
        (True, ({"k": [1]}, "k"), {}, "dict not modified when match found"),
        (True, ({"k": [1]}, "x"), {"k": [1]}, "dict modified when no match found"),
        (False, ({"k": [1]}, "k"), {"k": [1]}, "dict modified when match found"),
        (False, ({"k": [1]}, "x"), {"k": [1]}, "dict modified when no match found"),
    ),
)
def test_merge_lists_pop_behavior(args, pop, expected, message):
    """Validate input dicts are (or are not) modified in-place."""

    helpers.merge_lists(*args, pop_dict_lists=pop)
    assert args[0] == expected, message
