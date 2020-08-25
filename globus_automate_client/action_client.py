import uuid
from typing import Any, Dict, Iterable, Mapping, Optional

import requests
from globus_sdk import (
    AccessTokenAuthorizer,
    ClientCredentialsAuthorizer,
    GlobusHTTPResponse,
    RefreshTokenAuthorizer,
)
from globus_sdk.base import BaseClient

from globus_automate_client.token_management import get_authorizer_for_scope


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
        headers: Dict = {}
        if self.authorizer is not None:
            self.authorizer.set_authorization_header(headers)
        resp = requests.get(self.base_url, headers=headers)
        return self.default_response_class(resp, client=self)

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


def create_action_client(
    action_url: str, action_scope: Optional[str] = None
) -> ActionClient:
    """
    A helper function to handle creating a properly authenticated ``ActionClient``
    which can operate against *Globus Action Provider Interface* compliant Action
    Providers.

    Given the ``action_url`` for a specific ActionProvider, this function will
    attempt to create a valid ``ActionClient`` for interacting with that
    ActionProvider. If the ``action_scope`` is not provided, this function will
    attempt to discover the ``action_scope`` by querying the target Action
    Provider's introspection endpoint. If the Action Provider is not configured
    to allow public, unauthenticated access to its introspection endpoint, the
    ``action_scope`` will be non-discoverable and authentication will fail.

    With the ``action_scope`` available, the function will search for a valid
    token using the fair_research_login library. In the event that tokens for
    the scope cannot be loaded, an interactive login will be triggered. Once
    tokens have been loaded, an Authorizer is created and used to instantiate
    the ``ActionClient`` which can be used for operations against that Action
    Provider.

    :param action_url: The URL address at which the target Action Provider
        exists
    :param action_scope: The target Action Provider's Globus Auth Scope used
        for authenticating access to it
    """
    if action_scope is None:
        # We don't know the scope which makes it impossible to get a token,
        # but create a client anyways in case this action provider is publicly
        # visible without authentication.
        temp_client = ActionClient(
            "temp_client", base_url=action_url, app_name="tmp_client",
        )
        action_scope = temp_client.action_scope

    if action_scope:
        authorizer = get_authorizer_for_scope(action_scope)
    else:
        # Any attempts to use this authorizer will fail but there's nothing we
        # can do without a scope.
        authorizer = None

    return ActionClient(
        "action_client",
        base_url=action_url,
        app_name="action_client",
        authorizer=authorizer,
    )
