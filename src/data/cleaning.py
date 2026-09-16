"""Cleaning and type coercion for M5-schema inputs."""

from __future__ import annotations

import pandas as pd

from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)


def clean_calendar(calendar: pd.DataFrame) -> pd.DataFrame:
    out = calendar.copy()
    out["date"] = pd.to_datetime(out["date"], errors="raise")
    out["wm_yr_wk"] = out["wm_yr_wk"].astype(int)
    out["d"] = out["d"].astype(str)
    for col in ["event_name_1", "event_type_1", "event_name_2", "event_type_2"]:
        if col not in out.columns:
            out[col] = pd.NA
        out[col] = out[col].replace({"": pd.NA})
    for col in ["snap_CA", "snap_TX", "snap_WI"]:
        if col not in out.columns:
            out[col] = 0
        out[col] = out[col].fillna(0).astype(int)
    out = out.sort_values("date").drop_duplicates("d")
    LOGGER.info("Cleaned calendar: %s rows, %s to %s", len(out), out["date"].min().date(), out["date"].max().date())
    return out


def clean_sales(sales: pd.DataFrame) -> pd.DataFrame:
    out = sales.copy()
    for col in ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]:
        out[col] = out[col].astype(str).str.strip()
    day_cols = [c for c in out.columns if str(c).startswith("d_")]
    if out[day_cols].isna().any().any():
        na_count = int(out[day_cols].isna().sum().sum())
        LOGGER.warning("Filling %s missing daily sales values with 0", na_count)
        out[day_cols] = out[day_cols].fillna(0)
    negative = out[day_cols] < 0
    if negative.any().any():
        n_neg = int(negative.sum().sum())
        LOGGER.warning("Clipping %s negative daily sales values to 0", n_neg)
        out[day_cols] = out[day_cols].clip(lower=0)
    out[day_cols] = out[day_cols].astype("int64")
    LOGGER.info("Cleaned sales: %s series, %s days", len(out), len(day_cols))
    return out


def clean_prices(prices: pd.DataFrame) -> pd.DataFrame:
    out = prices.copy()
    out["store_id"] = out["store_id"].astype(str).str.strip()
    out["item_id"] = out["item_id"].astype(str).str.strip()
    out["wm_yr_wk"] = out["wm_yr_wk"].astype(int)
    out["sell_price"] = pd.to_numeric(out["sell_price"], errors="coerce")
    invalid = out["sell_price"].isna() | (out["sell_price"] < 0)
    if invalid.any():
        n_invalid = int(invalid.sum())
        LOGGER.warning("Dropping %s price rows with missing or negative sell_price", n_invalid)
        out = out.loc[~invalid]
    out = out.drop_duplicates(["store_id", "item_id", "wm_yr_wk"], keep="last")
    LOGGER.info("Cleaned prices: %s rows", len(out))
    return out
