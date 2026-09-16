"""End-to-end supply chain analytics pipeline.

1. validate data
2. clean data
3. transform data
4. load SQL tables
5. generate demand features
6. generate forecasts
7. evaluate models
8. run inventory optimization
9. generate dashboard-ready tables
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.cleaning import clean_calendar, clean_prices, clean_sales
from src.data.ingestion import discover_raw_files, load_raw_m5
from src.data.transformation import build_fact_daily_sales
from src.data.validation import validate_fact_sales, validate_raw_files
from src.database.connection import get_engine
from src.database.loaders import load_all_tables, write_processed_outputs
from src.features.calendar_features import add_calendar_features
from src.features.demand_features import build_demand_profile, select_forecast_candidates
from src.features.inventory_features import attach_cost_assumptions, simulate_on_hand_inventory
from src.forecasting.engine import run_forecasting_engine
from src.forecasting.model_selection import select_best_models
from src.inventory.engine import run_inventory_engine
from src.utils.helpers import load_config, load_model_config, resolve_path
from src.utils.logging_config import get_logger, setup_logging


def _json_safe(value):
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, float) and value != value:
        return None
    try:
        import numpy as np

        if isinstance(value, np.generic):
            native = value.item()
            if isinstance(native, float) and native != native:
                return None
            return native
    except ImportError:
        pass
    return value


def ensure_sample_if_configured(config: dict) -> None:
    sample_cfg = config.get("sample", {})
    if not sample_cfg.get("generate_if_missing", True):
        return
    sales_path = resolve_path(config["paths"]["data_dir"]) / config["paths"].get(
        "sales_file", "sales_train_validation.csv"
    )
    if sales_path.exists():
        return
    from scripts.generate_sample_data import generate, write_raw

    logger = get_logger("run_pipeline")
    logger.info("Raw M5 files not found; generating schema-compatible sample data")
    frames = generate(config)
    write_raw(frames, resolve_path(config["paths"]["data_dir"]))


def build_insights(metrics, inventory, profile) -> dict:
    """Derive talking points from calculated tables. Never hard-code accuracy claims."""
    naive = metrics.loc[metrics["model"] == "Naive", "Forecast_Accuracy"]
    best = metrics.loc[metrics["rank"] == 1, "Forecast_Accuracy"]
    baseline_accuracy = float(naive.mean()) if len(naive) else float("nan")
    best_model_accuracy = float(best.mean()) if len(best) else float("nan")
    improvement = best_model_accuracy - baseline_accuracy
    model_means = (
        metrics.dropna(subset=["WMAPE"])
        .groupby("model")[["WMAPE", "Forecast_Accuracy", "MAE", "RMSE"]]
        .mean()
        .reset_index()
        .sort_values("WMAPE")
    )
    dept_acc = (
        metrics.loc[metrics["rank"] == 1]
        .groupby("dept_id")["Forecast_Accuracy"]
        .mean()
        .sort_values()
    )
    risk_counts = inventory["stockout_risk"].value_counts().to_dict()
    excess_value = float(inventory["excess_value"].sum())
    a_share = float((inventory["abc_class"] == "A").mean())
    worst_stores = (
        inventory.groupby("store_id")
        .agg(
            critical=("stockout_risk", lambda s: int((s == "CRITICAL").sum())),
            excess_value=("excess_value", "sum"),
        )
        .sort_values("critical", ascending=False)
    )
    volatile = profile.groupby("demand_segment").size().to_dict()
    return {
        "baseline_accuracy": baseline_accuracy,
        "best_model_accuracy": best_model_accuracy,
        "improvement_vs_baseline": improvement,
        "best_model_by_mean_wmape": model_means.iloc[0]["model"] if len(model_means) else None,
        "model_comparison": model_means.to_dict(orient="records"),
        "lowest_accuracy_department": None if dept_acc.empty else str(dept_acc.index[0]),
        "lowest_department_accuracy": None if dept_acc.empty else float(dept_acc.iloc[0]),
        "stockout_risk_counts": {str(k): int(v) for k, v in risk_counts.items()},
        "excess_inventory_value": excess_value,
        "a_class_share": a_share,
        "highest_risk_store": None if worst_stores.empty else str(worst_stores.index[0]),
        "demand_segment_counts": {str(k): int(v) for k, v in volatile.items()},
        "series_evaluated": int(metrics.groupby(["item_id", "store_id"]).ngroups),
        "disclaimer": (
            "Accuracy and inventory exposure figures are computed from this run. "
            "Lead time, cost, and on-hand inventory are scenario parameters."
        ),
    }


def main() -> None:
    setup_logging()
    logger = get_logger("run_pipeline")
    config = load_config()
    model_cfg = load_model_config()
    ensure_sample_if_configured(config)

    logger.info("Step 1/9 validate data")
    files = discover_raw_files(config)
    raw = load_raw_m5(config)
    validate_raw_files(files, raw)

    logger.info("Step 2/9 clean data")
    calendar = clean_calendar(raw["calendar"])
    sales = clean_sales(raw["sales"])
    prices = clean_prices(raw["prices"])

    logger.info("Step 3/9 transform data")
    fact = build_fact_daily_sales(sales, calendar, prices, config)
    fact = add_calendar_features(fact)
    validate_fact_sales(fact)

    logger.info("Step 5/9 generate demand features")
    profile = build_demand_profile(fact)
    profile = attach_cost_assumptions(profile, config)
    profile = simulate_on_hand_inventory(profile, seed=int(config["inventory"].get("inventory_simulation_seed", 42)))
    candidates = select_forecast_candidates(profile, config)

    logger.info("Step 6-7/9 generate and evaluate forecasts")
    evaluation, forward, metrics = run_forecasting_engine(fact, candidates, config, model_cfg)
    best = select_best_models(metrics)
    forward = forward.merge(
        best[["item_id", "store_id", "best_model"]],
        on=["item_id", "store_id"],
        how="left",
    )
    forward["is_selected_model"] = forward["model"] == forward["best_model"]

    logger.info("Step 8/9 inventory optimization")
    inventory = run_inventory_engine(profile, config)
    inventory = inventory.merge(
        best[["item_id", "store_id", "best_model", "Forecast_Accuracy", "WMAPE"]],
        on=["item_id", "store_id"],
        how="left",
    )

    logger.info("Step 4/9 load SQL tables")
    engine = get_engine(config)
    load_all_tables(engine, fact, forward, metrics, inventory)

    logger.info("Step 9/9 dashboard-ready tables")
    out_dir = write_processed_outputs(config, fact, profile, evaluation, forward, metrics, inventory)
    insights = build_insights(metrics, inventory, profile)
    (out_dir / "run_insights.json").write_text(
        json.dumps(_json_safe(insights), indent=2, allow_nan=False),
        encoding="utf-8",
    )
    logger.info(
        "Pipeline complete. baseline_accuracy=%.3f best_model_accuracy=%.3f improvement=%.3f",
        insights["baseline_accuracy"],
        insights["best_model_accuracy"],
        insights["improvement_vs_baseline"],
    )

    # Always refresh the web dashboard extracts.
    from scripts.generate_dashboard_data import export_dashboard

    export_dashboard(config, fact, evaluation, forward, metrics, inventory, insights)


if __name__ == "__main__":
    main()
