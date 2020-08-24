import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set

from globus_sdk import (
    AccessTokenAuthorizer,
    ClientCredentialsAuthorizer,
    GlobusHTTPResponse,
    RefreshTokenAuthorizer,
)
from globus_sdk.base import BaseClient
from jsonschema import Draft7Validator

from globus_automate_client.action_client import ActionClient, create_action_client
from globus_automate_client.token_management import get_authorizer_for_scope

PROD_FLOWS_BASE_URL = "https://flows.globus.org"

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


class FlowValidationError(Exception):
    def __init__(self, errors: Iterable[str], **kwargs):
        message = "; ".join(errors)
        super().__init__(message, **kwargs)


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
                if isinstance(val, str):
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

    def __init__(self, client_id: str, *args, **kwargs) -> None:
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
        input_schema: Optional[Mapping[str, Any]] = None,
        validate_definition: bool = True,
        validate_input_schema: bool = True,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """
        Deploys a Flow definition to the Flows service, making the Flow
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
        self.authorizer = get_authorizer_for_scope(MANAGE_FLOWS_SCOPE, self.client_id)
        temp_body: Dict[str, Any] = {"definition": flow_definition, "title": title}
        temp_body["subtitle"] = subtitle
        temp_body["description"] = description
        temp_body["keywords"] = keywords
        temp_body["visible_to"] = visible_to
        temp_body["runnable_by"] = runnable_by
        temp_body["administered_by"] = administered_by
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
            this Flow's defintion

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
        self.authorizer = get_authorizer_for_scope(MANAGE_FLOWS_SCOPE, self.client_id)
        temp_body: Dict[str, Any] = {"definition": flow_definition, "title": title}
        temp_body["subtitle"] = subtitle
        temp_body["description"] = description
        temp_body["keywords"] = keywords
        temp_body["visible_to"] = visible_to
        temp_body["runnable_by"] = runnable_by
        temp_body["administered_by"] = administered_by
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

        self.authorizer = get_authorizer_for_scope(MANAGE_FLOWS_SCOPE, self.client_id)
        path = self.qjoin_path(flow_id)
        return self.get(path, **kwargs)

    def list_flows(
        self, roles: Optional[List[str]] = None, **kwargs
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
        """
        self.authorizer = get_authorizer_for_scope(MANAGE_FLOWS_SCOPE, self.client_id)
        params = {}
        if roles is not None and len(roles) > 0:
            params.update(dict(roles=",".join(roles)))
        return self.get("/flows", params=params, **kwargs)

    def _scope_for_flow(self, flow_id: str) -> str:
        flow_defn = self.get_flow(flow_id)
        flow_scope = flow_defn.get("globus_auth_scope", flow_defn.get("scope_string"))
        return flow_scope

    def _action_client_for_flow(
        self, flow_id: str, flow_scope: Optional[str] = None
    ) -> ActionClient:
        if flow_scope is None:
            ac = create_action_client(
                f"{self.base_url}/flows/{flow_id}", VIEW_FLOWS_SCOPE
            )
            flow_scope = ac.action_scope

        ac = create_action_client(f"{self.base_url}/flows/{flow_id}", flow_scope)
        return ac

    def run_flow(
        self, flow_id: str, flow_scope: Optional[str], flow_input: Mapping, **kwargs
    ) -> GlobusHTTPResponse:
        """
        Run an instance of a deployed Flow with the given input.

        :param flow_id: The UUID identifying the Flow to run

        :param flow_scope:  The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to pull its scope automatically

        :param flow_input: A Flow-specific dictionary specifying the input
            required for the Flow to run.
        """
        ac = self._action_client_for_flow(flow_id, flow_scope)
        return ac.run(flow_input, **kwargs)

    def flow_action_status(
        self, flow_id: str, flow_scope: Optional[str], flow_action_id: str, **kwargs
    ) -> GlobusHTTPResponse:
        """
        Determine the status for an Action that was launched by a Flow

        :param flow_id: The UUID identifying the Flow which triggered the Action

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to pull its scope automatically

        :param flow_action_id: The ID specifying the Action for which's status
            we want to query
        """
        ac = self._action_client_for_flow(flow_id, flow_scope)
        return ac.status(flow_action_id)

    def flow_action_release(
        self, flow_id: str, flow_scope: Optional[str], flow_action_id: str, **kwargs
    ) -> GlobusHTTPResponse:
        """
        Remove the execution history for an Action that was launched by a Flow

        :param flow_id: The UUID identifying the Flow which launched the Action

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to pull its scope automatically

        :param flow_action_id: The ID specifying the Action to release
        """
        ac = self._action_client_for_flow(flow_id, flow_scope)
        return ac.release(flow_action_id)

    def flow_action_cancel(
        self, flow_id: str, flow_scope: Optional[str], flow_action_id: str, **kwargs
    ) -> GlobusHTTPResponse:
        """
        Cancel the excution of an Action that was launched by a Flow

        :param flow_id: The UUID identifying the Flow which launched the Action

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to pull its scope automatically

        :param flow_action_id: The ID specifying the Action we want to cancel
        """

        ac = self._action_client_for_flow(flow_id, flow_scope)
        return ac.cancel(flow_action_id)

    def list_flow_actions(
        self,
        flow_id: str,
        flow_scope: Optional[str],
        statuses: Optional[List[str]],
        roles: Optional[List[str]] = None,
        **kwargs,
    ) -> GlobusHTTPResponse:
        """
        List all Actions that were launched as part of a Flow's run

        :param flow_id: The UUID identifying the Flow which launched the Action

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to pull its scope automatically

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
        """
        if flow_scope is None:
            flow_scope = self._scope_for_flow(flow_id)
        self.authorizer = get_authorizer_for_scope(flow_scope, self.client_id)
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
        """
        Retrieve an Action's execution log history for an Action that was launched by a
        specific Flow.

        :param flow_id:  The UUID identifying the Flow which launched the Action

        :param flow_scope: The scope associated with the Flow ``flow_id``. If
            not provided, the SDK will attempt to perform an introspection on
            the Flow to pull its scope automatically

        :param flow_action_id: The ID specifying the Action for which's history
            to query

        :param limit: An integer specifying the maximum number of records for
            the Action's execution history to return.

        :param reverse_order: An indicator for whether to retrieve the records
            in reverse-chronological order.
        """
        if flow_scope is None:
            flow_scope = self._scope_for_flow(flow_id)
        self.authorizer = get_authorizer_for_scope(flow_scope, self.client_id)
        params = {"reverse_order": reverse_order, "limit": limit}
        return self.get(
            f"/flows/{flow_id}/{flow_action_id}/log", params=params, **kwargs
        )

    def delete_flow(self, flow_id: str, **kwargs):
        """
        Remove a Flow defintion and its metadata from the Flows service

        :param flow_id: The UUID identifying the Flow to delete
        """
        return self.delete(f"/flows/{flow_id}", **kwargs)


def create_flows_client(
    client_id: str, base_url: str = PROD_FLOWS_BASE_URL
) -> FlowsClient:
    """
    A helper function to handle creating a properly authenticated
    ``FlowsClient`` which can operate against the Globus Automate Flows service.

    If necessary, it's possible to supply a custom ``base_url`` to indicate the
    address at which the Flows Service is located.

    This function will attempt to load tokens for the MANAGE_FLOWS_SCOPE using
    the fair_research_login library. In the event that tokens for the scope
    cannot be loaded, an interactive login Flow will be triggered. Once tokens
    have been loaded, an Authorizer is created and used to instantiate the
    ``FlowsClient``.

    :param client_id: The Globus ID to associate with this instance of the
        FlowsClient
    :param base_url: The URL at which the Globus Automate Flows service is
        located
    """
    authorizer = get_authorizer_for_scope(MANAGE_FLOWS_SCOPE, client_id)
    return FlowsClient(
        client_id,
        "flows_client",
        base_url=base_url,
        app_name="flows_client",
        authorizer=authorizer,
    )
