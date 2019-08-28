import uuid
from typing import Any, Dict, Optional

import requests
from globus_sdk import (
    AccessTokenAuthorizer,
    ClientCredentialsAuthorizer,
    GlobusHTTPResponse,
    RefreshTokenAuthorizer,
)
from globus_sdk.base import BaseClient


class ActionClient(BaseClient):
    allowed_authorizer_types = (
        AccessTokenAuthorizer,
        RefreshTokenAuthorizer,
        ClientCredentialsAuthorizer,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def introspect(self, **kwargs) -> GlobusHTTPResponse:
        headers: Dict = {}
        if self.authorizer is not None:
            self.authorizer.set_authorization_header(headers)
        resp = requests.get(self.base_url, headers=headers)
        return self.default_response_class(resp, client=self)

    def run(
        self, body: Dict[str, Any], request_id: Optional[str] = None
    ) -> GlobusHTTPResponse:
        if request_id is None:
            request_id = str(uuid.uuid4())
        path = self.qjoin_path("run")
        body = {"request_id": str(request_id), "body": body}
        return self.post(path, body)

    def status(self, action_id) -> GlobusHTTPResponse:
        path = self.qjoin_path(action_id, "status")
        return self.get(path)

    def cancel(self, action_id) -> GlobusHTTPResponse:
        path = self.qjoin_path(action_id, "cancel")
        return self.post(path)

    def release(self, action_id) -> GlobusHTTPResponse:
        path = self.qjoin_path(action_id, "release")
        return self.post(path)


def create_action_client(action_url: str, access_token: str) -> ActionClient:
    authorizer = AccessTokenAuthorizer(access_token)
    return ActionClient(
        "action_client",
        base_url=action_url,
        app_name="action_client",
        authorizer=authorizer,
    )
