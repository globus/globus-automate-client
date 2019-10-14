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

_prod_queues_base_url = "https://queues.api.globus.org/v1"

QUEUES_ADMIN_SCOPE = (
    "https://auth.globus.org/scopes/3170bf0b-6789-4285-9aba-8b7875be7cbc/admin"
)
QUEUES_SEND_SCOPE = (
    "https://auth.globus.org/scopes/3170bf0b-6789-4285-9aba-8b7875be7cbc/send"
)
QUEUES_RECEIVE_SCOPE = (
    "https://auth.globus.org/scopes/3170bf0b-6789-4285-9aba-8b7875be7cbc/receive"
)

ALL_QUEUES_SCOPES = (QUEUES_ADMIN_SCOPE, QUEUES_SEND_SCOPE, QUEUES_RECEIVE_SCOPE)


class QueuesClient(BaseClient):
    allowed_authorizer_types = (
        AccessTokenAuthorizer,
        RefreshTokenAuthorizer,
        ClientCredentialsAuthorizer,
    )

    def __init__(self, token_map, client_id, *args, **kwargs) -> None:
        self.token_map = token_map
        self.client_id = client_id
        super().__init__(*args, **kwargs)

    def create_queue(
        self,
        label: str,
        admins: List[str],
        senders: List[str],
        receivers: List[str],
        delivery_timeout: int = 86400,
        **kwargs,
    ) -> GlobusHTTPResponse:
        self.authorizer = AccessTokenAuthorizer(self.token_map.get(QUEUES_ADMIN_SCOPE))
        body = {
            "data": {
                "label": label,
                "admins": admins,
                "senders": senders,
                "receivers": receivers,
                "delivery_timeout": delivery_timeout,
            }
        }
        return self.post("/queues", body, **kwargs)

    def get_queue(self, queue_id: str) -> GlobusHTTPResponse:
        return self.get(f"/queues/{queue_id}")

    def list_queues(
        self, roles: Optional[List[str]] = None, **kwargs
    ) -> GlobusHTTPResponse:
        self.authorizer = AccessTokenAuthorizer(self.token_map.get(QUEUES_ADMIN_SCOPE))
        params = {}
        if roles is not None and len(roles) > 0:
            params.update(dict(roles=",".join(roles)))
        return self.get("/queues", params=params, **kwargs)

    def update_queue(
        self,
        queue_id: str,
        label: Optional[str] = None,
        admins: Optional[List[str]] = None,
        senders: Optional[List[str]] = None,
        receivers: Optional[List[str]] = None,
        delivery_timeout: Optional[int] = None,
        **kwargs,
    ) -> Optional[GlobusHTTPResponse]:
        body = dict(
            label=label,
            admins=admins,
            senders=senders,
            receivers=receivers,
            delivery_timeout=delivery_timeout,
        )
        # Remove the missing values from the update operation
        body = {k: v for k, v in body.items() if v is not None}
        if body:
            return self.put(f"/queues/{queue_id}", {"data": body}, **kwargs)
        else:
            return None

    def delete_queue(self, queue_id: str) -> str:
        try:
            delete_op_resp = self.delete(f"/queues/{queue_id}")
            return str(delete_op_resp)
        except KeyError:
            # Client lib seems to choke if there's no content-type on the response which
            # queues doesn't seem to set on delete. Catch that as best we can as a
            # KeyError then return a somewhat useful string
            return f"Queue {queue_id} deleted."

    def send_message(
        self, queue_id: str, message_body: str, deduplication_id: Optional[str] = None
    ) -> GlobusHTTPResponse:
        self.authorizer = AccessTokenAuthorizer(self.token_map.get(QUEUES_SEND_SCOPE))
        if deduplication_id is None:
            deduplication_id = str(uuid.uuid4())
        body = {
            "data": [
                {"deduplication_id": deduplication_id, "message_body": message_body}
            ]
        }
        return self.post(f"/queues/{queue_id}/messages", body)

    def receieve_messages(
        self,
        queue_id: str,
        max_messages: int = 1,
        receive_request_attempt_id: Optional[str] = None,
    ) -> GlobusHTTPResponse:
        params = {"max_messages": max_messages}
        if receive_request_attempt_id is not None:
            params["receive_request_attempt_id"] = receive_request_attempt_id
        return self.get(f"/queues/{queue_id}/messages", params=params)


def create_queues_client(
    client_id: str, base_url: str = "https://queues.api.globus.org/v1"
) -> QueuesClient:
    access_tokens = get_access_tokens_for_scopes(ALL_QUEUES_SCOPES, client_id)
    temp_access_token = access_tokens.get(QUEUES_ADMIN_SCOPE)
    authorizer = AccessTokenAuthorizer(temp_access_token)
    return QueuesClient(
        access_tokens,
        client_id,
        "queues_client",
        base_url=base_url,
        app_name="queues_client",
        authorizer=authorizer,
    )
