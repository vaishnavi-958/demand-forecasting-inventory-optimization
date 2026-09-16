"""Stockout-risk classification from inventory position vs ROP and lead time coverage."""

from __future__ import annotations


def classify_stockout_risk(
    current_inventory: float,
    reorder_point_units: float,
    avg_daily_demand: float,
    lead_time_days: float,
    near_rop_tolerance: float = 0.15,
) -> str:
    if current_inventory < 0:
        raise ValueError("current_inventory cannot be negative")
    if avg_daily_demand < 0:
        raise ValueError("avg_daily_demand cannot be negative")

    days_of_supply = current_inventory / avg_daily_demand if avg_daily_demand > 0 else float("inf")
    if avg_daily_demand > 0 and days_of_supply < lead_time_days:
        return "CRITICAL"
    if current_inventory < reorder_point_units:
        return "HIGH"
    near_band = reorder_point_units * (1.0 + near_rop_tolerance)
    if current_inventory <= near_band:
        return "MEDIUM"
    return "LOW"


def recommended_action(risk: str, excess_flag: bool) -> str:
    if risk == "CRITICAL":
        return "EXPEDITE"
    if risk == "HIGH":
        return "REORDER"
    if excess_flag:
        return "REDUCE INVENTORY"
    if risk == "MEDIUM":
        return "MONITOR"
    return "NO ACTION"
