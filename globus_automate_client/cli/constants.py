import enum
import functools
import json

import typer
import yaml
from globus_sdk import GlobusHTTPResponse

from globus_automate_client.graphviz_rendering import (
    graphviz_format,
    state_colors_for_log,
)


class InputFormat(str, enum.Enum):
    json = "json"
    yaml = "yaml"

    def get_dumper(self):
        if self is self.json:
            return json.dumps
        elif self is self.yaml:
            return yaml.dump


class OutputFormat(str, enum.Enum):
    json = "json"
    yaml = "yaml"

    def get_dumper(self):
        if self is self.yaml:
            return functools.partial(yaml.dump, indent=2)
        return functools.partial(json.dumps, indent=2)


class FlowDisplayFormat(str, enum.Enum):
    json = "json"
    graphviz = "graphviz"
    image = "image"
    yaml = "yaml"

    def get_dumper(self):
        if self is self.yaml:
            return functools.partial(yaml.dump, indent=2)
        if self is self.graphviz:
            return graphviz_text
        if self is self.image:
            return graphviz_image
        return functools.partial(json.dumps, indent=2)


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
