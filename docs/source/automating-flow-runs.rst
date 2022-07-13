Running a flow automatically
****************************

It is frequently desirable to run a flow when new data becomes available.
This document provides examples for how to accomplish this
using `watchdog`_ to monitor for filesystem events
and using the Globus Automate CLI to run already-defined flows.


Shell scripting
===============

`watchdog`_ provides a CLI tool named ``watchmedo``.
If you're comfortable with shell scripting
then you can use the following command to run a script named ``runner.sh``.


..  literalinclude:: code_snippets/watchmedo.sh
    :caption: ``watchmedo.sh`` [:download:`download <code_snippets/watchmedo.sh>`]
    :language: shell


The ``watchmedo`` command currently has no way to filter filesystem events.
On Linux, ``runner.sh`` will be run when:

*   a file is created (but has not had data written yet)
*   data is written to the file (but the file has not been closed yet)
*   the file is closed

This will likely result in your flow running far more often than expected.
To avoid this, ``runner.sh`` must filter the incoming filesystem events.
Here is an example script that will run a flow with custom input
when the filesystem event type is ``"closed"``:


..  literalinclude:: code_snippets/runner.sh
    :caption: ``runner.sh`` [:download:`download <code_snippets/runner.sh>`]
    :language: shell

..  note::

    Filesystem events are less granular on Windows platforms.
    Notably, there is no ``"closed"`` event type to signal all data have been written to a file.
    There is only a ``"modified"`` event type, which may fire multiple times
    if large files are written and flushed to disk in multiple chunks.

    Users on Windows may want to use the Python script below.


Python scripting
================

If you know that files will be created or modified in large batches,
you may need to write a script to monitor for filesystem events
and wait some amount of time for filesystem events to taper off.
One way to do this is using the `watchdog`_ package.

The script below will monitor for filesystem events of all types.
It will only run a flow 60 seconds after the most recent filesystem event is encountered.


..  literalinclude:: code_snippets/runner.py
    :caption: ``runner.py`` [:download:`download <code_snippets/runner.py>`]
    :language: python


..  Links used in this document
..  ===========================
..
..  _watchdog: https://github.com/gorakhargosh/watchdog/
