Bugfixes
--------

-   `[sc-19291] <https://app.shortcut.com/globus/story/19291>`_
    Prevent passive flow permission updates.

    Previously, permissions were erased during updates if no permissions were specified.
    Now, permissions will only be erased if an empty string is passed. For example:

    ..  code-block:: text

        # Erase all viewer permissions.
        globus-automate flow update $UUID --flow-viewer=""
