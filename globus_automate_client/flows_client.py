import uuid
from typing import Any, Dict, Optional, List
from globus_sdk import (
    ClientCredentialsAuthorizer,
    AccessTokenAuthorizer,
    RefreshTokenAuthorizer,
    GlobusHTTPResponse,
)
from globus_sdk.base import BaseClient

from .token_management import get_access_tokens_for_scopes, get_access_token_for_scope

_prod_flows_base_url = "https://flows.automate.globus.org"

MANAGE_FLOWS_SCOPE = (
    "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/manage_flows"
)
VIEW_FLOWS_SCOPE = (
    "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/view_flows"
)
RUN_FLOWS_SCOPE = (
    "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run"
)
RUN_STATUS_SCOPE = (
    "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run_status"
)
NULL_SCOPE = "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/null"

ALL_FLOW_SCOPES = (
    MANAGE_FLOWS_SCOPE,
    VIEW_FLOWS_SCOPE,
    RUN_FLOWS_SCOPE,
    RUN_STATUS_SCOPE,
)


class FlowsClient(BaseClient):
    allowed_authorizer_types = (
        AccessTokenAuthorizer,
        RefreshTokenAuthorizer,
        ClientCredentialsAuthorizer,
    )

    def __init__(self, token_map, client_id, *args, **kwargs) -> None:
        self.token_map = token_map
        self.client_id = client_id
        super().__init__(*args, **kwargs)

    def deploy_flow(
        self,
        flow_definition: Dict[str, Any],
        visible_to: List[str] = [],
        runnable_by: List[str] = [],
        **kwargs,
    ) -> GlobusHTTPResponse:
        self.authorizer = AccessTokenAuthorizer(self.token_map.get(MANAGE_FLOWS_SCOPE))
        req_body = {"definition": flow_definition}
        if visible_to:
            req_body["visible_to"] = visible_to
        if runnable_by:
            req_body["runnable_by"] = runnable_by
        return self.post("/", req_body, **kwargs)

    def get_flow(self, flow_id: str, **kwargs) -> GlobusHTTPResponse:
        self.authorizer = AccessTokenAuthorizer(self.token_map.get(MANAGE_FLOWS_SCOPE))
        path = self.qjoin_path(flow_id)
        return self.get(path, **kwargs)

    def list_flows(self, **kwargs) -> GlobusHTTPResponse:
        self.authorizer = AccessTokenAuthorizer(self.token_map.get(MANAGE_FLOWS_SCOPE))
        return self.get("/mine", **kwargs)

    def run_flow(
        self, flow_id: str, flow_scope: str, flow_input: Optional[str], **kwargs
    ) -> GlobusHTTPResponse:
        if flow_scope is None:
            flow_defn = self.get_flow(flow_id)
            flow_scope = flow_defn.data["scope_string"]
        flow_token = get_access_token_for_scope(flow_scope, self.client_id)
        self.authorizer = AccessTokenAuthorizer(flow_token)
        req_body = {"body": flow_input}
        return self.post(f"/{flow_id}/run", req_body, **kwargs)

    def _scope_for_flow(self, flow_id: str) -> Optional[str]:
        flow_defn = self.get_flow(flow_id)
        flow_scope = flow_defn.get("globus_auth_scope", flow_defn.get(["scope_string"]))
        return flow_scope

    def flow_action_status(
        self, flow_id: str, flow_scope: str, flow_action_id: str, **kwargs
    ) -> GlobusHTTPResponse:
        if flow_scope is None:
            flow_defn = self.get_flow(flow_id)
            flow_scope = flow_defn.data["scope_string"]
        flow_token = get_access_token_for_scope(flow_scope, self.client_id)
        self.authorizer = AccessTokenAuthorizer(flow_token)
        return self.get(f"/{flow_id}/{flow_action_id}/status", **kwargs)

    def flow_action_log(
        self,
        flow_id: str,
        flow_scope: str,
        flow_action_id: str,
        limit: int = 10,
        reverse_order: bool = False,
        **kwargs,
    ) -> GlobusHTTPResponse:
        if flow_scope is None:
            flow_defn = self.get_flow(flow_id)
            flow_scope = flow_defn.data["scope_string"]
        flow_token = get_access_token_for_scope(flow_scope, self.client_id)
        self.authorizer = AccessTokenAuthorizer(flow_token)
        params = {"reverse_order": reverse_order, "limit": limit}
        return self.get(f"/{flow_id}/{flow_action_id}/log", params=params, **kwargs)


def create_flows_client(
    client_id: str, base_url: str = "https://flows.automate.globus.org"
) -> FlowsClient:
    access_tokens = get_access_tokens_for_scopes(ALL_FLOW_SCOPES, client_id)
    temp_access_token = access_tokens.get(MANAGE_FLOWS_SCOPE)
    authorizer = AccessTokenAuthorizer(temp_access_token)
    return FlowsClient(
        access_tokens,
        client_id,
        "flows_client",
        base_url=base_url,
        app_name="flows_client",
        authorizer=authorizer,
    )
