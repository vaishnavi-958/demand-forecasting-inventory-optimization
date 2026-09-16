"""Reshape M5 wide sales into a star-schema-ready daily fact table."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)


def melt_sales(sales: pd.DataFrame) -> pd.DataFrame:
    id_vars = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
    day_cols = [c for c in sales.columns if str(c).startswith("d_")]
    LOGGER.info("Melting %s series x %s days into long format", len(sales), len(day_cols))
    long_df = sales.melt(
        id_vars=id_vars,
        value_vars=day_cols,
        var_name="d",
        value_name="sales_units",
    )
    long_df["d"] = long_df["d"].astype(str)
    long_df["sales_units"] = long_df["sales_units"].astype("int64")
    return long_df


def _promotion_flag(calendar: pd.DataFrame) -> pd.Series:
    event = calendar.get("event_name_1").notna() if "event_name_1" in calendar.columns else False
    return event.astype(int)


def build_fact_daily_sales(
    sales: pd.DataFrame,
    calendar: pd.DataFrame,
    prices: pd.DataFrame,
    config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Join melted sales to calendar and weekly sell prices; compute revenue."""
    del config  # reserved for future filters
    long_df = melt_sales(sales)
    cal = calendar.copy()
    cal["promotion_flag"] = _promotion_flag(cal)
    fact = long_df.merge(
        cal[["d", "date", "wm_yr_wk", "weekday", "wday", "month", "year", "promotion_flag",
             "event_name_1", "event_type_1", "snap_CA", "snap_TX", "snap_WI"]],
        on="d",
        how="left",
        validate="many_to_one",
    )
    if fact["date"].isna().any():
        missing = int(fact["date"].isna().sum())
        raise ValueError(f"{missing} sales rows could not be joined to calendar dates")

    fact = fact.merge(
        prices[["store_id", "item_id", "wm_yr_wk", "sell_price"]],
        on=["store_id", "item_id", "wm_yr_wk"],
        how="left",
    )
    # Carry last known price forward within each SKU/store, then backfill.
    fact = fact.sort_values(["item_id", "store_id", "date"])
    fact["price"] = (
        fact.groupby(["item_id", "store_id"], group_keys=False)["sell_price"]
        .transform(lambda s: s.ffill().bfill())
    )
    missing_price = int(fact["price"].isna().sum())
    if missing_price:
        LOGGER.warning("Imputing median catalog price for %s rows without sell_price", missing_price)
        median_price = float(prices["sell_price"].median())
        fact["price"] = fact["price"].fillna(median_price)

    snap_map = {"CA": "snap_CA", "TX": "snap_TX", "WI": "snap_WI"}
    fact["snap_flag"] = 0
    for state, col in snap_map.items():
        if col in fact.columns:
            fact.loc[fact["state_id"] == state, "snap_flag"] = fact.loc[fact["state_id"] == state, col]

    fact["revenue"] = fact["sales_units"] * fact["price"]
    fact["date_key"] = fact["date"].dt.strftime("%Y%m%d").astype(int)
    fact["product_key"] = fact["item_id"].astype("category").cat.codes + 1
    fact["store_key"] = fact["store_id"].astype("category").cat.codes + 1
    fact["department_key"] = fact["dept_id"].astype("category").cat.codes + 1
    fact["series_id"] = fact["item_id"] + "|" + fact["store_id"]

    LOGGER.info(
        "Built fact_daily_sales: %s rows, %s series, revenue_sum=%.2f",
        len(fact),
        fact["series_id"].nunique(),
        float(fact["revenue"].sum()),
    )
    return fact
