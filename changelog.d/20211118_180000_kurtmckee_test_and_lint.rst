Bugfixes
--------

-   Fix a bug that could allow the Flows authorizer to be lost if an exception was raised.
    (Authorizer swaps are now handled using a context manager.)

Other
-----

-   Add code linting, documentation build testing, and a bunch of unit tests.
-   Add GitHub Actions to run on push and pull requests.
-   Add a pre-commit configuration file to increase overall code quality.
