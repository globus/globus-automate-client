import pytest
import responses


@pytest.fixture(autouse=True)
def mocked_responses():
    """Mock responses to requests."""

    with responses.RequestsMock() as request_mock:
        yield request_mock
