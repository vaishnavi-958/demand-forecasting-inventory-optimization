"""Load star-schema tables and write dashboard-ready extracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.engine import Engine

from src.utils.helpers import ensure_dir, resolve_path
from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)


def _to_sql(df: pd.DataFrame, name: str, engine: Engine, if_exists: str = "replace") -> None:
    LOGGER.info("Loading %s (%s rows)", name, len(df))
    method = None if engine.dialect.name == "sqlite" else "multi"
    df.to_sql(name, engine, if_exists=if_exists, index=False, method=method, chunksize=5000)


def build_dimensions(fact: pd.DataFrame) -> dict[str, pd.DataFrame]:
    dim_date = (
        fact[["date", "date_key", "year", "month", "weekday"]]
        .drop_duplicates("date_key")
        .sort_values("date_key")
        .copy()
    )
    dim_date["quarter"] = pd.to_datetime(dim_date["date"]).dt.quarter
    dim_date["week"] = pd.to_datetime(dim_date["date"]).dt.isocalendar().week.astype(int)

    dim_product = (
        fact[["product_key", "item_id", "dept_id", "cat_id"]]
        .drop_duplicates("item_id")
        .sort_values("product_key")
    )
    dim_store = (
        fact[["store_key", "store_id", "state_id"]]
        .drop_duplicates("store_id")
        .sort_values("store_key")
    )
    dim_department = (
        fact[["department_key", "dept_id", "cat_id"]]
        .drop_duplicates("dept_id")
        .sort_values("department_key")
    )
    return {
        "dim_date": dim_date,
        "dim_product": dim_product,
        "dim_store": dim_store,
        "dim_department": dim_department,
    }


def fact_sales_star(fact: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "date_key",
        "product_key",
        "store_key",
        "department_key",
        "item_id",
        "store_id",
        "dept_id",
        "sales_units",
        "price",
        "revenue",
        "promotion_flag",
        "snap_flag",
    ]
    return fact[cols].copy()


def load_all_tables(
    engine: Engine,
    fact: pd.DataFrame,
    forecasts: pd.DataFrame,
    metrics: pd.DataFrame,
    inventory: pd.DataFrame,
) -> None:
    dims = build_dimensions(fact)
    for name, frame in dims.items():
        _to_sql(frame, name, engine)
    _to_sql(fact_sales_star(fact), "fact_daily_sales", engine)
    _to_sql(forecasts, "fact_forecast", engine)
    _to_sql(metrics, "fact_model_metrics", engine)
    _to_sql(inventory, "fact_inventory_optimization", engine)
    abc = inventory[
        [
            "item_id",
            "store_id",
            "dept_id",
            "annual_demand",
            "unit_cost",
            "annual_consumption_value",
            "cumulative_value_pct",
            "abc_class",
        ]
    ].copy()
    _to_sql(abc, "fact_abc_classification", engine)


def write_processed_outputs(
    config: dict[str, Any],
    fact: pd.DataFrame,
    profile: pd.DataFrame,
    evaluation: pd.DataFrame,
    forecasts: pd.DataFrame,
    metrics: pd.DataFrame,
    inventory: pd.DataFrame,
) -> Path:
    out_dir = ensure_dir(resolve_path(config["paths"]["processed_dir"]))
    fact.to_parquet(out_dir / "fact_daily_sales.parquet", index=False)
    profile.to_parquet(out_dir / "demand_profile.parquet", index=False)
    evaluation.to_parquet(out_dir / "forecast_evaluation.parquet", index=False)
    forecasts.to_parquet(out_dir / "fact_forecast.parquet", index=False)
    metrics.to_csv(out_dir / "model_metrics.csv", index=False)
    inventory.to_csv(out_dir / "fact_inventory_optimization.csv", index=False)
    inventory.to_parquet(out_dir / "fact_inventory_optimization.parquet", index=False)
    LOGGER.info("Wrote processed extracts to %s", out_dir)
    return out_dir
