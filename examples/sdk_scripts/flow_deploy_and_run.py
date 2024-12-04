#!/usr/bin/env python
import json
import sys

from globus_automate_client import create_flows_client


def main():
    flow_file = sys.argv[1]
    with open(flow_file) as ff:
        flow_dict = json.load(ff)
    flow_input = sys.argv[2]
    with open(flow_input) as fi:
        flow_input_data = json.load(fi)
    fc = create_flows_client()
    deploy_result = fc.deploy_flow(
        flow_dict,
        title="Deployed via SDK",
        visible_to=["public"],
        runnable_by=["all_authenticated_users"],
    )
    flow_id = deploy_result.data["id"]
    print(f"Flow id is {flow_id}")
    run_result = fc.run_flow(flow_id, None, flow_input_data)
    print(f"Flow Run Result: {json.dumps(run_result.data, indent=4)}")


if __name__ == "__main__":
    main()
