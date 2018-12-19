# Authoring Flows for the Globus Flows Service

The Globus Flows Service provides users with the ability to easily define compositions, Flows, of a numerous Actions to perform a single, logical operation. Flows may be invoked as other Actions, potentially running for a long time with an API for monitoring the progress of the flow instance during its lifetime. Definition of such Flows requires an easy to read, author, and potentially visualize method of defining the Flows. For this purpose, the Flows service starts from the core of the [Amazon States Language](https://states-language.net/spec.html). We start with a conservative approach to using the Amazon States Language adopting a minimal subset of its capability and functionality with the intent of building out compatibility with more aspects of the entire language specification as we validate and become familiar with its usage in the context of the Flows service.

The [States Language Specification](https://states-language.net/spec.html) describes its capabilities in terms of State Types and Allowed Fields as summarized in [this table](https://states-language.net/spec.html#state-type-table). The Globus Flows system starts with a minimal subset of this table as follows:

|States |Pass|Action|
|---|----|------|
|Type|Required|Required|
|Comment|Allowed|Allowed|
|InputPath|Allowed|Allowed|
|OutputPath|Disallowed|Disallowed|
|Parameters|Disallowed|Disallowed|
|ResultPath|Allowed|Allowed|
|_One of_: Next or "End": true|Required|Required|
|Retry, Catch|Disallowed|Allowed|

The only two states are Pass, which behaves as in the States Language, and Action which is a newly defined state (described below) for invoking Actions. The important changes in the field types are that `OutputPath` and `Parameters` are disallowed. In the case of `OutputPath` it can be destructive of much of the state of the flow, and may interfere with internal state used to track system information maintained within the flow. Parameters is a relatively new addition to the state language specification, and it is anticipated that support will be added. All of the additional state types: `Choice`, `Wait`, `Succeed`, `Fail` and `Parallel` are being evaluated for support. The `Task` state ties closely to Amazon AWS resources so likely will not be supported. The `Action` state replaces its functionality.

The Action state is used for invoking Actions as part of a flow. It introduces new field types as described below:

|Field Name|Required/Allowed|Description|
|----------|----------------|-----------|
|ActionUrl|Required|The **base** URL for invoking the Action (without operation suffixes such as `/run`)|
|ActionScope|Required|The scope string to be used when interacting with the Action|
|WaitTime|Allowed|The (minimum) time, in seconds, to wait for the invoked Action to reach a completed state. If not provided, a default time of 60 seconds is used.|

Should the Action not complete by the end of the `WaitTime` value, an Error condition will be raised, and it may be handled using a `Catch` field.

The States Language continues to provide a strong foundation for a
powerful set of operations for complex, asynchronous flows and will
allow us to grow to support these same capabilities in the Globus Flows service.


