# Visualize or lint a Flow definition before deploying
globus-automate flow lint --format json \
    --definition examples/flows/hello-world/definition.json

# Deploy a Flow while defining its input schema
globus-automate flow deploy --title "Hello World Flow" \
    --definition examples/flows/hello-world/definition.json \
    --input-schema examples/flows/hello-world/input-schema.json

# Display a deployed Flow using its FLOW_ID generated during Deploy
globus-automate flow display <FLOW_ID>

# Run a Flow using its FLOW_ID generated during Deploy
globus-automate flow run --flow-input examples/flows/hello-world/input.json \
    <FLOW_ID>

# See the Actions for a given Flow
globus-automate flow action-list --flow_id <FLOW_ID>

# Check an Action's status for an Action triggered by a Flow
globus-automate flow action-status --flow_id <FLOW_ID> <ACTION_ID>
