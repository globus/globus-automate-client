# Count to 10 using the Flows service

The flow defined below is roughly equivalent to a `for` loop:
It initializes a `counter` variable in a `state_manager` and
increments `counter` until its value equals 10.

The `counter` variable is stored in a `state_manager` variable
so a ResultPath can be specified in the "Increment" state.
