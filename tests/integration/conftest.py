import pytest


@pytest.fixture(autouse=True)
def integration_command_compat():
    yield
