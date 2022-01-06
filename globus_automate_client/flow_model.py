import uuid
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator


def ensure_has_json_path_val(val: Any) -> bool:
    if isinstance(val, str):
        return val.startswith("$.")
    elif isinstance(val, dict):
        for k, v in val.items():
            if ensure_has_json_path_val(v):
                return True
    elif isinstance(val, (list, tuple, set)):
        for list_val in val:
            if ensure_has_json_path_val(list_val):
                return True
    return False


class PrincipalUrnList(BaseModel):
    __root__: List[str]


class RunnableByList(PrincipalUrnList):
    pass


class VisibleToList(PrincipalUrnList):
    pass


class NextOrEnd(BaseModel):
    Next: Optional[str]
    End: Optional[bool]

    @root_validator
    def validate_next_or_end(cls, values):
        if values["Next"] is None and values["End"] is None:
            raise AssertionError("At least one of 'Next' or 'End' must be specified")
        if values["Next"] is not None and values["End"] is True:
            raise AssertionError(
                "Cannot have a value for 'Next' and a value for 'End' of true"
            )
        return values


class StateParameters(BaseModel):
    __root__: Dict[str, Any]

    @root_validator
    def validate_parameters(cls, values: Dict[str, Any]):
        errors: List[str] = []
        for param_name, val in values.items():
            if param_name.endswith(".$") and not ensure_has_json_path_val(val):
                errors.append(
                    f"Parameters key named {param_name} doesn't contain a JSONPath "
                    f"Value (which must start with the prefix '$.')"
                )
        if len(errors) > 0:
            raise AssertionError("; ".join(errors))


class FlowState(BaseModel):
    Comment: Optional[str]


class ActionState(FlowState, NextOrEnd):
    Type: Literal["Action"]
    ActionUrl: str
    ActionScope: Optional[str]
    Parameters: Optional[StateParameters]


class PassState(FlowState, NextOrEnd):
    Type: Literal["Pass"]
    Parameters: Optional[StateParameters]


class FlowStateDescriminator(BaseModel):
    #    __root__: Union[ActionState, PassState] = Field(..., discriminator="Type")
    ...


class FlowDefinition(BaseModel):
    StartAt: str
    Comment: Optional[str]
    States: Dict[str, FlowStateDescriminator]


class Flow(BaseModel):
    title: str
    subtitle: Optional[str]
    descriptin: Optional[str]
    keywords: Optional[List[str]]
    subscription_id: Optional[uuid.UUID]
    definition: FlowDefinition
    input_schema: Dict[str, Any]
    visible_to: Optional[VisibleToList]
    flow_viewers: Optional[VisibleToList]
    runnable_by: Optional[RunnableByList]
    flow_starters: Optional[RunnableByList]
    flow_administrators: Optional[RunnableByList]
