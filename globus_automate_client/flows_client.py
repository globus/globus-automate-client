import uuid
from typing import Any, Dict, List, Mapping, Optional

from globus_sdk import (
    AccessTokenAuthorizer,
    ClientCredentialsAuthorizer,
    GlobusHTTPResponse,
    RefreshTokenAuthorizer,
)
from globus_sdk.base import BaseClient

from .token_management import get_access_token_for_scope, get_access_tokens_for_scopes

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
        flow_definition: Mapping[str, Any],
        title: str,
        subtitle: Optional[str] = None,
        description: Optional[str] = None,
        keywords: List[str] = [],
        visible_to: List[str] = [],
        runnable_by: List[str] = [],
        administered_by: List[str] = [],
        **kwargs,
    ) -> GlobusHTTPResponse:
        self.authorizer = AccessTokenAuthorizer(self.token_map.get(MANAGE_FLOWS_SCOPE))
        temp_body: Dict[str, Any] = {"definition": flow_definition, "title": title}
        temp_body["subtitle"] = subtitle
        temp_body["description"] = description
        temp_body["keywords"] = keywords
        temp_body["visible_to"] = visible_to
        temp_body["runnable_by"] = runnable_by
        temp_body["administered_by"] = administered_by
        # Remove None / empty list items from the temp_body
        req_body = {k: v for k, v in temp_body.items() if v}
        return self.post("/flows", req_body, **kwargs)

    def get_flow(self, flow_id: str, **kwargs) -> GlobusHTTPResponse:
        self.authorizer = AccessTokenAuthorizer(self.token_map.get(MANAGE_FLOWS_SCOPE))
        path = self.qjoin_path(flow_id)
        return self.get(path, **kwargs)

    def list_flows(
        self, roles: Optional[List[str]] = None, **kwargs
    ) -> GlobusHTTPResponse:
        self.authorizer = AccessTokenAuthorizer(self.token_map.get(MANAGE_FLOWS_SCOPE))
        params = {}
        if roles is not None and len(roles) > 0:
            params.update(dict(roles=",".join(roles)))
        return self.get("/flows", params=params, **kwargs)

    def run_flow(
        self, flow_id: str, flow_scope: str, flow_input: Mapping, **kwargs
    ) -> GlobusHTTPResponse:
        if flow_scope is None:
            flow_scope = self._scope_for_flow(flow_id)
        flow_token = get_access_token_for_scope(flow_scope, self.client_id)
        self.authorizer = AccessTokenAuthorizer(flow_token)
        req_body = {"body": flow_input}
        return self.post(f"/flows/{flow_id}/run", req_body, **kwargs)

    def _scope_for_flow(self, flow_id: str) -> Optional[str]:
        flow_defn = self.get_flow(flow_id)
        flow_scope = flow_defn.get("globus_auth_scope", flow_defn.get("scope_string"))
        return flow_scope

    def flow_action_status(
        self, flow_id: str, flow_scope: str, flow_action_id: str, **kwargs
    ) -> GlobusHTTPResponse:
        if flow_scope is None:
            flow_scope = self._scope_for_flow(flow_id)
        flow_token = get_access_token_for_scope(flow_scope, self.client_id)
        self.authorizer = AccessTokenAuthorizer(flow_token)
        return self.get(f"/flows/{flow_id}/{flow_action_id}/status", **kwargs)

    def list_flow_actions(
        self,
        flow_id: str,
        flow_scope: Optional[str],
        statuses: Optional[List[str]],
        roles: Optional[List[str]] = None,
        **kwargs,
    ) -> GlobusHTTPResponse:
        if flow_scope is None:
            flow_scope = self._scope_for_flow(flow_id)
        flow_token = get_access_token_for_scope(flow_scope, self.client_id)
        self.authorizer = AccessTokenAuthorizer(flow_token)
        params = {}
        if statuses is not None and len(statuses) > 0:
            params.update(dict(status=",".join(statuses)))
        if roles is not None and len(roles) > 0:
            params.update(dict(roles=",".join(roles)))
        return self.get(f"/flows/{flow_id}/actions", params=params, **kwargs)

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
            flow_scope = self._scope_for_flow(flow_id)
        flow_token = get_access_token_for_scope(flow_scope, self.client_id)
        self.authorizer = AccessTokenAuthorizer(flow_token)
        params = {"reverse_order": reverse_order, "limit": limit}
        return self.get(
            f"/flows/{flow_id}/{flow_action_id}/log", params=params, **kwargs
        )

    def delete_flow(self, flow_id: str, flow_scope: Optional[str], **kwargs):
        if flow_scope is None:
            flow_scope = self._scope_for_flow(flow_id)
        return self.delete(f"/flows/{flow_id}", **kwargs)


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
