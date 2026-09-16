"""Run the scalable forecasting strategy across selected SKU/store series."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.forecasting.arima_model import fit_predict_arima
from src.forecasting.baseline import fit_predict_naive
from src.forecasting.evaluation import chronological_split, summarize_forecasts
from src.forecasting.exponential_smoothing import fit_predict_holt_winters
from src.forecasting.moving_average import fit_predict_moving_average
from src.forecasting.prophet_model import PROPHET_AVAILABLE, fit_predict_prophet
from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)


def _future_index(last_date, horizon: int) -> pd.DatetimeIndex:
    start = pd.to_datetime(last_date) + pd.Timedelta(days=1)
    return pd.date_range(start, periods=horizon, freq="D")


def _attach_keys(pred: pd.DataFrame, item_id: str, store_id: str, dept_id: str, cat_id: str) -> pd.DataFrame:
    pred = pred.copy()
    pred["item_id"] = item_id
    pred["store_id"] = store_id
    pred["dept_id"] = dept_id
    pred["cat_id"] = cat_id
    if "forecast_lower" not in pred.columns:
        pred["forecast_lower"] = pd.NA
    if "forecast_upper" not in pred.columns:
        pred["forecast_upper"] = pd.NA
    return pred


def forecast_series(
    series: pd.DataFrame,
    candidates: pd.Series,
    config: dict[str, Any],
    model_cfg: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fc_cfg = config["forecasting"]
    horizon = int(fc_cfg["horizon_days"])
    validation_days = int(fc_cfg["validation_days"])
    series = series.sort_values("date")
    train, valid = chronological_split(series, "date", validation_days)
    valid_dates = pd.to_datetime(valid["date"])
    item_id = series["item_id"].iloc[0]
    store_id = series["store_id"].iloc[0]
    dept_id = series["dept_id"].iloc[0]
    cat_id = series["cat_id"].iloc[0]

    preds: list[pd.DataFrame] = []
    if candidates.get("run_lightweight", True):
        preds.append(fit_predict_naive(train, valid_dates))
        for window in model_cfg.get("moving_average", {}).get("windows", [7, 14, 28]):
            preds.append(fit_predict_moving_average(train, valid_dates, int(window)))
    if candidates.get("run_holt_winters", False):
        preds.append(fit_predict_holt_winters(train, valid_dates, model_cfg))
    if candidates.get("run_arima", False):
        preds.append(fit_predict_arima(train, valid_dates, model_cfg))
    if candidates.get("run_prophet", False) and PROPHET_AVAILABLE:
        preds.append(fit_predict_prophet(train, valid_dates, model_cfg))
    elif candidates.get("run_prophet", False):
        LOGGER.info("Prophet not installed; skipping %s | %s", item_id, store_id)

    val_forecasts = pd.concat(preds, ignore_index=True)
    val_forecasts = _attach_keys(val_forecasts, item_id, store_id, dept_id, cat_id)
    actuals = valid[["date", "sales_units"]].rename(columns={"sales_units": "actual"})
    actuals["date"] = pd.to_datetime(actuals["date"])
    val_forecasts["date"] = pd.to_datetime(val_forecasts["date"])
    eval_df = val_forecasts.merge(actuals, on="date", how="left")

    # Refit on train+valid (all history) for the forward horizon used by inventory.
    full_history = pd.concat([train, valid], ignore_index=True)
    future_dates = _future_index(full_history["date"].max(), horizon)
    forward: list[pd.DataFrame] = []
    if candidates.get("run_lightweight", True):
        forward.append(fit_predict_naive(full_history, future_dates))
        for window in model_cfg.get("moving_average", {}).get("windows", [7, 14, 28]):
            forward.append(fit_predict_moving_average(full_history, future_dates, int(window)))
    if candidates.get("run_holt_winters", False):
        forward.append(fit_predict_holt_winters(full_history, future_dates, model_cfg))
    if candidates.get("run_arima", False):
        forward.append(fit_predict_arima(full_history, future_dates, model_cfg))
    if candidates.get("run_prophet", False) and PROPHET_AVAILABLE:
        forward.append(fit_predict_prophet(full_history, future_dates, model_cfg))
    fwd_df = pd.concat(forward, ignore_index=True)
    fwd_df = _attach_keys(fwd_df, item_id, store_id, dept_id, cat_id)
    fwd_df["actual"] = pd.NA
    return eval_df, fwd_df


def run_forecasting_engine(
    fact: pd.DataFrame,
    candidates: pd.DataFrame,
    config: dict[str, Any],
    model_cfg: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    LOGGER.info("Prophet available: %s", PROPHET_AVAILABLE)
    eval_parts: list[pd.DataFrame] = []
    fwd_parts: list[pd.DataFrame] = []
    fact = fact.copy()
    fact["date"] = pd.to_datetime(fact["date"])

    for _, cand in candidates.iterrows():
        mask = (fact["item_id"] == cand["item_id"]) & (fact["store_id"] == cand["store_id"])
        series = fact.loc[mask]
        if series.empty:
            LOGGER.warning("No fact rows for %s | %s", cand["item_id"], cand["store_id"])
            continue
        try:
            eval_df, fwd_df = forecast_series(series, cand, config, model_cfg)
        except ValueError as exc:
            LOGGER.warning("Skipping %s | %s: %s", cand["item_id"], cand["store_id"], exc)
            continue
        eval_parts.append(eval_df)
        fwd_parts.append(fwd_df)

    if not eval_parts:
        raise RuntimeError("Forecasting engine produced no evaluations. Check MIN_HISTORY_DAYS and data coverage.")

    evaluation = pd.concat(eval_parts, ignore_index=True)
    forward = pd.concat(fwd_parts, ignore_index=True)
    metrics = summarize_forecasts(evaluation)
    LOGGER.info("Forecast evaluation complete: %s metric rows", len(metrics))
    return evaluation, forward, metrics


def rolling_origin_wmape(
    series: pd.DataFrame,
    model_fn,
    horizon: int,
    folds: int,
    value_col: str = "sales_units",
) -> float:
    """Optional rolling-origin check. Origins walk backward by `horizon` days."""
    series = series.sort_values("date")
    scores = []
    for fold in range(folds, 0, -1):
        cut = len(series) - fold * horizon
        if cut < 30:
            continue
        train = series.iloc[:cut]
        valid = series.iloc[cut : cut + horizon]
        pred = model_fn(train, pd.to_datetime(valid["date"]))
        merged = pred.merge(
            valid[["date", value_col]].rename(columns={value_col: "actual"}),
            left_on="date",
            right_on="date",
        )
        from src.forecasting.evaluation import wmape as _wmape

        scores.append(_wmape(merged["actual"], merged["forecast"]))
    if not scores:
        return float("nan")
    return float(sum(scores) / len(scores))
