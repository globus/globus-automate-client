import enum
import json

import yaml


class InputFormat(str, enum.Enum):
    json = "json"
    yaml = "yaml"

    def get_dumper(self):
        if self is self.json:
            return json.dumps
        elif self is self.yaml:
            return yaml.dump
