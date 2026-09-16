"""Excess inventory vs target coverage / recommended inventory position."""

from __future__ import annotations


def classify_excess(
    current_inventory: float,
    avg_daily_demand: float,
    safety_stock_units: float,
    lead_time_days: float,
    target_days_supply: float,
    excess_days_supply_threshold: float,
    unit_cost: float,
) -> dict[str, float | bool]:
    if avg_daily_demand < 0:
        raise ValueError("avg_daily_demand cannot be negative")
    recommended_position = avg_daily_demand * lead_time_days + safety_stock_units
    days_of_supply = current_inventory / avg_daily_demand if avg_daily_demand > 0 else 0.0
    excess_vs_position = max(current_inventory - recommended_position, 0.0)
    excess_vs_target = max(current_inventory - avg_daily_demand * target_days_supply, 0.0) if avg_daily_demand > 0 else 0.0
    excess_units = max(excess_vs_position, excess_vs_target)
    flag = bool(days_of_supply > excess_days_supply_threshold or excess_vs_position > 0 and days_of_supply > target_days_supply)
    if avg_daily_demand == 0 and current_inventory > 0:
        flag = True
        excess_units = current_inventory
        days_of_supply = float("inf")
    return {
        "recommended_inventory_position": float(recommended_position),
        "days_of_supply": float(days_of_supply) if days_of_supply != float("inf") else 9999.0,
        "excess_units": float(excess_units if flag else 0.0),
        "excess_value": float((excess_units if flag else 0.0) * max(unit_cost, 0.0)),
        "excess_inventory_flag": flag,
    }
