from globus_automate_client import create_flows_client
from globus_automate_client.token_management import CLIENT_ID

# Create an authenticated FlowsClient that can run operations against the Flows
# service
fc = create_flows_client(CLIENT_ID)

# Get a listing of runnable, deployed flows
available_flows = fc.list_flows(["runnable_by"])
for flow in available_flows.data["flows"]:
    print(flow)
