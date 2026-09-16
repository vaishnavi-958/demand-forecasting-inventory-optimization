"""Reorder point = average daily demand × lead time + safety stock."""

from __future__ import annotations


def reorder_point(
    avg_daily_demand: float,
    lead_time_days: float,
    safety_stock_units: float,
) -> float:
    if avg_daily_demand < 0:
        raise ValueError("avg_daily_demand cannot be negative")
    if lead_time_days < 0:
        raise ValueError("lead_time_days cannot be negative")
    if safety_stock_units < 0:
        raise ValueError("safety_stock_units cannot be negative")
    lead_time_demand = avg_daily_demand * lead_time_days
    return float(lead_time_demand + safety_stock_units)


def lead_time_demand(avg_daily_demand: float, lead_time_days: float) -> float:
    return float(max(avg_daily_demand, 0.0) * max(lead_time_days, 0.0))
