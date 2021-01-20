from globus_automate_client import create_action_client

# Create an ActionClient for the HelloWorld Action
ac = create_action_client("https://actions.globus.org/hello_world")

# Run an Action and check its results
resp = ac.run({"echo_string": "Hello from SDK"})
assert resp.data["status"] == "SUCCEEDED"
