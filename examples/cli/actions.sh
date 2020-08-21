# Use the hello world action to echo a string back to you
globus-automate action run \
    --action-url https://actions.automate.globus.org/hello_world \
    --body '{"echo_string": "from CLI"}'

# Directly invoke the Identifiers Action to create an Identifier
globus-automate action run \
    --action-url https://actions.automate.globus.org/identifiers/create \
    --body action_bodies/identifier.json

# Check an executed Action's status via its ACTION_ID
globus-automate action status \
    --action-url https://actions.automate.globus.org/hello_world \
    <ACTION_ID>
