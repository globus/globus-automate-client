# Process an unknown quantity of items in batches.

The number of items in each batch is configurable at runtime.

The flow defined below gets a list of files from the
Globus Tutorial Endpoint 1 and collects the list of files
into batches that can be processed in predictable quantities.

The flow accepts a single input argument: `step`.

Note that a `state_manager` variable is used so that a ResultPath
can be specified when evaluating the `i` and `batches` state variables.

## Example

If you create 10 files in your home directory on Tutorial Endpoint 1
named "a.txt" through "j.txt" and run this flow with an input of:

```
{"step": 3}
```

then the files will be batched into groups of 3 similar to this:

```
[
    ["1.txt", "2.txt", "3.txt"],
    ["4.txt", "5.txt", "6.txt"],
    ["7.txt", "8.txt", "9.txt"],
    ["10.txt"]
]
```
