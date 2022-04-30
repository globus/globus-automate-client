import abc
import collections
import functools
import json
from time import sleep
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union, cast

import arrow
import typer
import yaml
from globus_sdk import AuthClient, BaseClient, GlobusAPIError, GlobusHTTPResponse
from requests import Response
from rich.console import Group, RenderableType
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text
from typing_extensions import Literal

from .auth import get_authorizers_for_scopes
from .constants import OutputFormat
from .helpers import get_http_details
from .rich_rendering import cli_content, live_content

_title_max_width = 25
_uuid_min_width = 36


def humanize_datetimes(dt: str) -> str:
    return arrow.get(dt).humanize()


def humanize_auth_urn(urn: str) -> str:
    id = urn.split(":")[-1]
    if urn.startswith("urn:globus:auth:identity:"):
        return f"User: {id}"
    elif urn.startswith("urn:globus:groups:id:"):
        return f"Group: {id}"
    return urn


def identity_to_user(field: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Given a list of dict entries, this function will attempt to
    """
    # get_identities will fail if there's no data, so short circuit
    if len(items) == 0:
        return items

    # Only do the conversion if the user is already logged in
    authzs = get_authorizers_for_scopes(["openid"], no_login=True)
    authorizer = authzs.get("openid")
    if authorizer is None:
        return items

    # Collect IDs from the List data
    creators: Dict[str, None] = collections.OrderedDict()
    for item in items:
        urn_id = item.get(field, "")
        id = urn_id.split(":")[-1]
        creators[id] = None

    # Get id -> username mapping
    ac = AuthClient(authorizer=authorizer)
    resp = ac.get_identities(ids=creators.keys())
    id_to_user = {i["id"]: i["username"] for i in resp.data["identities"]}

    # Update items in list
    for item in items:
        urn_id = item.get(field, "")
        id = urn_id.split(":")[-1]
        if id in id_to_user:
            item[field] = id_to_user[id]
    return items


class Field:
    """
    A generic class structure for transforming lists of data into a table. Each
    instance of this class represents a single field to pull from a data item.
    """

    def __init__(
        self,
        name: str,
        default: str,
        transformation: Optional[Callable[[str], str]] = None,
        min_width: Optional[int] = None,
        max_width: Optional[int] = None,
    ) -> None:
        """
        name: The name of the field which contains the data for display
        default: A placeholder to use if the field is not available
        transformation: A callable that takes and returns a string. This is used
            to format the data field in an item
        """
        self.name = name
        self.default = default
        self.transformation = transformation
        self.min_width = min_width
        self.max_width = max_width


class DisplayFields(abc.ABC):
    """
    An object representing how to parse lists of data into a table.

    fields: A list of Fields that defines which fields get rendered into a table
        and how they are presented
    path_to_data_list: A key under which the data list is defined
    """

    fields: List[Field]
    path_to_data_list: str
    prehook: Optional[Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]]] = None


class RunListDisplayFields(DisplayFields):
    """
    This object defines the fields and display style of a Run listing into a
    table.
    """

    fields = [
        Field("action_id", "", min_width=_uuid_min_width),
        Field("label", "<EMPTY>"),
        Field("status", ""),
        Field("start_time", "", humanize_datetimes),
        Field("created_by", "", humanize_auth_urn),
        Field("flow_id", "<DELETED>"),
    ]
    path_to_data_list = "runs"
    prehook = functools.partial(identity_to_user, "created_by")


class FlowListDisplayFields(DisplayFields):
    """
    This object defines the fields and display style of a Flow listing into a
    table.
    """

    fields = [
        Field("title", "", max_width=_title_max_width),
        Field("id", "", min_width=_uuid_min_width),
        Field("flow_owner", "", humanize_auth_urn),
        # Field("created_at", "", humanize_datetimes),
        # Field("updated_at", "", humanize_datetimes),
    ]
    path_to_data_list = "flows"
    prehook = functools.partial(identity_to_user, "flow_owner")


class RunLogDisplayFields(DisplayFields):
    """
    This object defines the fields and display style of a Run log listing into a
    table.
    """

    fields = [
        Field("code", ""),
        Field("description", ""),
        Field("time", "", humanize_datetimes),
    ]
    path_to_data_list = "entries"


class CompletionDetector(abc.ABC):
    """
    An object that can be used to determine if an operation is complete or if it
    should continue polling.
    """

    terminals: Set[str]

    @classmethod
    @abc.abstractmethod
    def is_complete(cls, result: Union[GlobusHTTPResponse, GlobusAPIError]) -> bool:
        """
        Given either a GloubsHTTPReponse or GlobusAPIError, this method should
        return a boolean indicating if polling should continue.
        """
        pass


class ActionCompletionDetector(CompletionDetector):
    """
    This class determines when a Run has reached a completed state.
    """

    terminals: Set[str] = {"SUCCEEDED", "FAILED"}

    @classmethod
    def is_complete(cls, result: Union[GlobusHTTPResponse, GlobusAPIError]) -> bool:
        return (
            isinstance(result, GlobusAPIError)
            or result.data.get("status", None) in cls.terminals
        )


class LogCompletionDetector(CompletionDetector):
    """
    This class determines when a Run has reached a completed state from
    inspecting its logs.
    """

    terminals: Set[str] = {"FlowSucceeded", "FlowFailed", "FlowCanceled"}

    @classmethod
    def is_complete(cls, result: Union[GlobusHTTPResponse, GlobusAPIError]) -> bool:
        return isinstance(result, GlobusAPIError) or any(
            entry["code"] in cls.terminals for entry in result.data["entries"]
        )


class Result:
    """
    A class which wraps a Globus API response.
    """

    def __init__(
        self,
        response: Union[GlobusHTTPResponse, GlobusAPIError, str],
        detector: Type[CompletionDetector] = ActionCompletionDetector,
    ):
        self.result = response
        self.detector = detector

        self.is_api_error = isinstance(response, GlobusAPIError)
        self.data: Union[str, Dict[str, Any]]
        if isinstance(response, str):
            self.data = {"result": response}
        elif isinstance(response, GlobusAPIError):
            self.data = response.raw_json if response.raw_json else response.raw_text
        else:
            self.data = response.data

    @property
    def details(self) -> str:
        return get_http_details(self.result)

    @property
    def completed(self) -> bool:
        return isinstance(self.result, str) or self.detector.is_complete(self.result)

    def as_json(self) -> str:
        return json.dumps(self.data, indent=2).strip()

    def as_yaml(self) -> str:
        return yaml.dump(self.data, indent=2).strip()


class Renderer:
    """
    A class which understands how to render itself as json, yaml or a table and
    under which cirsumstances to use rich rendering. It's important that not
    every output be rendered using rich because JSON parsing tools cannot parse
    rich objects.
    """

    def __init__(
        self,
        result: Result,
        *,
        verbose: bool = False,
        watching: bool = False,
        format: Literal["json", "yaml", "table"] = "json",
        fields: Optional[Type[DisplayFields]] = None,
        run_once: bool = False,
    ):
        self.result = result
        self.verbose = verbose
        self.watching = watching
        self.run_once = run_once
        self.format = format
        self.fields = fields
        self.table_style = "orange1"
        self.detail_style = "cyan"
        self.success_style = "green"
        self.fail_style = "red"
        self.spinner = Spinner("simpleDotsScrolling")

        if format == "table":
            assert fields is not None

    @property
    def will_update(self) -> bool:
        return self.watching and not self.result.completed and not self.run_once

    @property
    def use_rich_rendering(self) -> bool:
        return self.watching or self.format == "table"

    @property
    def result_style(self) -> str:
        if self.result.is_api_error:
            return self.fail_style
        return self.success_style

    @property
    def details_as_text(self) -> Text:
        return Text(self.result.details, style=self.detail_style)

    @property
    def details_as_str(self) -> str:
        return self.details_as_text.plain

    @property
    def result_as_text(self) -> Text:
        if self.result.is_api_error:
            style = self.fail_style
        else:
            style = self.success_style

        if self.format == "yaml":
            return Text(self.result.as_yaml(), style)
        return Text(self.result.as_json(), style)

    @property
    def result_as_renderable(self) -> RenderableType:
        if self.format != "table" or self.result.is_api_error:
            return self.result_as_text

        assert self.fields is not None
        table = Table()
        for f in self.fields.fields:
            table.add_column(
                f.name,
                style=self.table_style,
                min_width=f.min_width,
                max_width=f.max_width,
            )

        list_of_data: List[Dict[str, Any]] = cast(dict, self.result.data).get(
            self.fields.path_to_data_list,
            [],
        )
        if self.fields.prehook:
            list_of_data = self.fields.prehook(list_of_data)
        for d in list_of_data:
            row_values = []
            for f in self.fields.fields:
                value = d.get(f.name, f.default)
                if f.transformation:
                    value = f.transformation(value)
                row_values.append(value)
            table.add_row(*row_values)
        return table

    @property
    def result_as_str(self) -> str:
        return self.result_as_text.plain

    def render(self):
        """
        Determine how and what to render to the console. If not using rich
        rendering, all output is handled by typer, allowing outside tools such
        as JQ to parse the results.
        """
        if self.use_rich_rendering:
            renderables: List[RenderableType] = []
            if self.verbose:
                d = self.details_as_text
                renderables.append(d)
            r = self.result_as_renderable
            renderables.append(r)
            if self.will_update:
                s = self.spinner
                renderables.append(s)

            cli_content.rg = Group(*renderables)
        else:
            if self.verbose:
                typer.secho(self.details_as_str, fg=self.detail_style, err=True)
            typer.secho(self.result_as_str, fg=self.result_style, nl=True)


class RequestRunner:
    """
    A utility class for encapsulating logic around repeated requests, error
    handling, and output formatting. In general, run_and_render should be the
    interface into instances. But for fine grain control on execution and
    rendering, the individual methods may be called.
    """

    def __init__(
        self,
        callable: Callable[[], GlobusHTTPResponse],
        *,
        format: OutputFormat = OutputFormat.json,
        verbose: bool = False,
        watch: bool = False,
        run_once: bool = False,
        fields: Optional[Type[DisplayFields]] = None,
        detector: Type[CompletionDetector] = ActionCompletionDetector,
    ):
        self.callable = callable
        self.format = format
        self.verbose = verbose
        self.watch = watch
        self.fields = fields
        self.run_once = run_once
        self.detector = detector

    def run(self) -> Result:
        result: Union[GlobusHTTPResponse, GlobusAPIError]
        try:
            result = self.callable()
        except GlobusAPIError as err:
            result = err
        return Result(result, detector=self.detector)

    def render(self, result: Result):
        Renderer(
            result,
            verbose=self.verbose,
            watching=self.watch,
            format=self.format,
            fields=self.fields,
            run_once=self.run_once,
        ).render()

    def render_as_result(
        self,
        d: Dict[str, Any],
        client: BaseClient,
        status_code: int = 200,
    ):
        resp = Response()
        resp.status_code = status_code
        resp._content = json.dumps(d).encode("utf-8")
        resp.headers.update({"Content-Type": "application/json"})
        globus_resp = GlobusHTTPResponse(resp, client=client)
        self.render(Result(globus_resp))

    def run_and_render(self) -> Result:
        result = self.run()

        # It's assumed that no additional auth URL's will need to be written to STDOUT
        # because of the successful call to `self.run()`, above.
        with live_content:
            while True:
                self.render(result)
                if not self.watch or self.run_once or result.completed:
                    return result
                sleep(2)
                result = self.run()
