import argparse


from .pseudo_flows import load_from_file, flow_to_digraph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("flow_file")
    args = parser.parse_args()
    flow_file = args.flow_file
    flow_def = load_from_file(flow_file)
    gr = flow_to_digraph(flow_def)
    print(gr.source)


if __name__ == "__main__":
    main()
