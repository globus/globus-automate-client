import enum


class InputFormat(str, enum.Enum):
    json = "json"
    yaml = "yaml"
