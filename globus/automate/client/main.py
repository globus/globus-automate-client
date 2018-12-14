import argparse
import time
from os import path
from typing import Any, List, Optional, Tuple, Dict
from globus_sdk import AccessTokenAuthorizer, NativeAppAuthClient

from .action_client import ActionClient, create_action_client
from .token_management import get_access_token_for_scope

CLIENT_ID = "e6c75d97-532a-4c88-b031-8584a319fa3e"


hello_request = {"echo_string": "From the CLI"}
transfer_request = {
    "source_endpoint_id": "go#ep1",
    "destination_endpoint_id": "go#ep2",
    "transfer_items": [
        {"source_path": "/~/file1.txt", "destination_path": "/~/cli_file1.txt"}
    ],
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action-scope")
    parser.add_argument("action_url")
    args = parser.parse_args()
    scope = args.action_scope
    action_url = args.action_url
    access_token = get_access_token_for_scope(scope, CLIENT_ID)
    client = create_action_client(action_url, access_token)
    res = client.run(transfer_request)
    print(res.data)
    action_id = res.data["action_id"]
    while res.data["status"] != "SUCCEEDED":
        res = client.status(action_id)
        print(res.data)
        if res.data["status"] != "SUCCEEDED":
            time.sleep(2)
    res = client.release(action_id)
    print(res.data)
    # res = client.status(action_id)
    # print(res.data)


if __name__ == "__main__":
    main()
