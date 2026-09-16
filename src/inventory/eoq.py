"""EOQ = sqrt((2 × D × S) / H). Costs are scenario parameters, not retailer actuals."""

from __future__ import annotations

import math


def economic_order_quantity(
    annual_demand: float,
    ordering_cost: float,
    holding_cost: float,
) -> float:
    if annual_demand < 0:
        raise ValueError("annual_demand cannot be negative")
    if ordering_cost < 0:
        raise ValueError("ordering_cost cannot be negative")
    if holding_cost < 0:
        raise ValueError("holding_cost cannot be negative")
    if annual_demand == 0 or ordering_cost == 0:
        return 0.0
    if holding_cost == 0:
        raise ValueError("holding_cost must be positive to compute EOQ")
    return float(math.sqrt((2.0 * annual_demand * ordering_cost) / holding_cost))
