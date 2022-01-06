from pydantic import ValidationError

from globus_automate_client.flow_model import NextOrEnd


def test_next_or_end():
    try:
        ne = NextOrEnd()
        print(ne)
    except ValidationError as ve:
        print(ve)

def test_flow_state():
    try:
