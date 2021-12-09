from typing import Dict, Iterable, List, Optional, Set, Union


def merge_keywords(
    base: Optional[Iterable[str]],
    kwargs: Dict[str, Union[str, Iterable[str]]],
    *keywords: str,
) -> Optional[List[str]]:
    """Merge all given keyword parameter aliases and deduplicate the values.

    ..  warning::

        This function has a side-effect. It deliberately modifies *kwargs* in-place.
        Any keyword alias that exists in *kwargs* will be removed from *kwargs*.

    If an alias key exists in *kwargs* and has a value other than None
    then it will be included in the final result that is returned.

    If *base* is None and all found aliases have a value of None,
    then None will be returned.

    For example, given a function with the following call signature:

    ..  code-block:: python

        def example(names=None, **kwargs):
            pass

    It is possible to quickly add support for additional parameter names
    so that users can call the function with alternative keyword parameters:

    ..  code-block:: python

        all_names = merge_keywords(names, kwargs, "pseudonyms", "nicknames")

    """

    result: Optional[Set[str]] = None
    if base is not None:
        result = set(base)

    for keyword in keywords:
        # Consume the keyword alias.
        # NOTE: .pop() is a destructive operation with a deliberate side-effect.
        value = kwargs.pop(keyword, None)
        if value is None:
            continue

        # Update the final result.
        if result is None:
            result = set()
        if isinstance(value, str):
            result.add(value)
        else:
            result |= set(value)

    if result is None:
        return None
    return list(result)
