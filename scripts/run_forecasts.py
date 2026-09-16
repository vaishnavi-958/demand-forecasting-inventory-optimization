"""Run forecasting only against already-processed fact_daily_sales.parquet."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.features.demand_features import build_demand_profile, select_forecast_candidates
from src.forecasting.engine import run_forecasting_engine
from src.utils.helpers import load_config, load_model_config, resolve_path
from src.utils.logging_config import get_logger, setup_logging


def main() -> None:
    setup_logging()
    logger = get_logger("run_forecasts")
    config = load_config()
    model_cfg = load_model_config()
    fact_path = resolve_path(config["paths"]["processed_dir"]) / "fact_daily_sales.parquet"
    if not fact_path.exists():
        raise FileNotFoundError(f"{fact_path} not found. Run scripts/run_pipeline.py first.")
    fact = pd.read_parquet(fact_path)
    profile = build_demand_profile(fact)
    candidates = select_forecast_candidates(profile, config)
    evaluation, forward, metrics = run_forecasting_engine(fact, candidates, config, model_cfg)
    out = resolve_path(config["paths"]["processed_dir"])
    evaluation.to_parquet(out / "forecast_evaluation.parquet", index=False)
    forward.to_parquet(out / "fact_forecast.parquet", index=False)
    metrics.to_csv(out / "model_metrics.csv", index=False)
    logger.info("Wrote forecast outputs for %s series", candidates.shape[0])


if __name__ == "__main__":
    main()
