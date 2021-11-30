import enum

import typer
from globus_sdk import GlobusHTTPResponse

from globus_automate_client.graphviz_rendering import (
    graphviz_format,
    state_colors_for_log,
)


class FlowRole(str, enum.Enum):
    flow_viewer = "flow_viewer"
    flow_starter = "flow_starter"
    flow_administrator = "flow_administrator"
    flow_owner = "flow_owner"


class FlowRoleDeprecated(str, enum.Enum):
    created_by = "created_by"
    visible_to = "visible_to"
    runnable_by = "runnable_by"
    administered_by = "administered_by"


class FlowRoleAllNames(str, enum.Enum):
    # Compile supported and deprecated names explicitly to satisfy mypy.
    flow_viewer = "flow_viewer"
    flow_starter = "flow_starter"
    flow_administrator = "flow_administrator"
    flow_owner = "flow_owner"

    # Deprecated
    created_by = "created_by"
    visible_to = "visible_to"
    runnable_by = "runnable_by"
    administered_by = "administered_by"


class ActionRole(str, enum.Enum):
    run_monitor = "run_monitor"
    run_manager = "run_manager"
    run_owner = "run_owner"


class ActionRoleDeprecated(str, enum.Enum):
    created_by = "created_by"
    monitor_by = "monitor_by"
    manage_by = "manage_by"


class ActionRoleAllNames(str, enum.Enum):
    # Compile supported and deprecated names explicitly to satisfy mypy.
    run_monitor = "run_monitor"
    run_manager = "run_manager"
    run_owner = "run_owner"

    # Deprecated
    created_by = "created_by"
    monitor_by = "monitor_by"
    manage_by = "manage_by"


class ActionStatus(str, enum.Enum):
    succeeded = "SUCCEEDED"
    failed = "FAILED"
    active = "ACTIVE"
    inactive = "INACTIVE"


class OutputFormat(str, enum.Enum):
    """
    This class defines the generally supported output formats
    """

    json = "json"
    yaml = "yaml"


class ListingOutputFormat(str, enum.Enum):
    """
    This class represents the different output formats for lists of data
    """

    json = "json"
    yaml = "yaml"
    table = "table"


class RunLogOutputFormat(str, enum.Enum):
    """
    This class represents the different formats in which a Run's logs may be
    displayed
    """

    json = "json"
    yaml = "yaml"
    table = "table"
    image = "image"
    graphiz = "graphiz"

    def visualize(self, flow_log: GlobusHTTPResponse, flow_def: GlobusHTTPResponse):
        if self == "image":
            self.graphviz_image(flow_log, flow_def)
        elif self == "graphiz":
            self.graphviz_text(flow_log, flow_def)

    def graphviz_text(self, flow_log: GlobusHTTPResponse, flow_def: GlobusHTTPResponse):
        graphviz_out = self._as_graphiz(flow_log, flow_def)
        typer.echo(graphviz_out.source)

    def graphviz_image(
        self, flow_log: GlobusHTTPResponse, flow_def: GlobusHTTPResponse
    ):
        graphviz_out = self._as_graphiz(flow_log, flow_def)
        graphviz_out.render("flows-output/graph", view=True, cleanup=True)

    def _as_graphiz(self, flow_log: GlobusHTTPResponse, flow_def: GlobusHTTPResponse):
        definition = flow_def.data["definition"]
        colors = state_colors_for_log(flow_log.data["entries"])
        return graphviz_format(definition, colors)


class ImageOutputFormat(str, enum.Enum):
    """
    This class represents the different ways of visualizing a Flow
    """

    json = "json"
    yaml = "yaml"
    image = "image"
    graphviz = "graphviz"

    def visualize(self, flow_dict):
        if self == "image":
            self.graphviz_image(flow_dict)
        elif self == "graphviz":
            self.graphviz_text(flow_dict)

    def graphviz_text(self, flow):
        graphviz_out = graphviz_format(flow, None)
        typer.echo(graphviz_out.source)

    def graphviz_image(self, flow):
        graphviz_out = graphviz_format(flow, None)
        graphviz_out.render("flows-output/graph", view=True, cleanup=True)


def graphviz_text(flow_log: GlobusHTTPResponse, flow_def: GlobusHTTPResponse):
    definition = flow_def.data["definition"]
    colors = state_colors_for_log(flow_log.data["entries"])
    graphviz_out = graphviz_format(definition, colors)
    typer.echo(graphviz_out.source)


def graphviz_image(flow_log: GlobusHTTPResponse, flow_def: GlobusHTTPResponse):
    definition = flow_def.data["definition"]
    colors = state_colors_for_log(flow_log.data["entries"])
    graphviz_out = graphviz_format(definition, colors)
    graphviz_out.render("flows-output/graph", view=True, cleanup=True)
