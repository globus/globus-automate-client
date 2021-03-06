import os

from globus_sdk import AccessTokenAuthorizer

from globus_automate_client import FlowsClient
from globus_automate_client.flows_client import (
    MANAGE_FLOWS_SCOPE,
    AllowedAuthorizersType,
)
from globus_automate_client.token_management import CLIENT_ID


def authorizer_retriever(
    flow_url: str, flow_scope: str, client_id: str
) -> AllowedAuthorizersType:
    """
    This callback will be called when attempting to interact with a
    specific Flow. The callback will receive the Flow url, Flow scope, and
    client_id and can choose to use some, all or none of the kwargs. This is
    expected to return an Authorizer which can be used to make authenticated
    calls to the Flow.

    The method used to acquire valid credentials is up to the user. Here, we
    naively create an Authorizer using the same token everytime.
    """
    flow_token = os.environ.get("MY_ACCESS_TOKEN")
    return AccessTokenAuthorizer(flow_token)


# Create an AccessTokenAuthorizer using a token that has consents to the
# MANAGE_FLOWS_SCOPE. This lets the FlowsClient perform operations against the
# Flow's service i.e. create flow, update a flow, delete a flow
flows_service_token = os.environ.get("ANOTHER_OR_THE_SAME_ACCESS_TOKEN")
flows_service_authorizer = AccessTokenAuthorizer(flows_service_token)

fc = FlowsClient.new_client(
    client_id=CLIENT_ID,
    authorizer=flows_service_authorizer,
    authorizer_callback=authorizer_retriever,
)

my_flows = fc.list_flows()
print(my_flows)

running_flow = fc.run_flow(
    "1e6b4406-ee3d-4bc5-9198-74128e108111", None, {"echo_string": "hey"}
)
print(running_flow)

# It's possible to create an Authorizer and pass it as a kwarg to the flow
# operation. This usage will not attempt to make use of the authorizer_callback:
running_flow_2 = fc.run_flow(
    "1e6b4406-ee3d-4bc5-9198-74128e108111",
    None,
    {"echo_string": "hey"},
    authorizer=AccessTokenAuthorizer(...),
)
print(running_flow_2)
