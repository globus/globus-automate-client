import glob
import os

import pytest
import yaml

from globus_automate_client.models import FlowDefinition


@pytest.mark.parametrize("filename", glob.glob("./examples/flows/*/definition*"))
def test_example_flow(filename: str):
    with open(os.path.join(os.getcwd(), filename), "r") as f:
        flow_def = yaml.safe_load(f)
        FlowDefinition(**flow_def).json(indent=2)
