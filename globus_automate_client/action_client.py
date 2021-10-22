import uuid
from typing import Any, Dict, Iterable, Mapping, Optional, Type, TypeVar, Union

from globus_sdk import (
    AccessTokenAuthorizer,
    ClientCredentialsAuthorizer,
    GlobusHTTPResponse,
    RefreshTokenAuthorizer,
)
from globus_sdk import BaseClient

from .helpers import merge_lists

_ActionClient = TypeVar("_ActionClient", bound="ActionClient")


class ActionClient(BaseClient):
    allowed_authorizer_types = (
        AccessTokenAuthorizer,
        RefreshTokenAuthorizer,
        ClientCredentialsAuthorizer,
    )

    AllowedAuthorizersType = Union[
        AccessTokenAuthorizer, RefreshTokenAuthorizer, ClientCredentialsAuthorizer
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def action_scope(self) -> str:
        """
        This property can be used to determine an ``ActionClient``'s
        ``action_scope``. Internally, this property will introspect the Action
        Provider at the URL for which the ``ActionClient`` was created. If the
        ``Action Provider`` is not public, a valid ``Globus Authorizer`` will
        have to have been provided on initialization to the ``ActionClient``.
        Otherwise, this call will fail.
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
        label: Optional[str] = None,
        force_path: Optional[str] = None,
        **kwargs
    ) -> GlobusHTTPResponse:
        """
        Invoke the Action Provider to execute an Action with the given
        parameters.

        :param body: The Action Provider specific input required to execute an
            Action payload
        :param request_id: An optional identifier that serves to de-duplicate
            requests to the Action Provider
        :param manage_by: A series of Globus identities which may alter
            this Action's execution. The principal value is the user's or
            group's UUID prefixed with either 'urn:globus:groups:id:' or
            'urn:globus:auth:identity:'
        :param monitor_by: A series of Globus identities which may
            view the state of this Action. The principal value is the user's or
            group's UUID prefixed with either 'urn:globus:groups:id:' or
            'urn:globus:auth:identity:'
        :param force_path: A URL to use for running this action, ignoring any
            previous configuration
        :param label: Set a label for the Action that is run.
        :param run_monitors: May be used as an alias for ``monitor_by``
        :param run_managers: May be used as an alias for ``manage_by``
        """
        if request_id is None:
            request_id = str(uuid.uuid4())

        path = self.qjoin_path("run")
        if force_path:
            path = force_path
        body = {
            "request_id": str(request_id),
            "body": body,
            "monitor_by": merge_lists(monitor_by, kwargs, "run_monitors"),
            "manage_by": merge_lists(manage_by, kwargs, "run_managers"),
            "label": label,
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

    def resume(self, action_id: str) -> GlobusHTTPResponse:
        """
        Resume an INACTIVE action. Corrective action must have been taken prior to invoking
        this method, including the possibility of consenting to additional permissions
        and using tokens issued by those consents when creating this client. These
        consents would commonly be required when an Action is INACTIVE and shows the code
        ConsentRequired.

        :param action_id: An identifier that uniquely identifies an Action
            executed on this Action Provider.

        """
        path = self.qjoin_path(action_id, "resume")
        return self.post(path)

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

    def log(
        self,
        action_id: str,
        limit: int = 10,
        reverse_order: bool = False,
        marker: Optional[str] = None,
        per_page: Optional[int] = None,
    ) -> GlobusHTTPResponse:
        """
        Retrieve an Action's execution log history. Not all ``Action Providers``
        support this operation.

        :param action_id: An identifier that uniquely identifies an Action
            executed on this Action Provider.
        :param limit: A integer specifying how many log records to return
        :param reverse_order: Display the Action states in reverse-
            chronological order
        :param marker: A pagination_token indicating the page of results to
            return and how many entries to return. Not all ActionProviders will
            support this parameter.
        :param per_page: The number of results to return per page. If
            supplied a pagination_token, this parameter has no effect. Not all
            ActionProviders will support this parameter.
        """

        # *reverse_order* MUST BE None to prevent reversing the sort order.
        # Any other value, including False, will reverse the sort order.
        params: Dict[str, Union[int, str]] = {
            "reverse_order": reverse_order or None,
            "limit": limit,
        }
        if marker is not None:
            params["pagination_token"] = marker
        if per_page is not None and marker is None:
            params["per_page"] = per_page
        path = self.qjoin_path(action_id, "log")
        return self.get(path, params=params)

    @classmethod
    def new_client(
        cls: Type[_ActionClient],
        action_url: str,
        authorizer: AllowedAuthorizersType,
        http_timeout: int = 10,
    ) -> _ActionClient:
        """
        Classmethod to simplify creating an ActionClient. Use this method when
        attemping to create an ActionClient with pre-existing credentials or
        authorizers.

        :param action_url: The url at which the target Action Provider is
            located.
        :param authorizer: The authorizer to use for validating requests to the
            Action Provider.
        :param http_timeout: The amount of time to wait for connections to
            the Action Provider to be made.

        **Examples**
            >>> authorizer = ...
            >>> action_url = "https://actions.globus.org/hello_world"
            >>> ac = ActionClient.new_client(action_url, authorizer)
            >>> print(ac.run({"echo_string": "Hello from SDK"}))
        """
        return cls(
            "action_client",
            app_name="Globus Automate SDK - ActionClient",
            base_url=action_url,
            authorizer=authorizer,
            http_timeout=http_timeout,
        )
