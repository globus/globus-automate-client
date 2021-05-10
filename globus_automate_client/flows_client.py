import json
import os
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)

from globus_sdk import (
    AccessTokenAuthorizer,
    ClientCredentialsAuthorizer,
    GlobusHTTPResponse,
    RefreshTokenAuthorizer,
)
from globus_sdk.base import BaseClient
from jsonschema import Draft7Validator

from globus_automate_client import ActionClient

PROD_FLOWS_BASE_URL = "https://flows.globus.org"

_ENVIRONMENT_FLOWS_BASE_URLS = {
    None: PROD_FLOWS_BASE_URL,
    "prod": PROD_FLOWS_BASE_URL,
    "production": PROD_FLOWS_BASE_URL,
    "sandbox": "https://sandbox.flows.automate.globus.org",
    "integration": "https://integration.flows.automate.globus.org",
    "test": "https://test.flows.automate.globus.org",
    "preview": "https://preview.flows.automate.globus.org",
    "staging": "https://staging.flows.automate.globus.org",
}

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

_FlowsClient = TypeVar("_FlowsClient", bound="FlowsClient")
AllowedAuthorizersType = Union[
    AccessTokenAuthorizer, RefreshTokenAuthorizer, ClientCredentialsAuthorizer
]
AuthorizerCallbackType = Callable[..., AllowedAuthorizersType]


class FlowValidationError(Exception):
    def __init__(self, errors: Iterable[str], **kwargs):
        message = "; ".join(errors)
        super().__init__(message)


def _all_vals_for_keys(
    key_name_set: Set[str],
    d: Mapping[str, Any],
    stop_traverse_key_set: Optional[Set[str]] = None,
) -> Set[str]:
    val_set = set()
    for k, v in d.items():
        if k in key_name_set and isinstance(v, str):
            val_set.add(v)
        if stop_traverse_key_set is not None and k in stop_traverse_key_set:
            continue
        if isinstance(v, dict):
            val_set.update(
                _all_vals_for_keys(
                    key_name_set, v, stop_traverse_key_set=stop_traverse_key_set
                )
            )
        elif isinstance(v, list):
            for val in v:
                if k in key_name_set and isinstance(v, str):
                    val_set.add(val)
                elif isinstance(val, dict):
                    val_set.update(
                        _all_vals_for_keys(
                            key_name_set,
                            val,
                            stop_traverse_key_set=stop_traverse_key_set,
                        )
                    )
    return val_set


def validate_flow_definition(flow_definition: Mapping[str, Any]) -> None:
    """Perform local, JSONSchema based validation of a Flow definition. This is validation
    on the basic structure of your Flow definition.such as required fields / properties
    for the various state types and the overall structure of the Flow. This schema based
    validation *does not* do any validation of input values or parameters passed to
    Actions as those Actions define their own schemas and the Flow may generate or
    compute values to these Actions and thus static, schema based validation cannot
    determine if the Action parameter values generated during execution are correct.

    The input is the dictionary containing the flow definition.

    If the flow passes validation, no value is returned. If validation errors are found,
    a FlowValidationError exception will be raised containing a string message describing
    the error(s) encountered.
    """
    schema_path = Path(__file__).parent / "flows_schema.json"
    with schema_path.open() as sf:
        flow_schema = json.load(sf)
    validator = Draft7Validator(flow_schema)
    errors = validator.iter_errors(flow_definition)
    error_msgs = set()
    for error in errors:
        if error.path:
            # Elements of the error path may be integers or other non-string types,
            # but we need strings for use with join()
            error_path_for_message = ".".join([str(x) for x in error.path])
            error_message = (
                f"'{error_path_for_message}' invalid due to {error.message}: "
                f" {error.context}"
            )
        else:
            error_message = f"{error.message}: {error.context}"
        error_msgs.add(error_message)
    if error_msgs:
        raise FlowValidationError(error_msgs)

    # We can be aggressive about indexing these maps as it has already passed schema
    # validation
    state_names = set(flow_definition["States"].keys())
    flow_state_refs = _all_vals_for_keys(
        {"Next", "Default", "StartAt"},
        flow_definition,
        stop_traverse_key_set={"Parameters"},
    )

    unreferenced = state_names - flow_state_refs
    not_present = flow_state_refs - state_names
    if len(unreferenced) > 0:
        error_msgs.add(
            "The following states are defined but not referenced by any "
            f"other states in the flow: {unreferenced}"
        )
    if len(not_present) > 0:
        error_msgs.add(
            "The following states are referenced but are not defined by the"
            f" flow: {not_present}"
        )
    if error_msgs:
        raise FlowValidationError(error_msgs)
    return


def _get_flows_base_url_for_environment():
    environ = os.environ.get("GLOBUS_SDK_ENVIRONMENT")
    if environ not in _ENVIRONMENT_FLOWS_BASE_URLS:
        raise ValueError(f"Unknown value for GLOBUS_SDK_ENVIRONMENT: {environ}")
    return _ENVIRONMENT_FLOWS_BASE_URLS[environ]


class FlowsClient(BaseClient):
    """
    This is a specialized type of the Globus Auth service's ``BaseClient`` used
    to interact with the Globus Flows service. Any keyword arguments given are
    passed through to the ``BaseClient`` constructor.
    """

    allowed_authorizer_types = (
        AccessTokenAuthorizer,
        RefreshTokenAuthorizer,
        ClientCredentialsAuthorizer,
    )

    def __init__(
        self,
        client_id: str,
        get_authorizer_callback: AuthorizerCallbackType,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.flow_management_authorizer: AllowedAuthorizersType = self.authorizer
        self.get_authorizer_callback = get_authorizer_callback

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
        subscription_id: Optional[str] = None,
        input_schema: Optional[Mapping[str, Any]] = None,
        validate_definition: bool = True,
        validate_input_schema: bool = True,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """Deploys a Flow definition to the Flows service, making the Flow
        available for execution on the Globus Automate Flows Service.

        :param flow_definition: A mapping corresponding to a Globus Flows
            definition.

        :param title: A simple, human readable title for the deployed Flow

        :param subtitle: A longer, more verbose title for the deployed Flow

        :param description: A long form explanation of the Flow's purpose or
            usage

        :param keywords: A series of words which may help categorize or make the
            Flow discoverable

        :param visible_to: A series of Globus identities which may discover and
            view the Flow definition

        :param runnable_by: A series of Globus identities which may run an
            instance of this Flow

        :param administered_by: A series of Globus identities which may update
            this Flow's definition

        :param subscription_id: The Globus Subscription which will be used to make this
        flow managed.

        :param input_schema: A mapping representing the JSONSchema used to
            validate input to this Flow. If not supplied, no validation will be
            done on input to this Flow.

        :param validate_definition: Set to ``True`` to validate the provided
            ``flow_definition`` before attempting to deploy the Flow.

        :param validate_input_schema: Set to ``True`` to validate the provided
            ``input_schema`` before attempting to deploy the Flow.

        """
        if validate_definition:
            validate_flow_definition(flow_definition)
        self.authorizer = self.flow_management_authorizer
        temp_body: Dict[str, Any] = {"definition": flow_definition, "title": title}
        temp_body["subtitle"] = subtitle
        temp_body["description"] = description
        temp_body["keywords"] = keywords
        temp_body["visible_to"] = visible_to
        temp_body["runnable_by"] = runnable_by
        temp_body["administered_by"] = administered_by
        temp_body["subscription_id"] = subscription_id
        temp_body["input_schema"] = input_schema
        # Remove None / empty list items from the temp_body
        req_body = {k: v for k, v in temp_body.items() if v}
        return self.post("/flows", req_body, **kwargs)

    def update_flow(
        self,
        flow_id: str,
        flow_definition: Optional[Mapping[str, Any]] = None,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        description: Optional[str] = None,
        keywords: List[str] = [],
        visible_to: List[str] = [],
        runnable_by: List[str] = [],
        administered_by: List[str] = [],
        subscription_id: Optional[str] = None,
        input_schema: Optional[Mapping[str, Any]] = None,
        validate_definition: bool = True,
        validate_input_schema: bool = True,
        **kwargs,
    ) -> Optional[GlobusHTTPResponse]:
        """
        Updates a deployed Flow's definition or metadata. This method will
        preserve the existing Flow's values for fields which are not
        submitted as part of the update.

        :param flow_id: The UUID for the Flow that will be updated

        :param flow_definition: A mapping corresponding to a Globus Flows
            definition

        :param title: A simple, human readable title for the deployed Flow

        :param subtitle: A longer, more verbose title for the deployed Flow

        :param description: A long form explanation of the Flow's purpose or
            usage

        :param keywords: A series of words which may help categorize or make the
            Flow discoverable

        :param visible_to: A series of Globus identities which may discover and
            view the Flow definition

        :param runnable_by: A series of Globus identities which may run an
            instance of this Flow

        :param administered_by: A series of Globus identities which may update
            this Flow's definition

        :param subscription_id: The Globus Subscription which will be used to make this
        flow managed.

        :param input_schema: A mapping representing the JSONSchema used to
            validate input to this Flow. If not supplied, no validation will be
            done on input to this Flow.

        :param validate_definition: Set to ``True`` to validate the provided
            ``flow_definition`` before attempting to update the Flow.

        :param validate_input_schema: Set to ``True`` to validate the provided
            ``input_schema`` before attempting to update the Flow.
        """
        if validate_definition and flow_definition is not None:
            validate_flow_definition(flow_definition)
        self.authorizer = self.flow_management_authorizer
        temp_body: Dict[str, Any] = {"definition": flow_definition, "title": title}
        temp_body["subtitle"] = subtitle
        temp_body["description"] = description
        temp_body["keywords"] = keywords
        temp_body["visible_to"] = visible_to
        temp_body["runnable_by"] = runnable_by
        temp_body["administered_by"] = administered_by
        temp_body["subscription_id"] = subscription_id
        temp_body["input_schema"] = input_schema
        # Remove None / empty list items from the temp_body
        req_body = {k: v for k, v in temp_body.items() if v}
        if len(req_body) == 0:
            return None
        else:
            return self.put(f"/flows/{flow_id}", req_body, **kwargs)

    def get_flow(self, flow_id: str, **kwargs) -> GlobusHTTPResponse:
        """
        Retrieve a deployed Flow's definition and metadata

        :param flow_id: The UUID identifying the Flow for which to retrieve
            details
        """
        self.authorizer = self.flow_management_authorizer
        path = self.qjoin_path(flow_id)
        return self.get(path, **kwargs)

    def list_flows(
        self,
        roles: Optional[List[str]] = None,
        marker: Optional[str] = None,
        per_page: Optional[int] = None,
        filters: Optional[dict] = None,
        orderings: Optional[dict] = None,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """
        Display all deployed Flows for which you have the selected role(s)

        :param roles:
            A list of roles specifying the level of access you have
            for a Flow. Valid values are:

            - created_by
            - visible_to
            - runnable_by
            - administered_by

            Each value in the ``roles`` list is Or-ed to retrieve a listing of Flows
            where the retrieving identity has at least one of the listed roles on
            each Flow
        :param marker: A pagination_token indicating the page of results to
            return and how many entries to return. This is created by the Flow's
            service and returned by operations that support pagination.
        :param per_page: The number of results to return per page. If
            supplied a pagination_token, this parameter has no effect.
        :param filters: A filtering criteria to apply to the resulting Flow
            listing. The keys indicate the filter, the values indicate the
            pattern to match. The returned data will be the result of a logical
            AND between the filters. Patterns may be comma separated to produce
            the result of a logical OR.
        :param orderings: An ordering criteria to apply to the resulting
            Flow listing. The keys indicate the field to order on, and
            the value can be either ASC, for ascending order, or DESC, for
            descending order. The first ordering criteria will be used to sort
            the data, subsequent ordering criteria will be applied for ties.
            Note: To ensure orderings are applied in the correct order, use an
            OrderedDict if trying to apply multiple orderings.
        """
        self.authorizer = self.flow_management_authorizer
        params = {}
        if roles is not None and len(roles) > 0:
            params.update(dict(filter_roles=",".join(roles)))
        if marker is not None:
            params["pagination_token"] = marker
        if per_page is not None and marker is None:
            params["per_page"] = str(per_page)
        if filters is not None:
            params.update(filters)
        if orderings:
            builder = []
            for field, value in orderings.items():
                builder.append(f"{field} {value}")
            params["orderby"] = ",".join(builder)
        return self.get("/flows", params=params, **kwargs)

    def delete_flow(self, flow_id: str, **kwargs):
        """
        Remove a Flow definition and its metadata from the Flows service

        :param flow_id: The UUID identifying the Flow to delete
        """
        self.authorizer = self.flow_management_authorizer
        return self.delete(f"/flows/{flow_id}", **kwargs)

    def scope_for_flow(self, flow_id: str) -> str:
        """
        Returns the scope associated with a particular Flow

        :param flow_id: The UUID identifying the Flow's scope to lookup
        """
        flow_url = f"{self.base_url}/flows/{flow_id}"
        return ActionClient.new_client(
            flow_url, authorizer=self.authorizer
        ).action_scope

    def _get_authorizer_for_flow(
        self, flow_id: str, flow_scope: Optional[str], extras: Dict[str, Any]
    ) -> AllowedAuthorizersType:
        if "authorizer" in extras:
            return extras.pop("authorizer")

        if flow_scope is None:
            flow_scope = self.scope_for_flow(flow_id)

        flow_url = f"{self.base_url}/flows/{flow_id}"
        return self.get_authorizer_callback(
            flow_url=flow_url,
            flow_scope=flow_scope,
            client_id=self.client_id,
        )

    def run_flow(
        self,
        flow_id: str,
        flow_scope: Optional[str],
        flow_input: Mapping,
        manage_by: Optional[List[str]] = None,
        monitor_by: Optional[List[str]] = None,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """
        Run an instance of a deployed Flow with the given input.

        :param flow_id: The UUID identifying the Flow to run

        :param flow_scope:  The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to determine its scope automatically

        :param flow_input: A Flow-specific dictionary specifying the input
            required for the Flow to run.

        :param manage_by: A series of Globus identities which may alter
            this Flow instance's execution. The principal value is the user's or
            group's UUID prefixed with either 'urn:globus:groups:id:' or
            'urn:globus:auth:identity:'

        :param monitor_by: A series of Globus identities which may view this
            Flow instance's execution state. The principal value is the user's
            or group's UUID prefixed with either 'urn:globus:groups:id:' or
            'urn:globus:auth:identity:'

        :param kwargs: Any additional kwargs passed into this method are passed
            onto the Globus BaseClient. If there exists an "authorizer" keyword
            argument, that gets used to run the Flow operation. Otherwise the
            authorizer_callback defined for the FlowsClient will be used.
        """
        authorizer = self._get_authorizer_for_flow(flow_id, flow_scope, kwargs)
        flow_url = f"{self.base_url}/flows/{flow_id}"
        ac = ActionClient.new_client(flow_url, authorizer)
        return ac.run(flow_input, manage_by=manage_by, monitor_by=monitor_by, **kwargs)

    def flow_action_status(
        self, flow_id: str, flow_scope: Optional[str], flow_action_id: str, **kwargs
    ) -> GlobusHTTPResponse:
        """
        Determine the status for an Action that was launched by a Flow

        :param flow_id: The UUID identifying the Flow which triggered the Action

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to determine its scope automatically

        :param flow_action_id: The ID specifying the Action for which's status
            we want to query

        :param kwargs: Any additional kwargs passed into this method are passed
            onto the Globus BaseClient. If there exists an "authorizer" keyword
            argument, that gets used to run the Flow operation. Otherwise the
            authorizer_callback defined for the FlowsClient will be used.
        """
        authorizer = self._get_authorizer_for_flow(flow_id, flow_scope, kwargs)
        flow_url = f"{self.base_url}/flows/{flow_id}"
        ac = ActionClient.new_client(flow_url, authorizer)
        return ac.status(flow_action_id)

    def flow_action_resume(
        self, flow_id: str, flow_scope: Optional[str], flow_action_id: str, **kwargs
    ) -> GlobusHTTPResponse:
        """
        Resume a Flow Action which is in an INACTIVE state.

        :param flow_id: The UUID identifying the Flow which triggered the Action

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to determine its scope automatically.

        :param flow_action_id: The ID specifying the Action with an INACTIVE
            status we want to resume.

        :param kwargs: Any additional kwargs passed into this method are passed
            onto the Globus BaseClient. If there exists an "authorizer" keyword
            argument, that gets used to run the Flow operation. Otherwise the
            authorizer_callback defined for the FlowsClient will be used.
        """
        authorizer = self._get_authorizer_for_flow(flow_id, flow_scope, kwargs)
        flow_url = f"{self.base_url}/flows/{flow_id}"
        ac = ActionClient.new_client(flow_url, authorizer)
        return ac.resume(flow_action_id)

    def flow_action_release(
        self, flow_id: str, flow_scope: Optional[str], flow_action_id: str, **kwargs
    ) -> GlobusHTTPResponse:
        """
        Remove the execution history for an Action that was launched by a Flow

        :param flow_id: The UUID identifying the Flow which launched the Action

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to determine its scope automatically

        :param flow_action_id: The ID specifying the Action to release

        :param kwargs: Any additional kwargs passed into this method are passed
            onto the Globus BaseClient. If there exists an "authorizer" keyword
            argument, that gets used to run the Flow operation. Otherwise the
            authorizer_callback defined for the FlowsClient will be used.
        """
        authorizer = self._get_authorizer_for_flow(flow_id, flow_scope, kwargs)
        flow_url = f"{self.base_url}/flows/{flow_id}"
        ac = ActionClient.new_client(flow_url, authorizer)
        return ac.release(flow_action_id)

    def flow_action_cancel(
        self, flow_id: str, flow_scope: Optional[str], flow_action_id: str, **kwargs
    ) -> GlobusHTTPResponse:
        """
        Cancel the excution of an Action that was launched by a Flow

        :param flow_id: The UUID identifying the Flow which launched the Action

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to determine its scope automatically

        :param flow_action_id: The ID specifying the Action we want to cancel

        :param kwargs: Any additional kwargs passed into this method are passed
            onto the Globus BaseClient. If there exists an "authorizer" keyword
            argument, that gets used to run the Flow operation. Otherwise the
            authorizer_callback defined for the FlowsClient will be used.
        """
        authorizer = self._get_authorizer_for_flow(flow_id, flow_scope, kwargs)
        flow_url = f"{self.base_url}/flows/{flow_id}"
        ac = ActionClient.new_client(flow_url, authorizer)
        return ac.cancel(flow_action_id)

    def list_flow_actions(
        self,
        flow_id: str,
        flow_scope: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
        marker: Optional[str] = None,
        per_page: Optional[int] = None,
        filters: Optional[dict] = None,
        orderings: Optional[dict] = None,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """
        List all Actions that were launched as part of a Flow's run

        :param flow_id: The UUID identifying the Flow which launched the Action

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to determine its scope automatically

        :param statuses: A list of statuses used to filter the Actions that are
            returned by the listing. Returned Actions are guaranteed to have one
            of the specified ``statuses``. Valid values are:

            - SUCCEEDED
            - FAILED
            - ACTIVE
            - INACTIVE

        :param roles: A list of roles used to filter the Actions that are
            returned by the listing. Returned Actions are guaranteed to have the
            callers identity in the specified role. Valid values are:

            - created_by
            - visible_to
            - runnable_by
            - administered_by

        :param marker: A pagination_token indicating the page of results to
            return and how many entries to return. This is created by the Flow's
            service and returned by operations that support pagination.
        :param per_page: The number of results to return per page. If
            supplied a pagination_token, this parameter has no effect.
        :param filters: A filtering criteria to apply to the resulting Action
            listing. The keys indicate the filter, the values indicate the
            pattern to match. The returned data will be the result of a logical
            AND between the filters. Patterns may be comma separated to produce
            the result of a logical OR.
        :param orderings: An ordering criteria to apply to the resulting
            Action listing. The keys indicate the field to order on, and
            the value can be either ASC, for ascending order, or DESC, for
            descending order. The first ordering criteria will be used to sort
            the data, subsequent ordering criteria will be applied for ties.
            Note: To ensure orderings are applied in the correct order, use an
            OrderedDict if trying to apply multiple orderings.

        :param kwargs: Any additional kwargs passed into this method are passed
            onto the Globus BaseClient. If there exists an "authorizer" keyword
            argument, that gets used to run the Flow operation. Otherwise the
            authorizer_callback defined for the FlowsClient will be used.
        """
        params = {}
        if statuses is not None and len(statuses) > 0:
            params.update(dict(filter_status=",".join(statuses)))
        if roles is not None and len(roles) > 0:
            params.update(dict(filter_roles=",".join(roles)))
        if marker is not None:
            params["pagination_token"] = marker
        if per_page is not None and marker is None:
            params["per_page"] = str(per_page)
        if filters:
            params.update(filters)
        if orderings:
            builder = []
            for field, value in orderings.items():
                builder.append(f"{field} {value}")
            params["orderby"] = ",".join(builder)

        self.authorizer = self._get_authorizer_for_flow(flow_id, flow_scope, kwargs)
        response = self.get(f"/flows/{flow_id}/actions", params=params, **kwargs)
        self.authorizer = self.flow_management_authorizer
        return response

    def flow_action_log(
        self,
        flow_id: str,
        flow_scope: str,
        flow_action_id: str,
        limit: int = 10,
        reverse_order: bool = False,
        marker: Optional[str] = None,
        per_page: Optional[int] = None,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """
        Retrieve an Action's execution log history for an Action that was launched by a
        specific Flow.

        :param flow_id:  The UUID identifying the Flow which launched the Action

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to determine its scope automatically

        :param flow_action_id: The ID specifying the Action for which's history
            to query

        :param limit: An integer specifying the maximum number of records for
            the Action's execution history to return.

        :param reverse_order: An indicator for whether to retrieve the records
            in reverse-chronological order.

        :param marker: A pagination_token indicating the page of results to
            return and how many entries to return. This is created by the Flow's
            service and returned by operations that support pagination.
        :param per_page: The number of results to return per page. If
            supplied a pagination_token, this parameter has no effect.

        :param kwargs: Any additional kwargs passed into this method are passed
            onto the Globus BaseClient. If there exists an "authorizer" keyword
            argument, that gets used to run the Flow operation. Otherwise the
            authorizer_callback defined for the FlowsClient will be used.
        """
        authorizer = self._get_authorizer_for_flow(flow_id, flow_scope, kwargs)
        flow_url = f"{self.base_url}/flows/{flow_id}"
        ac = ActionClient.new_client(flow_url, authorizer)
        return ac.log(flow_action_id, limit, reverse_order, marker, per_page)

    @classmethod
    def new_client(
        cls: Type[_FlowsClient],
        client_id: str,
        authorizer_callback: AuthorizerCallbackType,
        authorizer: AllowedAuthorizersType,
        base_url: Optional[str] = None,
        http_timeout: int = 10,
    ) -> _FlowsClient:
        """
        Classmethod to simplify creating an FlowsClient. Use this method when
        attemping to create a FlowsClient with pre-existing credentials or
        authorizers. This method is useful when creating a FlowClient for
        interacting with a Flow without wanting to launch an interactive login
        process.

        :param client_id: The client_id to associate with this FlowsClient.

        :param authorizer_callback: A callable which is capable of returning an
            authorizer for a particular Flow. The callback should accept three
            keyword-args: flow_url, flow_scope, client_id. Using some, all, or
            none of these args, the callback should return a GlobusAuthorizer
            which provides access to the targetted Flow.

        :param authorizer: The authorizer to use for validating requests to the
            Flows service. This authorizer is used when interacting with the
            Flow's service, it is not used for interactive with a particular
            flow. Therefore, this authorizer should grant consent to the
            MANAGE_FLOWS_SCOPE. For interacting with a particular flow, set the
            authorizer_callback parameter.

        :param base_url: The url at which the target Action Provider is
            located.

        **Examples**
            >>> def cli_authorizer_callback(**kwargs):
                    flow_url = kwargs["flow_url"]
                    flow_scope = kwargs["flow_scope"]
                    client_id = kwargs["client_id"]
                    return get_cli_authorizer(flow_url, flow_scope, client_id)
            >>> action_url = "https://actions.globus.org/hello_world"
            >>> client_id = "00000000-0000-0000-0000-000000000000"
            >>> auth = ...
            >>> fc = FlowsClient.new_client(client_id, cli_authorizer_callback, auth)
            >>> print(fc.list_flows())
        """
        if base_url is None:
            base_url = _get_flows_base_url_for_environment()
        return cls(
            client_id,
            authorizer_callback,
            "flows_client",
            app_name="Globus Automate SDK FlowsClient",
            base_url=base_url,
            authorizer=authorizer,
            http_timeout=http_timeout,
        )
