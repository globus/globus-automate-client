About ``changelog.d/``
======================

The ``changelog.d/`` directory contains changelog fragments.


Creating fragments
------------------

Changelog fragments are created during development to document and categorize changes.
The files are created and automatically named using the ``scriv create`` command.

To correctly include your GitHub username in the fragment filename,
run this command to modify your global git configuration:

..  code-block:: shell

    git config --global github.user GITHUB_USERNAME


Collecting fragments
--------------------

The fragments are collected and collated during the release process using this command:

..  code-block:: shell

    scriv collect
