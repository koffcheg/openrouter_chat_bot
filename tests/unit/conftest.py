import pytest


@pytest.fixture(autouse=True)
def unit_cleanup_compat():
    yield
