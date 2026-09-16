"""Assemble SKU/store inventory policy, risk, ABC, and EOQ outputs."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.inventory.abc_analysis import abc_classify
from src.inventory.eoq import economic_order_quantity
from src.inventory.excess_inventory import classify_excess
from src.inventory.reorder_point import lead_time_demand, reorder_point
from src.inventory.safety_stock import safety_stock, z_from_service_level
from src.inventory.stockout_risk import classify_stockout_risk, recommended_action
from src.utils.helpers import z_for_service_level
from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)


def inventory_turns(cogs: float, average_inventory_value: float) -> float:
    """Turns = COGS / average inventory. Both arguments are analytical proxies when M5 has no stock ledger."""
    if average_inventory_value < 0 or cogs < 0:
        raise ValueError("COGS and average inventory cannot be negative")
    if average_inventory_value == 0:
        return 0.0
    return float(cogs / average_inventory_value)


def run_inventory_engine(
    profile: pd.DataFrame,
    config: dict[str, Any],
    service_level: float | None = None,
    lead_time_override: float | None = None,
    ordering_cost_override: float | None = None,
    holding_cost_rate_override: float | None = None,
) -> pd.DataFrame:
    inventory_cfg = config.get("inventory", {})
    abc_cfg = config.get("abc", {})
    sl = float(service_level if service_level is not None else inventory_cfg.get("service_level", 0.95))
    z_value = z_for_service_level(config, sl)
    ordering_cost = float(
        ordering_cost_override if ordering_cost_override is not None else inventory_cfg.get("ordering_cost", 75.0)
    )
    holding_rate = float(
        holding_cost_rate_override
        if holding_cost_rate_override is not None
        else inventory_cfg.get("holding_cost_rate", 0.25)
    )
    target_dos = float(inventory_cfg.get("target_days_supply", 21))
    excess_dos = float(inventory_cfg.get("excess_days_supply_threshold", 45))
    near_rop = float(inventory_cfg.get("near_rop_tolerance", 0.15))

    rows = []
    for _, row in profile.iterrows():
        lt = float(lead_time_override if lead_time_override is not None else row["lead_time_days"])
        add = float(row["avg_daily_demand"])
        sigma = float(row["demand_std"]) if pd.notna(row["demand_std"]) else 0.0
        unit_cost = float(row["unit_cost"]) if pd.notna(row["unit_cost"]) else 0.0
        holding_cost = unit_cost * holding_rate
        annual_demand = float(row["annual_demand"])
        on_hand = float(row.get("current_inventory", 0.0))

        ss = safety_stock(sigma, lt, z_value=z_value)
        ltd = lead_time_demand(add, lt)
        rop = reorder_point(add, lt, ss)
        try:
            eoq = economic_order_quantity(annual_demand, ordering_cost, holding_cost) if holding_cost > 0 else 0.0
        except ValueError:
            eoq = 0.0
        excess = classify_excess(on_hand, add, ss, lt, target_dos, excess_dos, unit_cost)
        dos = excess["days_of_supply"]
        risk = classify_stockout_risk(on_hand, rop, add, lt, near_rop)
        annual_value = annual_demand * unit_cost
        recommended_order_qty = max(eoq, rop - on_hand) if risk in {"CRITICAL", "HIGH"} else 0.0
        turns_proxy = inventory_turns(annual_value, max(on_hand * unit_cost, 1e-9))
        rec = recommended_action(risk, bool(excess["excess_inventory_flag"]))

        rows.append(
            {
                "item_id": row["item_id"],
                "store_id": row["store_id"],
                "dept_id": row["dept_id"],
                "cat_id": row["cat_id"],
                "state_id": row["state_id"],
                "demand_segment": row.get("demand_segment"),
                "demand_pattern": row.get("demand_pattern"),
                "avg_daily_demand": add,
                "demand_std": sigma,
                "lead_time_days": lt,
                "lead_time_source": row.get("lead_time_source", "analytical_assumption"),
                "service_level": sl,
                "z_value": z_value,
                "lead_time_demand": ltd,
                "safety_stock": ss,
                "reorder_point": rop,
                "current_inventory": on_hand,
                "inventory_position": on_hand,  # no open POs in M5; position = on-hand scenario
                "days_of_supply": dos,
                "target_days_supply": target_dos,
                "recommended_inventory_position": excess["recommended_inventory_position"],
                "recommended_order_flag": rec in {"EXPEDITE", "REORDER"},
                "recommended_order_qty": recommended_order_qty,
                "recommended_action": rec,
                "stockout_risk": risk,
                "excess_units": excess["excess_units"],
                "excess_value": excess["excess_value"],
                "excess_inventory_flag": excess["excess_inventory_flag"],
                "annual_demand": annual_demand,
                "unit_cost": unit_cost,
                "unit_cost_source": "sell_price_proxy",
                "ordering_cost": ordering_cost,
                "holding_cost_rate": holding_rate,
                "holding_cost": holding_cost,
                "eoq": eoq,
                "annual_consumption_value": annual_value,
                "inventory_turns_proxy": turns_proxy,
                "cogs_proxy": annual_value,
                "average_inventory_value_proxy": on_hand * unit_cost,
                "inventory_source": row.get("inventory_source", "analytical_scenario_proxy"),
            }
        )

    result = pd.DataFrame(rows)
    abc = abc_classify(
        result[["item_id", "store_id", "annual_consumption_value"]],
        value_col="annual_consumption_value",
        a_cutoff=float(abc_cfg.get("a_cutoff", 0.80)),
        b_cutoff=float(abc_cfg.get("b_cutoff", 0.95)),
    )
    result = result.merge(
        abc[["item_id", "store_id", "cumulative_value_pct", "abc_class"]],
        on=["item_id", "store_id"],
        how="left",
    )
    LOGGER.info(
        "Inventory engine complete: %s series, A=%s B=%s C=%s, critical=%s, excess=%s",
        len(result),
        int((result["abc_class"] == "A").sum()),
        int((result["abc_class"] == "B").sum()),
        int((result["abc_class"] == "C").sum()),
        int((result["stockout_risk"] == "CRITICAL").sum()),
        int(result["excess_inventory_flag"].sum()),
    )
    return result


def run_scenario(
    profile: pd.DataFrame,
    config: dict[str, Any],
    service_level: float,
    lead_time_days: float,
    ordering_cost: float,
    holding_cost_rate: float,
) -> pd.DataFrame:
    """Recalculate SS/ROP/EOQ under a planner-defined scenario."""
    return run_inventory_engine(
        profile,
        config,
        service_level=service_level,
        lead_time_override=lead_time_days,
        ordering_cost_override=ordering_cost,
        holding_cost_rate_override=holding_cost_rate,
    )
