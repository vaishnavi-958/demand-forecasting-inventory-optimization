"""Export Power BI CSV extracts and the Next.js executive dashboard JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from src.utils.helpers import ensure_dir, load_config, resolve_path
from src.utils.logging_config import get_logger, setup_logging


def _json_default(value):
    if isinstance(value, (np.floating,)):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    return str(value)


def _records(frame: pd.DataFrame) -> list:
    return json.loads(frame.to_json(orient="records"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, default=_json_default, indent=2, allow_nan=False), encoding="utf-8")


def export_dashboard(config, fact, evaluation, forward, metrics, inventory, insights) -> Path:
    logger = get_logger("generate_dashboard_data")
    dash_dir = ensure_dir(resolve_path(config["paths"]["dashboard_dir"]))
    pbi_dir = ensure_dir(resolve_path(config["paths"]["processed_dir"]) / "powerbi")

    best_eval = evaluation.merge(
        metrics.loc[metrics["rank"] == 1, ["item_id", "store_id", "model"]],
        on=["item_id", "store_id", "model"],
        how="inner",
    )
    daily_actual = (
        fact.groupby("date", as_index=False)
        .agg(sales_units=("sales_units", "sum"), revenue=("revenue", "sum"))
        .sort_values("date")
    )
    daily_actual["date"] = pd.to_datetime(daily_actual["date"]).dt.strftime("%Y-%m-%d")

    fcst_vs_actual = (
        best_eval.groupby("date", as_index=False)
        .agg(actual=("actual", "sum"), forecast=("forecast", "sum"))
        .sort_values("date")
    )
    fcst_vs_actual["date"] = pd.to_datetime(fcst_vs_actual["date"]).dt.strftime("%Y-%m-%d")

    model_summary = (
        metrics.groupby("model", as_index=False)
        .agg(
            MAE=("MAE", "mean"),
            RMSE=("RMSE", "mean"),
            MAPE=("MAPE", "mean"),
            sMAPE=("sMAPE", "mean"),
            WMAPE=("WMAPE", "mean"),
            Forecast_Accuracy=("Forecast_Accuracy", "mean"),
            series=("item_id", "count"),
        )
        .sort_values("WMAPE")
    )
    dept_accuracy = (
        metrics.loc[metrics["rank"] == 1]
        .groupby("dept_id", as_index=False)
        .agg(WMAPE=("WMAPE", "mean"), Forecast_Accuracy=("Forecast_Accuracy", "mean"))
        .sort_values("WMAPE")
    )

    kpis = {
        "total_sales": float(fact["revenue"].sum()),
        "total_units": float(fact["sales_units"].sum()),
        "forecast_accuracy": insights["best_model_accuracy"],
        "baseline_accuracy": insights["baseline_accuracy"],
        "improvement_vs_baseline": insights["improvement_vs_baseline"],
        "wmape": float(metrics.loc[metrics["rank"] == 1, "WMAPE"].mean()),
        "inventory_turns": float(inventory["inventory_turns_proxy"].median()),
        "stockout_risk_pct": float((inventory["stockout_risk"].isin(["CRITICAL", "HIGH"])).mean()),
        "excess_inventory_value": float(inventory["excess_value"].sum()),
        "a_class_sku_pct": float((inventory["abc_class"] == "A").mean()),
        "recommended_orders": int(inventory["recommended_order_flag"].sum()),
        "sku_store_count": int(inventory.shape[0]),
        "as_of": str(pd.to_datetime(fact["date"]).max().date()),
    }

    risk_summary = (
        inventory.groupby("stockout_risk", as_index=False)
        .agg(sku_count=("item_id", "count"), excess_value=("excess_value", "sum"), on_hand=("current_inventory", "sum"))
    )
    excess_by_cat = (
        inventory.groupby("cat_id", as_index=False)
        .agg(
            excess_value=("excess_value", "sum"),
            excess_units=("excess_units", "sum"),
            sku_count=("item_id", "count"),
        )
        .sort_values("excess_value", ascending=False)
    )
    store_perf = (
        inventory.groupby(["state_id", "store_id"], as_index=False)
        .agg(
            revenue_proxy=("annual_consumption_value", "sum"),
            avg_accuracy=("Forecast_Accuracy", "mean"),
            avg_wmape=("WMAPE", "mean"),
            critical=("stockout_risk", lambda s: int((s == "CRITICAL").sum())),
            high=("stockout_risk", lambda s: int((s == "HIGH").sum())),
            excess_value=("excess_value", "sum"),
            avg_dos=("days_of_supply", "median"),
        )
        .sort_values("critical", ascending=False)
    )
    abc_summary = (
        inventory.groupby("abc_class", as_index=False)
        .agg(
            sku_count=("item_id", "count"),
            annual_value=("annual_consumption_value", "sum"),
            inventory_value=("average_inventory_value_proxy", "sum"),
            avg_eoq=("eoq", "mean"),
        )
        .sort_values("abc_class")
    )
    pareto = (
        inventory.sort_values("annual_consumption_value", ascending=False)
        .assign(rank=lambda d: range(1, len(d) + 1))
        [["rank", "item_id", "store_id", "annual_consumption_value", "cumulative_value_pct", "abc_class"]]
        .head(80)
    )

    planner = inventory[
        [
            "item_id",
            "store_id",
            "dept_id",
            "cat_id",
            "abc_class",
            "demand_segment",
            "best_model",
            "Forecast_Accuracy",
            "WMAPE",
            "avg_daily_demand",
            "current_inventory",
            "safety_stock",
            "reorder_point",
            "days_of_supply",
            "stockout_risk",
            "excess_units",
            "excess_value",
            "eoq",
            "recommended_order_qty",
            "recommended_action",
            "lead_time_days",
            "service_level",
            "demand_std",
            "annual_demand",
            "unit_cost",
            "ordering_cost",
            "holding_cost_rate",
        ]
    ].sort_values(["stockout_risk", "excess_value"], ascending=[True, False])
    planner["stockout_risk"] = pd.Categorical(
        planner["stockout_risk"], categories=["CRITICAL", "HIGH", "MEDIUM", "LOW"], ordered=True
    )
    planner = planner.sort_values(["stockout_risk", "excess_value"], ascending=[True, False])

    sku_forecasts = (
        best_eval.groupby(["item_id", "store_id", "date"], as_index=False)
        .agg(actual=("actual", "sum"), forecast=("forecast", "sum"))
        .sort_values(["item_id", "store_id", "date"])
    )
    sku_forecasts["date"] = pd.to_datetime(sku_forecasts["date"]).dt.strftime("%Y-%m-%d")

    category_trend = (
        fact.groupby(["date", "cat_id"], as_index=False)
        .agg(sales_units=("sales_units", "sum"), revenue=("revenue", "sum"))
        .sort_values("date")
    )
    category_trend["date"] = pd.to_datetime(category_trend["date"]).dt.strftime("%Y-%m-%d")
    # downsample to weekly for the UI
    category_trend["week"] = pd.to_datetime(category_trend["date"]).dt.to_period("W").astype(str)
    category_weekly = (
        category_trend.groupby(["week", "cat_id"], as_index=False)
        .agg(sales_units=("sales_units", "sum"), revenue=("revenue", "sum"))
    )

    payload = {
        "kpis": kpis,
        "insights": insights,
        "sales_trend": _records(daily_actual.tail(180)),
        "forecast_vs_actual": _records(fcst_vs_actual),
        "model_summary": _records(model_summary),
        "dept_accuracy": _records(dept_accuracy),
        "risk_summary": _records(risk_summary),
        "excess_by_category": _records(excess_by_cat),
        "store_performance": _records(store_perf),
        "abc_summary": _records(abc_summary),
        "pareto": _records(pareto),
        "planner": _records(planner),
        "sku_forecasts": _records(sku_forecasts),
        "category_weekly": _records(category_weekly),
        "assumptions": {
            "lead_time": "Analytical assumption / scenario parameter. M5 has no supplier lead time.",
            "unit_cost": "Sell-price proxy. Not actual Walmart procurement cost.",
            "on_hand_inventory": "Simulated scenario position. M5 has no inventory snapshot.",
            "cogs_and_turns": "Turns use annual consumption value / scenario inventory value as a proxy.",
        },
    }
    write_json(dash_dir / "dashboard.json", payload)
    write_json(dash_dir / "kpis.json", kpis)
    write_json(dash_dir / "insights.json", insights)

    inventory.to_csv(pbi_dir / "fact_inventory_optimization.csv", index=False)
    metrics.to_csv(pbi_dir / "fact_model_metrics.csv", index=False)
    fact.groupby(["date", "item_id", "store_id", "dept_id", "cat_id"], as_index=False).agg(
        sales_units=("sales_units", "sum"), revenue=("revenue", "sum"), price=("price", "mean")
    ).to_csv(pbi_dir / "fact_daily_sales.csv", index=False)
    forward.to_csv(pbi_dir / "fact_forecast.csv", index=False)
    logger.info("Wrote dashboard JSON to %s and Power BI CSVs to %s", dash_dir, pbi_dir)
    return dash_dir


def main() -> None:
    setup_logging()
    config = load_config()
    processed = resolve_path(config["paths"]["processed_dir"])
    fact = pd.read_parquet(processed / "fact_daily_sales.parquet")
    evaluation = pd.read_parquet(processed / "forecast_evaluation.parquet")
    forward = pd.read_parquet(processed / "fact_forecast.parquet")
    metrics = pd.read_csv(processed / "model_metrics.csv")
    inventory = pd.read_parquet(processed / "fact_inventory_optimization.parquet")
    insights = json.loads((processed / "run_insights.json").read_text(encoding="utf-8"))
    export_dashboard(config, fact, evaluation, forward, metrics, inventory, insights)


if __name__ == "__main__":
    main()
