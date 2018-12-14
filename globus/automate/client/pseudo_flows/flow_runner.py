import argparse


from .pseudo_flows import load_from_file, flow_to_digraph, run_flow

CLIENT_ID = "e6c75d97-532a-4c88-b031-8584a319fa3e"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("flow_file")
    parser.add_argument("input_file")
    args = parser.parse_args()
    flow_file = args.flow_file
    input_file = args.input_file
    flow_def = load_from_file(flow_file)
    input_state = load_from_file(input_file)

    final_state = run_flow(flow_def, input_state, CLIENT_ID)
    print(f"Final State of flow: {final_state}")


if __name__ == "__main__":
    main()
