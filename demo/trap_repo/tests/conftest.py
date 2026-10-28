import pytest


@pytest.fixture
def make_order():
    class Order:
        lines = []
    return Order()
