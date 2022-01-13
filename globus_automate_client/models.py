import datetime
import enum
import typing as t

import typing_extensions as te
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Extra,
    Field,
    StrictBool,
    ValidationError as FlowValidationError,
    root_validator,
    validator,
)

FlowValidationError


def enforce_jsonpath(v: t.Optional[str]) -> t.Optional[str]:
    if v is not None and not v.startswith("$."):
        raise ValueError(f'"{v}" must be a JSONPath and start with "$."')
    return v


def check_jsonpath_syntax_in_dict(item: t.Optional[dict]) -> t.Optional[dict]:
    if item is None:
        return item

    for k, v in item.items():
        if k.endswith(".$") and (not isinstance(v, str) or not v.startswith("$.")):
            raise ValueError(
                f'Key "{k}" indicates its value will be a JSONPath, however its value "{v}" is not a JSONPath'
            )
        elif isinstance(v, dict):
            check_jsonpath_syntax_in_dict(v)
    return item


class StateType(str, enum.Enum):
    Pass = "Pass"
    Action = "Action"
    Wait = "Wait"
    Choice = "Choice"
    ExpressionEval = "ExpressionEval"
    Fail = "Fail"


class Catchers(BaseModel):
    ErrorEquals: t.List[str] = Field(..., min_items=1)
    Next: str
    ResultPath: t.Optional[str]

    class Config:
        extra = Extra.forbid

    _enforce_jsonpath = validator("ResultPath", allow_reuse=True)(enforce_jsonpath)


class DataTestExpression(BaseModel):
    Variable: str
    StringEquals: t.Optional[str]
    StringEqualsPath: t.Optional[str]
    StringLessThan: t.Optional[str]
    StringLessThanPath: t.Optional[str]
    StringGreaterThan: t.Optional[str]
    StringGreaterThanPath: t.Optional[str]
    StringLessThanEquals: t.Optional[str]
    StringLessThanEqualsPath: t.Optional[str]
    StringGreaterThanEquals: t.Optional[str]
    StringGreaterThanEqualsPath: t.Optional[str]
    StringMatches: t.Optional[str]
    NumericEquals: t.Optional[str]
    NumericEqualsPath: t.Optional[str]
    NumericLessThan: t.Optional[str]
    NumericLessThanPath: t.Optional[str]
    NumericGreaterThan: t.Optional[str]
    NumericGreaterThanPath: t.Optional[str]
    NumericLessThanEquals: t.Optional[str]
    NumericLessThanEqualsPath: t.Optional[str]
    NumericGreaterThanEquals: t.Optional[str]
    NumericGreaterThanEqualsPath: t.Optional[str]
    BooleanEquals: t.Optional[StrictBool]
    BooleanEqualsPath: t.Optional[str]
    TimestampEquals: t.Optional[str]
    TimestampEqualsPath: t.Optional[str]
    TimestampLessThan: t.Optional[str]
    TimestampLessThanPath: t.Optional[str]
    TimestampGreaterThan: t.Optional[str]
    TimestampGreaterThanPath: t.Optional[str]
    TimestampLessThanEquals: t.Optional[str]
    TimestampLessThanEqualsPath: t.Optional[str]
    TimestampGreaterThanEquals: t.Optional[str]
    TimestampGreaterThanEqualsPath: t.Optional[str]
    IsNull: t.Optional[StrictBool]
    IsPresent: t.Optional[StrictBool]
    IsNumeric: t.Optional[StrictBool]
    IsString: t.Optional[StrictBool]
    IsBoolean: t.Optional[StrictBool]
    IsTimestamp: t.Optional[StrictBool]

    class Config:
        extra = Extra.forbid

    _enforce_jsonpath = validator(
        "Variable",
        "StringEqualsPath",
        "StringLessThanPath",
        "StringGreaterThanPath",
        "StringLessThanEqualsPath",
        "StringGreaterThanEqualsPath",
        "NumericEqualsPath",
        "NumericLessThanPath",
        "NumericGreaterThanPath",
        "NumericLessThanEqualsPath",
        "NumericGreaterThanEqualsPath",
        "BooleanEqualsPath",
        "TimestampEqualsPath",
        "TimestampLessThanPath",
        "TimestampGreaterThanPath",
        "TimestampLessThanEqualsPath",
        "TimestampGreaterThanEqualsPath",
        allow_reuse=True,
    )(enforce_jsonpath)

    @root_validator(skip_on_failure=True)
    def validate_only_one_rule_is_set(cls, values):
        set_fields = {
            k
            for k, v in values.items()
            if k not in {"Variable", "Next"} and v is not None
        }
        if len(set_fields) != 1:
            raise ValueError(
                f'A "ChoiceRule" may only contain one expression. Found {", ".join(set_fields)}'
            )
        return values


class DataTestExpressionWithTransitions(DataTestExpression):
    Next: str


class BooleanExpression(BaseModel):
    And: t.Optional[t.List[t.Union[DataTestExpression, "BooleanExpression"]]] = Field(
        None, min_items=1
    )
    Or: t.Optional[t.List[t.Union[DataTestExpression, "BooleanExpression"]]] = Field(
        None, min_items=1
    )
    Not: t.Optional[t.Union[DataTestExpression, "BooleanExpression"]] = None

    class Config:
        extra = Extra.forbid

    @root_validator(skip_on_failure=True)
    def validate_only_one_boolean_choice_rule_set(cls, values):
        set_fields = {
            k for k, v in values.items() if k not in {"Next"} and v is not None
        }
        if len(set_fields) != 1:
            raise ValueError(
                'Exactly one of "And", "Or", or "Not" must be specified in a BooleanExpression'
            )
        return values


class BooleanExpressionWithTransitions(BooleanExpression):
    """
    A Boolean Expression is a JSON object which contains a field named "And",
    "Or", or "Not". If the field name is "And" or "Or", the value MUST be an
    non-empty object array of Choice Rules, which MUST NOT contain "Next"
    fields; the interpreter processes the array elements in order, performing
    the boolean evaluations in the expected fashion, ceasing array processing
    when the boolean value has been unambiguously determined.

    The value of a Boolean Expression containing a "Not" field MUST be a single
    Choice Rule, that MUST NOT contain a "Next" field; it returns the inverse
    of the boolean to which the Choice Rule evaluates.
    """

    Next: str


class ChoiceState(BaseModel):
    Type: te.Literal[StateType.Choice]
    Comment: t.Optional[str] = None
    Choices: t.List[
        t.Union[BooleanExpressionWithTransitions, DataTestExpressionWithTransitions]
    ] = Field(..., min_items=1)
    Default: t.Optional[str]

    class Config:
        extra = Extra.forbid


class NextOrEndState(BaseModel):
    Next: t.Optional[str] = None
    End: StrictBool = False

    @root_validator
    def validate_mutually_exclusive_fields(cls, values):
        if values.get("Next") and values.get("End"):
            raise ValueError('"Next" and "End" are mutually exclusive')
        if values.get("Next") is None and not values.get("End", False):
            raise ValueError('Either "Next" or "End" are required')
        return values


class ActionState(NextOrEndState):
    Type: te.Literal[StateType.Action]
    Comment: t.Optional[str] = None
    ActionUrl: AnyHttpUrl
    ActionScope: t.Optional[str] = None
    Parameters: t.Optional[t.Dict[str, t.Any]] = None
    RunAs: str = "User"
    ExceptionOnActionFailure: StrictBool = True
    Catch: t.Optional[t.List[Catchers]] = None
    WaitTime: int = 300
    InputPath: t.Optional[str] = None
    ResultPath: t.Optional[str] = None

    class Config:
        extra = Extra.forbid

    _enforce_jsonpath = validator("InputPath", "ResultPath", allow_reuse=True)(
        enforce_jsonpath
    )
    _check_jsonpath_syntax_in_dict = validator("Parameters", allow_reuse=True)(
        check_jsonpath_syntax_in_dict
    )

    @root_validator
    def validate_mutually_exclusive_fields(cls, values):
        fields = ["InputPath", "Parameters"]
        set_fields = {f: values.get(f) for f in fields if values.get(f) is not None}
        if len(set_fields) > 1:
            raise ValueError(
                f"Only one of these fields may be set: {set_fields.keys()}"
            )
        if len(set_fields) == 0:
            raise ValueError(f"At least one field must be set: {fields}")

        return values


class ExpressionEvalState(NextOrEndState):
    Type: te.Literal[StateType.ExpressionEval]
    Comment: t.Optional[str] = None
    Parameters: t.Optional[dict] = None
    ResultPath: t.Optional[str] = None

    class Config:
        extra = Extra.forbid

    _enforce_jsonpath = validator("ResultPath", allow_reuse=True)(enforce_jsonpath)
    _check_jsonpath_syntax_in_dict = validator("Parameters", allow_reuse=True)(
        check_jsonpath_syntax_in_dict
    )


class FailState(BaseModel):
    Type: te.Literal[StateType.Fail]
    Comment: t.Optional[str] = None
    Cause: t.Optional[str] = None
    Error: t.Optional[str] = None

    class Config:
        extra = Extra.forbid


class PassState(NextOrEndState):
    Type: te.Literal[StateType.Pass]
    Comment: t.Optional[str] = None
    Parameters: t.Optional[t.Dict[str, t.Any]] = None
    InputPath: t.Optional[str] = None
    Result: t.Optional[dict] = None
    ResultPath: t.Optional[str] = None
    # Not supported by Flows
    # OutputPath: t.Optional[str] = None

    class Config:
        extra = Extra.forbid

    _enforce_jsonpath = validator(
        "InputPath", "Result", "ResultPath", allow_reuse=True
    )(enforce_jsonpath)
    _check_jsonpath_syntax_in_dict = validator("Parameters", allow_reuse=True)(
        check_jsonpath_syntax_in_dict
    )


class WaitState(NextOrEndState):
    Type: te.Literal[StateType.Wait]
    Comment: t.Optional[str] = None
    InputPath: t.Optional[str] = None
    OutputPath: t.Optional[str] = None
    Seconds: t.Optional[int] = None
    Timestamp: t.Optional[datetime.datetime] = None
    SecondsPath: t.Optional[str] = None
    TimestampPath: t.Optional[str] = None

    _enforce_jsonpath = validator(
        "InputPath", "OutputPath", "SecondsPath", "TimestampPath", allow_reuse=True
    )(enforce_jsonpath)

    class Config:
        extra = Extra.forbid

    @root_validator(skip_on_failure=True)
    def validate_mutually_exclusive_fields(cls, values):
        fields = ["Seconds", "Timestamp", "SecondsPath", "TimestampPath"]
        set_fields = {f: values.get(f) for f in fields if values.get(f) is not None}
        if len(set_fields) > 1:
            raise ValueError(
                f"Only one of these fields may be set: {set_fields.keys()}"
            )
        if len(set_fields) == 0:
            raise ValueError(f"At least one field must be set: {fields}")

        return values


FlowState = te.Annotated[
    t.Union[
        PassState, WaitState, ActionState, FailState, ChoiceState, ExpressionEvalState
    ],
    Field(discriminator="Type"),
]


class FlowDefinition(BaseModel):
    StartAt: str
    States: t.Dict[str, FlowState]
    Comment: t.Optional[str]

    class Config:
        extra = Extra.forbid

    @validator("States")
    def validate_states(cls, v):
        if len(v) < 1:
            raise ValueError('At least one "State" is required')

        invalid_state_names = [
            state_name
            for state_name in v.keys()
            if len(state_name) > 128 or len(state_name) == 0
        ]
        if invalid_state_names:
            raise ValueError(
                f"The following states have invalid names: {', '.join(invalid_state_names)}"
            )
        return v

    @root_validator(skip_on_failure=True)
    def validate_start_at_is_a_state(cls, values):
        states, start_at = values.get("States", {}), values.get("StartAt", "")
        if start_at not in states:
            raise ValueError(f'StartAt state "{start_at}" is not defined in States')
        return values

    @root_validator(skip_on_failure=True)
    def validate_all_transition_states_exist(cls, values):
        states = values.get("States", {})
        defined_states = set(states.keys())
        referenced_states = {values["StartAt"]}

        for state in states.values():
            if state.Type not in {StateType.Choice, StateType.Fail}:
                # Ensure that all state's with a Next property have a valid transition
                next_state = state.Next
                if next_state is not None:
                    referenced_states.add(next_state)

            # Ensure that the Catch conditions in an Action state refer to a
            # valid transition
            if state.Type == StateType.Action:
                if state.Catch:
                    for catcher in state.Catch:
                        referenced_states.add(catcher.Next)

            # Ensure that the choice state rules have valid transitions
            elif state.Type == StateType.Choice:
                if state.Default:
                    referenced_states.add(state.Default)
                for choice in state.Choices:
                    referenced_states.add(choice.Next)

        undefined_states = referenced_states - defined_states
        unreferenced_states = defined_states - referenced_states
        if undefined_states:
            raise ValueError(
                f'Flow definition contained a reference to unknown state(s): {", ".join(undefined_states)}'
            )
        if unreferenced_states:
            raise ValueError(
                f'Flow definition contained unreachable state(s): {", ".join(unreferenced_states)}'
            )

        return values
