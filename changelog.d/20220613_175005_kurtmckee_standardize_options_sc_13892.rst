Bugfixes
--------

-   `[sc-13892] <https://app.shortcut.com/globus/story/13892>`_
    Standardize flow viewer, starter, and administrator arguments -- and their aliases -- throughout the CLI and API.

    Although this change fixes bugs that prevented documented CLI options from working,
    it also introduces breaking changes:

    *   ``--flow-viewer``, ``--flow-starter``, and ``--flow-administrator`` are the canonical CLI options.
    *   The CLI option aliases will continue to work, but the alias behavior has changed:

        *   If an alias is used, a warning is written to STDERR.
        *   If the canonical option name is combined with one of its aliases,
            an error will be written to STDERR and the Automate client will exit.
            The exit code will be 1.
        *   If more than one of the acceptable aliases is used (like ``--starter`` and ``--runnable-by``),
            an error will be written to STDERR and the Automate client will exit.
            The exit code will be 1.

    In addition, there are breaking changes in the API:

    *   ``flow_viewers``, ``flow_starters``, and ``flow_administrators`` are the canonical API argument names.
    *   The API argument aliases will continue to work, but the alias behavior has changed:

        *   If an alias is used, a Python warning will be issued.
            Applications can control the warning behavior using Python's ``warnings`` module.
        *   If the canonical option name is combined with one of its aliases, a ``ValueError`` will be raised.
        *   If more than one of the acceptable aliases is used (like ``starters`` and ``runnable_by``), a ``ValueError`` will be raised.
