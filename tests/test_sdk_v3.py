from typing import Iterable

import pytest

import globus_automate_client
from globus_automate_client.cli.constants import (
    ActionRole,
    ActionRoleAllNames,
    ActionRoleDeprecated,
    FlowRole,
    FlowRoleAllNames,
    FlowRoleDeprecated,
)


def test_import():
    assert bool(globus_automate_client)


@pytest.mark.parametrize(
    "combo, supported, deprecated",
    (
        (ActionRoleAllNames, ActionRole, ActionRoleDeprecated),
        (FlowRoleAllNames, FlowRole, FlowRoleDeprecated),
    ),
)
def test_role_name_compilations(
    combo: Iterable,
    supported: Iterable,
    deprecated: Iterable,
):
    """Ensure combination role name enums are perfect copies."""

    combo_names = {i.value for i in combo}
    supported_names = {i.value for i in supported}
    deprecated_names = {i.value for i in deprecated}

    assert combo_names == supported_names | deprecated_names
