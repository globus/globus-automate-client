import uuid
from typing import Any, Iterable, Mapping, Optional

from globus_sdk import (
    AccessTokenAuthorizer,
    ClientCredentialsAuthorizer,
    GlobusHTTPResponse,
    RefreshTokenAuthorizer,
)
from globus_sdk.authorizers.base import GlobusAuthorizer
from globus_sdk.base import BaseClient


class ActionClient(BaseClient):
    allowed_authorizer_types = (
        AccessTokenAuthorizer,
        RefreshTokenAuthorizer,
        ClientCredentialsAuthorizer,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def action_scope(self) -> str:
        """
        This property can be used to determine an ``ActionClient``'s
        ``action_scope``. Internally, this property will introspect the Action
        Provider at the URL for which the ``ActionClient`` was created.
        """
        if not hasattr(self, "_action_scope"):
            resp = self.introspect()
            if resp.data is None:
                self._action_scope = ""
            else:
                self._action_scope = resp.data.get("globus_auth_scope", "")
        return self._action_scope

    def introspect(self, **kwargs) -> GlobusHTTPResponse:
        """
        Introspect the details of an Action Provider to discover information
        such as its expected ``action_scope``, its ``input_schema``, and who to
        contact when there's trouble.
        """
        return self.get("")

    def run(
        self,
        body: Mapping[str, Any],
        request_id: Optional[str] = None,
        manage_by: Optional[Iterable[str]] = None,
        monitor_by: Optional[Iterable[str]] = None,
    ) -> GlobusHTTPResponse:
        """
        Invoke the Action Provider to execute an Action with the given
        parameters.

        :param body: The Action Provider specific input required to execute an
            Action payload
        :param request_id: An optional identifier that serves to de-deplicate
            requests to the Action Provider
        :param manage_by: A series of Globus identities which may alter
            this Action's execution
        :param monitor_by: A series of Globus identities which may
            view the state of this Action
        """
        if request_id is None:
            request_id = str(uuid.uuid4())
        if manage_by is not None:
            manage_by = list(set(manage_by))
        if monitor_by is not None:
            monitor_by = list(set(monitor_by))

        path = self.qjoin_path("run")
        body = {
            "request_id": str(request_id),
            "body": body,
            "monitor_by": monitor_by,
            "manage_by": manage_by,
        }
        # Remove None items from the temp_body
        body = {k: v for k, v in body.items() if v is not None}
        return self.post(path, body)

    def status(self, action_id: str) -> GlobusHTTPResponse:
        """
        Query the Action Provider for the status of executed Action

        :param action_id: An identifier that uniquely identifies an Action
            executed on this Action Provider.
        """
        path = self.qjoin_path(action_id, "status")
        return self.get(path)

    def cancel(self, action_id: str) -> GlobusHTTPResponse:
        """
        Cancel a currently executing Action on an Action Provider

        :param action_id: An identifier that uniquely identifies an Action
            executed on this Action Provider.
        """
        path = self.qjoin_path(action_id, "cancel")
        return self.post(path)

    def release(self, action_id: str) -> GlobusHTTPResponse:
        """
        Remove the history of an Action's execution from an Action Provider

        :param action_id: An identifier that uniquely identifies an Action
            executed on this Action Provider.
        """
        path = self.qjoin_path(action_id, "release")
        return self.post(path)

    @classmethod
    def new_client(cls, action_url: str, authorizer: GlobusAuthorizer):
        return cls(
            "action_client",
            app_name="Globus Automate SDK - ActionClient",
            base_url=action_url,
            authorizer=authorizer,
        )
