"""EOQ formula and edge cases."""

import math

import pytest

from src.inventory.eoq import economic_order_quantity


def test_eoq_classic():
    eoq = economic_order_quantity(annual_demand=10000, ordering_cost=50, holding_cost=2)
    assert abs(eoq - math.sqrt(500000)) < 1e-9


def test_eoq_zero_demand_or_setup():
    assert economic_order_quantity(0, 50, 2) == 0.0
    assert economic_order_quantity(1000, 0, 2) == 0.0


def test_eoq_zero_holding_raises():
    with pytest.raises(ValueError):
        economic_order_quantity(1000, 50, 0)


def test_eoq_rejects_negatives():
    with pytest.raises(ValueError):
        economic_order_quantity(-1, 50, 2)
