"""Inventory-oriented feature attachments. Costs are scenario parameters, not retailer actuals."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)


def attach_cost_assumptions(profile: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    inventory = config.get("inventory", {})
    lead_map = config.get("lead_time_by_department", {})
    default_lt = int(inventory.get("default_lead_time_days", 7))
    out = profile.copy()
    out["lead_time_days"] = out["dept_id"].map(lead_map).fillna(default_lt).astype(int)
    out["lead_time_source"] = "analytical_assumption"
    out["ordering_cost"] = float(inventory.get("ordering_cost", 75.0))
    out["holding_cost_rate"] = float(inventory.get("holding_cost_rate", 0.25))
    out["unit_cost"] = out["avg_price"].astype(float)
    out["holding_cost"] = out["unit_cost"] * out["holding_cost_rate"]
    out["target_days_supply"] = float(inventory.get("target_days_supply", 21))
    LOGGER.info("Attached inventory cost and lead-time assumptions to %s series", len(out))
    return out


def simulate_on_hand_inventory(profile: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Create a scenario on-hand position. M5 does not include inventory snapshots."""
    rng = pd.Series(dtype=float)
    generator = __import__("numpy").random.default_rng(seed)
    out = profile.copy()
    # Days of supply drawn so the planner workbench contains stockout, reorder, and excess cases.
    segment_dos = {
        "high_volume_low_volatility": (10, 28),
        "high_volume_high_volatility": (4, 18),
        "low_volume_low_volatility": (20, 55),
        "low_volume_high_volatility": (8, 70),
    }
    dos_values = []
    for _, row in out.iterrows():
        lo, hi = segment_dos.get(row.get("demand_segment"), (7, 40))
        dos_values.append(float(generator.uniform(lo, hi)))
    out["simulated_days_of_supply"] = dos_values
    out["current_inventory"] = (out["simulated_days_of_supply"] * out["avg_daily_demand"]).clip(lower=0)
    out["inventory_source"] = "analytical_scenario_proxy"
    LOGGER.info("Simulated on-hand inventory for %s series (scenario proxy, not retailer actuals)", len(out))
    del rng
    return out
