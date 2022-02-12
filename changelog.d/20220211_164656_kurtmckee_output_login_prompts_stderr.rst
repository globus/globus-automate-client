Bugfixes
--------

-   Output login prompts to STDERR.
    This protects serialized output to STDOUT so it can be piped to tools like `jq`.
