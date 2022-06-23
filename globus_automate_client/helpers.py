from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union


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


def validate_aliases(
    canonical_item: Tuple[str, Any],
    *aliases: Tuple[str, Any],
) -> Any:
    """Validate and standardize canonical values and aliased values.

    There are several places where names in the Flows service have changed.
    This function helps regulate the deprecation lifecycle of these names.

    *   The canonical name cannot be combined with one of its aliases.
        A canonical value that evaluates to True, and any alias value that is not None,
        will be considered a violation of this requirement.
    *   Only one alias MAY have a value other than None.

    :raises ValueError:
        If one of the validation rules is broken.

    :raises DeprecationWarning:
        If an alias is used instead of the canonical name.

        The DeprecationWarning is instantiated with arguments in this order:

        *   A deprecation message.
        *   The name of the alias that was used.
        *   The value of the alias.

        This design allows the CLI code to send the warning to STDERR
        and allows the API code to issue a true Python warning
        that can be managed by the calling application as desired.

    """

    canonical_name, canonical_value = canonical_item
    arguments = {k: v for k, v in aliases if v is not None}
    if canonical_value and arguments:
        raise ValueError(f"{canonical_name} cannot be combined with an alias.")
    if len(arguments) > 1:
        # Construct a readable, comma-separated list of argument names.
        alias_name_list = list(arguments)
        alias_names = ", ".join(alias_name_list[:-1])
        if len(arguments) >= 3:
            alias_names += ","  # Add an Oxford comma.
        alias_names = " and ".join([alias_names, alias_name_list[-1]])
        message = f"{alias_names} cannot be used together. Please use {canonical_name}."
        raise ValueError(message)
    if arguments:
        alias_name, alias_value = arguments.popitem()
        raise DeprecationWarning(
            f"{alias_name} is deprecated. Please use {canonical_name}.",
            alias_name,
            alias_value,
        )

    return canonical_value
