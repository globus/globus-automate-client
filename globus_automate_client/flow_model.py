import json
import uuid
from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from jsonschema import Draft7Validator
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    ValidationError,
    root_validator,
    validator,
)


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


def validate_against_schema(
    schema: Union[Draft7Validator, Mapping[str, Any]],
    input_to_validate: Mapping[str, Any],
) -> List[str]:
    if not isinstance(schema, Draft7Validator):
        schema = Draft7Validator(schema)
    errors = schema.iter_errors(input_to_validate)
    error_list = []
    for error in errors:
        if error.path:
            # Elements of the error path may be integers or other non-string types,
            # but we need strings for use with join()
            error_path_for_message = ".".join([str(x) for x in error.path])
            error_message = f"'{error_path_for_message}' invalid due to {error.message}"
        else:
            error_message = error.message
        error_list.append(error_message)
    return error_list


T = TypeVar("T", bound="DeserializerMixin")


class GlobusValidationException(Exception):
    pass


class DeserializerMixin(ABC):
    @classmethod
    def from_dict(cls: Type[T], in_dict: Dict[str, Any]) -> T:
        try:
            o = cls(**in_dict)
            return o
        except ValidationError as ve:
            for error in ve.errors():
                loc: Tuple[str] = error.get("loc", ("Unknown",))
                try:
                    states_index = loc.index("States")
                    prefix = f"In State {loc[states_index + 1]}:"
                except (ValueError, IndexError):
                    prefix = f"At location {'/'.join(loc)}:"
                msg = prefix + error.get("msg", "Unknown error")
                raise GlobusValidationException(msg)

    @classmethod
    def from_json(cls: Type[T], json_string: str) -> T:
        d = json.loads(json_string)
        return cls.from_dict(d)


class PrincipalUrnList(BaseModel):
    __root__: List[str]

    @staticmethod
    def validate_principal_urns_or_other_values(
        values, other_allowed_values: Optional[Set[str]] = None
    ):
        # TODO check that all values are either in principal URN format or in the
        # other_allowed_values list
        return values

    @root_validator
    def validate_principal_urns(cls, values):
        return PrincipalUrnList.validate_principal_urns_or_other_values(values)


class RunnableByList(PrincipalUrnList):
    @root_validator
    def validate_principal_list(cls, values):
        return PrincipalUrnList.validate_principal_urns_or_other_values(
            values, other_allowed_values={"all_authenticated_users"}
        )


class VisibleToList(PrincipalUrnList):
    @root_validator
    def validate_principal_list(cls, values):
        return PrincipalUrnList.validate_principal_urns_or_other_values(
            values, other_allowed_values={"public"}
        )


class StateReferencing(ABC):
    @abstractmethod
    def referenced_states(self) -> Set[str]:
        ...


class NextOrEnd(BaseModel, StateReferencing):
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

    def referenced_states(self) -> Set[str]:
        return {self.Next} if self.Next is not None else set()


class ParametersOrInputPath(BaseModel):
    Parameters: Optional[Dict[str, Any]]
    InputPath: Optional[str]

    @root_validator
    def validate_parameters_or_inputpath(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if values.get("Parameters") is not None and values.get("InputPath") is not None:
            raise AssertionError(
                "Only one of 'Parameters' and 'InputPath' may be specified."
            )
        return values

    @validator("InputPath")
    def validate_inputpath_is_jsonpath(cls, input_path: str):
        if not ensure_has_json_path_val(input_path):
            raise ValueError(
                f"InputPath value '{input_path}' must be a JSONPath value, starting with '$.'"
            )

    @validator("Parameters")
    def validate_parameters(cls, parameters: Dict[str, Any]) -> Dict[str, Any]:
        errors: List[str] = []
        for param_name, val in parameters.items():
            if param_name.endswith(".$") and not ensure_has_json_path_val(val):
                errors.append(
                    f"Parameters key named {param_name} doesn't contain a JSONPath "
                    f"Value (which must start with the prefix '$.')"
                )
            elif param_name.endswith(".="):
                # Can we validate the expression? Perhaps pass the string to simpleeval
                # with none or dummy value dictionary and at least see if it catches
                # syntax errors.
                pass
        if len(errors) > 0:
            raise AssertionError("; ".join(errors))
        return parameters


class FlowState(BaseModel):
    Comment: Optional[str]


class ResultPathModel(BaseModel):
    ResultPath: Optional[str]

    @validator("ResultPath")
    def result_path_validator(cls, result_path):
        if result_path is not None:
            if not ensure_has_json_path_val(result_path):
                raise ValueError(
                    "'ResultPath' must be a JSONPath value "
                    "(which must start with the prefix '$.')"
                )
        return result_path


class ActionCatch(ResultPathModel):
    ErrorEquals: Set[str]
    Next: str


class ActionState(FlowState, NextOrEnd, ParametersOrInputPath, ResultPathModel):
    Type: Literal["Action"]
    ActionUrl: HttpUrl
    ActionScope: Optional[str]
    RunAs: str
    ExceptionOnActionFailure: bool = False
    WaitTime: int = 300
    Catch: Optional[List[ActionCatch]]

    @validator("Catch")
    def catch_validator(
        cls, catch_list: Optional[List[ActionCatch]]
    ) -> Optional[List[ActionCatch]]:
        if catch_list is not None:
            seen_error_types: Set[str] = set()
            re_seen_error_types: Set[str] = set()
            for catch in catch_list:
                this_reseen = seen_error_types.intersection(catch.ErrorEquals)
                re_seen_error_types.update(this_reseen)
                seen_error_types.update(catch.ErrorEquals)
            if len(re_seen_error_types) > 0:
                raise ValueError(
                    f"The values {re_seen_error_types} occur more than "
                    "once in the ErrorEquals list of the Catch."
                )
        return catch_list


class PassState(FlowState, NextOrEnd, ParametersOrInputPath, ResultPathModel):
    Type: Literal["Pass"]


class ExpressionEvalState(FlowState, NextOrEnd, ResultPathModel):
    Type: Literal["ExpressionEval"]
    Parameters: Dict[str, Any]

    @validator("Parameters")
    def validate_parameters(cls, parameters: Dict[str, Any]) -> Dict[str, Any]:
        return ParametersOrInputPath.validate_parameters(parameters)


class FailState(FlowState):
    Type: Literal["Fail"]
    Error: str
    Cause: str


AllStateTypesUnion = Union[ActionState, PassState, ExpressionEvalState, FailState]


class FlowStateDescriminator(BaseModel):
    __root__: AllStateTypesUnion = Field(..., discriminator="Type")

    @property
    def state(self) -> FlowState:
        return self.__root__


class FlowDefinition(BaseModel, DeserializerMixin):
    StartAt: str
    Comment: Optional[str]
    States: Dict[str, FlowStateDescriminator]

    @validator("States")
    def validate_state_references(
        cls, states: Dict[str, FlowStateDescriminator], values: Dict[str, Any]
    ) -> Dict[str, FlowStateDescriminator]:
        defined_states = set(states.keys())
        referenced_states = {values.get("StartAt")}
        missing_references: Dict[str, Set[str]] = {}
        for state_name, flow_state_descrim in states.items():
            flow_state = flow_state_descrim.state
            if isinstance(flow_state, StateReferencing):
                references = flow_state.referenced_states()
                referenced_states.update(references)
                undefined_states = references - defined_states
                if len(undefined_states) > 0:
                    missing_references[state_name] = undefined_states

        errors: List[str] = []
        unreferenced_states = defined_states - referenced_states
        if len(unreferenced_states) > 0:
            errors.append(
                f"The following states are defined by the Flow but never referenced: {unreferenced_states}"
            )

        if len(missing_references) > 0:
            errors.append(
                "; ".join(
                    [
                        f"State(s) {v} referenced in State '{k}' not defined"
                        for k, v in missing_references.items()
                    ]
                )
            )

        if len(errors) > 0:
            raise ValueError("; ".join(errors))
        return states


class Flow(BaseModel, DeserializerMixin):
    # TODO: Add length and other constraints to these fields
    title: str
    subtitle: Optional[str]
    description: Optional[str]
    keywords: Optional[List[str]]
    subscription_id: Optional[uuid.UUID]
    definition: FlowDefinition
    input_schema: Dict[str, Any]
    # TODO: Make the next two act as aliases
    visible_to: Optional[VisibleToList]
    flow_viewers: Optional[VisibleToList]
    # TODO: Make the next two act as aliases
    runnable_by: Optional[RunnableByList]
    flow_starters: Optional[RunnableByList]
    flow_administrators: Optional[RunnableByList]

    @validator("input_schema")
    def validate_input_schema(cls, input_schema: Dict[str, Any]) -> Dict[str, Any]:
        # Use the JSONSchema implementation to validate that the InputSchema is a
        # valid JSONSchema
        schema_error_messages = validate_against_schema(
            Draft7Validator.META_SCHEMA, api_input["input_schema"]
        )
        if len(schema_error_messages) > 0:
            raise AssertionError(
                f"InputSchema is invalid: {'; '.join(schema_error_messages)}"
            )
        return input_schema
