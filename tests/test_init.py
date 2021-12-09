import inspect

import globus_automate_client


def test_all_exports():
    """Validate that all imported names are listed in __all__."""

    imported = set(
        name
        for name in dir(globus_automate_client)
        if (
            not name.startswith("__")
            and not inspect.ismodule(getattr(globus_automate_client, name))
        )
    )
    exported = set(globus_automate_client.__all__)
    assert imported == exported, "imported and exported names do not match"
