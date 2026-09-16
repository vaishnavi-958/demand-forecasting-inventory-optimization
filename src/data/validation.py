"""Raw-file and fact-table data quality checks. Failures are raised, not swallowed."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)

CALENDAR_REQUIRED = {"date", "wm_yr_wk", "d", "weekday", "month", "year"}
SALES_REQUIRED = {"id", "item_id", "dept_id", "cat_id", "store_id", "state_id"}
PRICES_REQUIRED = {"store_id", "item_id", "wm_yr_wk", "sell_price"}


class DataQualityError(ValueError):
    """Raised when a data-quality gate fails."""


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise DataQualityError(f"{name} is missing required columns: {sorted(missing)}")


def validate_raw_files(files: dict[str, Path], frames: dict[str, pd.DataFrame]) -> None:
    for label, path in files.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing raw file for {label}: {path}")
        if path.stat().st_size == 0:
            raise DataQualityError(f"Raw file is empty: {path}")

    _require_columns(frames["calendar"], CALENDAR_REQUIRED, "calendar")
    _require_columns(frames["sales"], SALES_REQUIRED, "sales")
    _require_columns(frames["prices"], PRICES_REQUIRED, "prices")

    day_cols = [c for c in frames["sales"].columns if str(c).startswith("d_")]
    if not day_cols:
        raise DataQualityError("sales file has no d_* demand columns (wide M5 format expected)")

    if frames["calendar"]["d"].duplicated().any():
        raise DataQualityError("calendar contains duplicate d labels")
    if frames["sales"]["id"].duplicated().any():
        raise DataQualityError("sales contains duplicate series ids")

    LOGGER.info("Raw file validation passed (%s daily columns)", len(day_cols))


def validate_fact_sales(fact: pd.DataFrame) -> dict[str, Any]:
    issues: list[str] = []
    if fact.empty:
        raise DataQualityError("fact_daily_sales is empty")

    required = {
        "date",
        "item_id",
        "store_id",
        "dept_id",
        "cat_id",
        "sales_units",
        "price",
        "revenue",
    }
    missing = required - set(fact.columns)
    if missing:
        raise DataQualityError(f"fact_daily_sales missing columns: {sorted(missing)}")

    null_ids = fact["item_id"].isna().sum() + fact["store_id"].isna().sum()
    if null_ids:
        issues.append(f"missing product/store identifiers: {int(null_ids)}")

    negative_sales = int((fact["sales_units"] < 0).sum())
    if negative_sales:
        issues.append(f"negative sales_units rows: {negative_sales}")

    invalid_prices = int(((fact["price"] < 0) | fact["price"].isna()).sum())
    if invalid_prices:
        issues.append(f"invalid prices: {invalid_prices}")

    dupes = int(fact.duplicated(["date", "item_id", "store_id"]).sum())
    if dupes:
        issues.append(f"duplicate date/item/store rows: {dupes}")

    date_span = pd.to_datetime(fact["date"])
    expected_days = (date_span.max() - date_span.min()).days + 1
    observed_days = date_span.nunique()
    missing_dates = expected_days - observed_days
    if missing_dates > 0:
        issues.append(f"calendar gaps across fact table: {missing_dates} missing dates")

    unexpected_nulls = int(fact[list(required)].isna().sum().sum())
    if unexpected_nulls:
        issues.append(f"unexpected nulls in required fields: {unexpected_nulls}")

    report = {
        "row_count": int(len(fact)),
        "sku_store_count": int(fact.groupby(["item_id", "store_id"]).ngroups),
        "date_min": str(date_span.min().date()),
        "date_max": str(date_span.max().date()),
        "observed_days": int(observed_days),
        "issues": issues,
    }
    if issues:
        LOGGER.error("Fact sales data-quality issues: %s", issues)
        raise DataQualityError(f"fact_daily_sales failed quality checks: {issues}")

    LOGGER.info("Fact sales validation passed: %s", report)
    return report
