import glob
import os

import pytest
import yaml

from globus_automate_client.models import FlowDefinition


@pytest.mark.parametrize("filename", glob.glob("./examples/flows/*/definition*"))
def test_example_flow(filename: str):
    with open(os.path.join(os.getcwd(), filename), "r") as f:
        flow_def_in = yaml.safe_load(f)
        flow_model = FlowDefinition(**flow_def_in)
        flow_def_out = flow_model.dict(exclude_unset=True)
        assert flow_def_out == flow_def_in
