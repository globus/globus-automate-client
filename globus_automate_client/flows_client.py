import contextlib
import json
import os
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)
from urllib.parse import quote

from globus_sdk import (
    AccessTokenAuthorizer,
    BaseClient,
    ClientCredentialsAuthorizer,
    GlobusHTTPResponse,
    RefreshTokenAuthorizer,
)
from jsonschema import Draft7Validator

from globus_automate_client import ActionClient

from .helpers import merge_lists

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
RUN_MANAGE_SCOPE = (
    "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/run_manage"
)
NULL_SCOPE = "https://auth.globus.org/scopes/eec9b274-0c81-4334-bdc2-54e90e689b9a/null"

ALL_FLOW_SCOPES = (
    MANAGE_FLOWS_SCOPE,
    VIEW_FLOWS_SCOPE,
    RUN_FLOWS_SCOPE,
    RUN_STATUS_SCOPE,
    RUN_MANAGE_SCOPE,
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
                if k in key_name_set and isinstance(val, str):
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


def validate_input_schema(input_schema: Optional[Mapping[str, Any]]) -> None:
    if input_schema is None:
        raise FlowValidationError(["No input schema provided"])
    validator = Draft7Validator(Draft7Validator.META_SCHEMA)
    errors = validator.iter_errors(input_schema)
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

    base_path: str = ""
    service_name: str = "flows"

    def __init__(
        self,
        client_id: str,
        get_authorizer_callback: AuthorizerCallbackType,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.client_id = client_id
        self.get_authorizer_callback = get_authorizer_callback

    @contextlib.contextmanager
    def use_temporary_authorizer(self, authorizer):
        """Temporarily swap out the authorizer instance variable.

        This is a context manager. Use it like this:

        ..  code-block:: python

            authorizer = self._get_authorizer_for_flow(...)
            with self.alternate_authorizer(authorizer):
                ...

        """

        original, self.authorizer = self.authorizer, authorizer
        try:
            yield
        finally:
            self.authorizer = original

    def deploy_flow(
        self,
        flow_definition: Mapping[str, Any],
        title: str,
        subtitle: Optional[str] = None,
        description: Optional[str] = None,
        keywords: Iterable[str] = (),
        flow_viewers: Iterable[str] = (),
        flow_starters: Iterable[str] = (),
        flow_administrators: Iterable[str] = (),
        subscription_id: Optional[str] = None,
        input_schema: Optional[Mapping[str, Any]] = None,
        validate_definition: bool = True,
        validate_schema: bool = True,
        dry_run: bool = False,
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

        :param flow_viewers: A series of Globus identities which may discover and
            view the Flow definition

        :param flow_starters: A series of Globus identities which may run an
            instance of this Flow

        :param flow_administrators: A series of Globus identities which may update
            this Flow's definition

        :param subscription_id: The Globus Subscription which will be used to
            make this flow managed.

        :param input_schema: A mapping representing the JSONSchema used to
            validate input to this Flow. If not supplied, no validation will be
            done on input to this Flow.

        :param validate_definition: Set to ``True`` to validate the provided
            ``flow_definition`` before attempting to deploy the Flow.

        :param validate_schema: Set to ``True`` to validate the provided
            ``input_schema`` before attempting to deploy the Flow.

        :param dry_run: Set to ``True`` to test whether the Flow can be
            deployed successfully.

        """
        if validate_definition:
            validate_flow_definition(flow_definition)
        if validate_schema:
            validate_input_schema(input_schema)
        temp_body: Dict[str, Any] = {
            "definition": flow_definition,
            "title": title,
            "subtitle": subtitle,
            "description": description,
            "keywords": keywords,
            "flow_viewers": merge_lists(flow_viewers, kwargs, "visible_to", "viewers"),
            "flow_starters": merge_lists(
                flow_starters, kwargs, "runnable_by", "starters"
            ),
            "flow_administrators": merge_lists(
                flow_administrators, kwargs, "administered_by", "administrators"
            ),
            "subscription_id": subscription_id,
        }
        # Remove None / empty list items from the temp_body
        req_body = {k: v for k, v in temp_body.items() if v}
        # We do this after clearing false truthy values since an empty input schema is a
        # valid thing
        if input_schema is not None:
            req_body["input_schema"] = input_schema
        url = "/flows"
        if dry_run:
            url = "/flows/dry-run"
        return self.post(url, data=req_body, **kwargs)

    def update_flow(
        self,
        flow_id: str,
        flow_definition: Optional[Mapping[str, Any]] = None,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        description: Optional[str] = None,
        keywords: Iterable[str] = (),
        flow_viewers: Iterable[str] = (),
        flow_starters: Iterable[str] = (),
        flow_administrators: Iterable[str] = (),
        subscription_id: Optional[str] = None,
        input_schema: Optional[Mapping[str, Any]] = None,
        validate_definition: bool = True,
        validate_schema: bool = True,
        **kwargs,
    ) -> GlobusHTTPResponse:
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

        :param flow_viewers: A series of Globus identities which may discover and
            view the Flow definition

        :param flow_starters: A series of Globus identities which may run an
            instance of this Flow

        :param flow_administrators: A series of Globus identities which may update
            this Flow's definition

        :param subscription_id: The Globus Subscription which will be used to
            make this flow managed.

        :param input_schema: A mapping representing the JSONSchema used to
            validate input to this Flow. If not supplied, no validation will be
            done on input to this Flow.

        :param validate_definition: Set to ``True`` to validate the provided
            ``flow_definition`` before attempting to update the Flow.

        :param validate_schema: Set to ``True`` to validate the provided
            ``input_schema`` before attempting to update the Flow.
        """
        if validate_definition and flow_definition is not None:
            validate_flow_definition(flow_definition)
        if validate_schema and input_schema is not None:
            validate_input_schema(input_schema)
        temp_body: Dict[str, Any] = {
            "definition": flow_definition,
            "title": title,
            "subtitle": subtitle,
            "description": description,
            "keywords": keywords,
            "flow_viewers": merge_lists(flow_viewers, kwargs, "visible_to", "viewers"),
            "flow_starters": merge_lists(
                flow_starters, kwargs, "runnable_by", "starters"
            ),
            "flow_administrators": merge_lists(
                flow_administrators, kwargs, "administered_by", "administrators"
            ),
            "subscription_id": subscription_id,
        }
        # Remove None / empty list items from the temp_body
        data = {k: v for k, v in temp_body.items() if v}
        # After removing false-y values, add the input schema.
        if input_schema is not None:
            data["input_schema"] = input_schema

        return self.put(f"/flows/{flow_id}", data=data, **kwargs)

    def get_flow(self, flow_id: str, **kwargs) -> GlobusHTTPResponse:
        """
        Retrieve a deployed Flow's definition and metadata

        :param flow_id: The UUID identifying the Flow for which to retrieve
            details
        """
        return self.get(f"/flows/{quote(flow_id)}", **kwargs)

    def list_flows(
        self,
        roles: Optional[Iterable[str]] = None,
        marker: Optional[str] = None,
        per_page: Optional[int] = None,
        filters: Optional[dict] = None,
        orderings: Optional[dict] = None,
        role: Optional[str] = None,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """Display all deployed Flows for which you have the selected role(s)

        :param roles:
            .. deprecated:: 0.12
               Use ``role`` instead

            See description for ``role`` parameter. Providing multiple roles behaves as
            if only a single ``role`` value is provided and displays the equivalent of
            the most permissive role.

        :param role: A role value specifying the minimum role-level permission which will
            be displayed based on the follow precedence of role values:

            - flow_viewer
            - flow_starter
            - flow_administrators
            - flow_owner

            Thus, if, for example, ``flow_starter`` is specified, flows for which the
            user has the ``flow_starter``, ``flow_administrator`` or ``flow_owner`` roles
            will be returned.

        :param marker: A pagination_token indicating the page of results to
            return and how many entries to return. This is created by the Flows
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
        params = {}
        if roles:
            params["filter_roles"] = ",".join(roles)
        if role is not None:
            params["filter_role"] = role
            params.pop(
                "filter_roles", None
            )  # role takes precedence over roles (plural)
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
        return self.get("/flows", query_params=params, **kwargs)

    def delete_flow(self, flow_id: str, **kwargs) -> GlobusHTTPResponse:
        """
        Remove a Flow definition and its metadata from the Flows service

        :param flow_id: The UUID identifying the Flow to delete
        """
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
        run_managers: Optional[Iterable[str]] = None,
        run_monitors: Optional[Iterable[str]] = None,
        dry_run: bool = False,
        label: Optional[str] = None,
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

        :param run_managers: A series of Globus identities which may alter
            this Flow instance's execution. The principal value is the user's or
            group's UUID prefixed with either 'urn:globus:groups:id:' or
            'urn:globus:auth:identity:'

        :param run_monitors: A series of Globus identities which may view this
            Flow instance's execution state. The principal value is the user's
            or group's UUID prefixed with either 'urn:globus:groups:id:' or
            'urn:globus:auth:identity:'

        :param label: An optional label which can be used to identify this run

        :param kwargs: Any additional kwargs passed into this method are passed
            onto the Globus BaseClient. If there exists an "authorizer" keyword
            argument, that gets used to run the Flow operation. Otherwise the
            authorizer_callback defined for the FlowsClient will be used.

        :param dry_run: Set to ``True`` to test what will happen if the Flow is run
            without actually running the Flow.

        """

        authorizer = self._get_authorizer_for_flow(flow_id, flow_scope, kwargs)
        flow_url = f"{self.base_url}/flows/{flow_id}"
        ac = ActionClient.new_client(flow_url, authorizer)
        run_monitors = merge_lists(run_monitors, kwargs, "monitor_by")
        run_managers = merge_lists(run_managers, kwargs, "manage_by")

        kwargs.pop("monitor_by", None)
        kwargs.pop("manage_by", None)
        if dry_run:
            path = flow_url + "/dry-run"
            return ac.run(
                flow_input,
                manage_by=run_managers,
                monitor_by=run_monitors,
                force_path=path,
                label=label,
                **kwargs,
            )
        else:
            return ac.run(
                flow_input,
                manage_by=run_managers,
                monitor_by=run_monitors,
                label=label,
                **kwargs,
            )

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

    def enumerate_runs(
        self,
        roles: Optional[Iterable[str]] = None,
        statuses: Optional[Iterable[str]] = None,
        marker: Optional[str] = None,
        per_page: Optional[int] = None,
        filters: Optional[dict] = None,
        orderings: Optional[dict] = None,
        role: Optional[str] = None,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """
        Retrieve a listing of Runs the caller has access to. This operation
        requires the supplied Authorizer to have the RUN_STATUS_SCOPE.

        :param statuses: A list of statuses used to filter the Actions that are
            returned by the listing. Returned Actions are guaranteed to have one
            of the specified ``statuses``. Valid values are:

            - SUCCEEDED
            - FAILED
            - ACTIVE
            - INACTIVE

        :param roles:
          .. deprecated:: 0.12
             Use ``role`` instead

            See description for ``role`` parameter. Providing multiple roles behaves as
            if only a single ``role`` value is provided and displays the equivalent of
            the most permissive role.

        :param role: A role value specifying the minimum role-level permission on the runs which will
            be returned based on the follow precedence of role values:

            - run_monitor
            - run_manager
            - run_owner

            Thus, if, for example, ``run_manager`` is specified, runs for which the
            user has the ``run_manager``, or ``run_owner`` roles
            will be returned.

        :param marker: A pagination_token indicating the page of results to
            return and how many entries to return. This is created by the Flows
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

        """
        params = {}
        if role:
            params["filter_role"] = role
        elif roles:
            params["filter_roles"] = ",".join(roles)
        if statuses:
            params["filter_status"] = ",".join(statuses)
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

        authorizer = self._get_authorizer_for_flow("", RUN_STATUS_SCOPE, kwargs)
        with self.use_temporary_authorizer(authorizer):
            return self.get("/runs", query_params=params, **kwargs)

    def enumerate_actions(
        self,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """
        An alias for ``enumerate_runs``
        """
        return self.enumerate_runs(**kwargs)

    def list_flow_actions(
        self,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """
        An alias for ``list_flow_runs``
        """
        return self.list_flow_runs(**kwargs)

    def list_flow_runs(
        self,
        flow_id: Optional[str] = None,
        flow_scope: Optional[str] = None,
        statuses: Optional[Iterable[str]] = None,
        roles: Optional[Iterable[str]] = None,
        marker: Optional[str] = None,
        per_page: Optional[int] = None,
        filters: Optional[dict] = None,
        orderings: Optional[dict] = None,
        role: Optional[str] = None,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """List all Runs for a particular Flow. If no flow_id is provided, all runs for all
        Flows will be returned.

        :param flow_id: The UUID identifying the Flow which launched the Run. If not
            provided, all runs will be returned regardless of which Flow was used to start
            the Run (equivalent to ``enumerate_runs``).

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to determine its scope automatically

        :param  statuses: The same as in ``enumerate_runs``.

        :param roles:
            ..  deprecated:: 0.12
                Use ``role`` instead

            The same as in ``enumerate_runs``.

        :param  marker: The same as in ``enumerate_runs``.

        :param  per_page: The same as in ``enumerate_runs``.

        :param  filters: The same as in ``enumerate_runs``.

        :param  orderings: The same as in ``enumerate_runs``.

        :param  role: The same as in ``enumerate_runs``.

        :param kwargs: Any additional kwargs passed into this method are passed
            onto the Globus BaseClient. If there exists an "authorizer" keyword
            argument, that gets used to run the Flow operation. Otherwise the
            authorizer_callback defined for the FlowsClient will be used.

        """
        if flow_id is None:
            return self.enumerate_runs(
                roles=roles,
                statuses=statuses,
                marker=marker,
                per_page=per_page,
                filters=filters,
                orderings=orderings,
                role=role,
            )

        params = {}
        if statuses:
            params["filter_status"] = ",".join(statuses)
        if roles:
            params["filter_roles"] = ",".join(roles)
        if role is not None:
            params["filter_role"] = role
            params.pop(
                "filter_roles", None
            )  # role takes precedence over roles (plural)
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

        authorizer = self._get_authorizer_for_flow(flow_id, flow_scope, kwargs)
        with self.use_temporary_authorizer(authorizer):
            return self.get(f"/flows/{flow_id}/actions", query_params=params, **kwargs)

    def flow_action_update(
        self,
        action_id: str,
        run_managers: Optional[Iterable[str]] = None,
        run_monitors: Optional[Iterable[str]] = None,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """
        Update a Flow Action.

        :param action_id: The UUID identifying the Action to update

        :param run_managers: A list of Globus Auth URNs which will have the
            ability to alter the execution of the Action. Supplying an empty
            list will remove all existing managers.

        :param run_monitors: A list of Globus Auth URNs which will have the
            ability to view the execution of the Action. Supplying an empty list
            will remove all existing monitors.

        :param kwargs: Any additional kwargs passed into this method are passed
            onto the Globus BaseClient. If there exists an "authorizer" keyword
            argument, that gets used to run the Flow operation. Otherwise the
            authorizer_callback defined for the FlowsClient will be used.
        """
        payload = {}
        if run_managers is not None:
            payload["run_managers"] = run_managers
        if run_monitors is not None:
            payload["run_monitors"] = run_monitors

        authorizer = self._get_authorizer_for_flow("", RUN_MANAGE_SCOPE, kwargs)
        with self.use_temporary_authorizer(authorizer):
            return self.put(f"/runs/{quote(action_id)}", data=payload, **kwargs)

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
            return and how many entries to return. This is created by the Flows
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
            app_name="Globus Automate SDK FlowsClient",
            base_url=base_url,
            authorizer=authorizer,
        )
