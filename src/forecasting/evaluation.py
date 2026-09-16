"""Forecast accuracy metrics. Zero-demand periods are handled without division-by-zero.

Forecast Accuracy is defined as 1 - WMAPE, expressed as a percentage.
WMAPE is the primary metric because MAPE is undefined or unstable when actuals are zero,
which is common in retail daily SKU/store demand.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _as_arrays(y_true, y_pred) -> tuple[np.ndarray, np.ndarray]:
    y = np.asarray(y_true, dtype=float)
    yhat = np.asarray(y_pred, dtype=float)
    if y.shape != yhat.shape:
        raise ValueError(f"Shape mismatch: y_true {y.shape} vs y_pred {yhat.shape}")
    mask = np.isfinite(y) & np.isfinite(yhat)
    return y[mask], yhat[mask]


def mae(y_true, y_pred) -> float:
    y, yhat = _as_arrays(y_true, y_pred)
    if len(y) == 0:
        return float("nan")
    return float(np.mean(np.abs(y - yhat)))


def rmse(y_true, y_pred) -> float:
    y, yhat = _as_arrays(y_true, y_pred)
    if len(y) == 0:
        return float("nan")
    return float(np.sqrt(np.mean((y - yhat) ** 2)))


def mape(y_true, y_pred) -> float:
    """MAPE on strictly positive actuals only. Returns NaN if none exist."""
    y, yhat = _as_arrays(y_true, y_pred)
    positive = y > 0
    if not np.any(positive):
        return float("nan")
    return float(np.mean(np.abs((y[positive] - yhat[positive]) / y[positive])))


def smape(y_true, y_pred) -> float:
    y, yhat = _as_arrays(y_true, y_pred)
    denom = np.abs(y) + np.abs(yhat)
    valid = denom > 0
    if not np.any(valid):
        return 0.0 if np.allclose(y, yhat) else float("nan")
    return float(np.mean(2.0 * np.abs(y[valid] - yhat[valid]) / denom[valid]))


def wmape(y_true, y_pred) -> float:
    y, yhat = _as_arrays(y_true, y_pred)
    if len(y) == 0:
        return float("nan")
    denom = float(np.sum(np.abs(y)))
    if denom == 0:
        return 0.0 if np.allclose(y, yhat) else 1.0
    return float(np.sum(np.abs(y - yhat)) / denom)


def forecast_accuracy(y_true, y_pred) -> float:
    """Forecast Accuracy = 1 - WMAPE. Clipped to [0, 1] for reporting stability."""
    value = 1.0 - wmape(y_true, y_pred)
    return float(np.clip(value, 0.0, 1.0))


def metrics_dict(y_true, y_pred) -> dict[str, float]:
    return {
        "MAE": mae(y_true, y_pred),
        "RMSE": rmse(y_true, y_pred),
        "MAPE": mape(y_true, y_pred),
        "sMAPE": smape(y_true, y_pred),
        "WMAPE": wmape(y_true, y_pred),
        "Forecast_Accuracy": forecast_accuracy(y_true, y_pred),
    }


def chronological_split(frame: pd.DataFrame, date_col: str, validation_days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Time-based holdout. Random splits leak future demand into training and are not used."""
    ordered = frame.sort_values(date_col)
    if validation_days <= 0:
        raise ValueError("validation_days must be positive")
    if len(ordered) <= validation_days:
        raise ValueError("Series is shorter than the validation window")
    train = ordered.iloc[:-validation_days]
    valid = ordered.iloc[-validation_days:]
    return train, valid


def summarize_forecasts(eval_frame: pd.DataFrame) -> pd.DataFrame:
    """eval_frame must contain item_id, store_id, dept_id, model, actual, forecast."""
    rows = []
    keys = ["item_id", "store_id", "dept_id", "model"]
    for key, g in eval_frame.groupby(keys, dropna=False):
        metrics = metrics_dict(g["actual"], g["forecast"])
        record = dict(zip(keys, key))
        record.update(metrics)
        record["n_points"] = int(len(g))
        rows.append(record)
    metrics_df = pd.DataFrame(rows)
    if metrics_df.empty:
        return metrics_df
    metrics_df["rank"] = (
        metrics_df.groupby(["item_id", "store_id"])["WMAPE"]
        .rank(method="min", ascending=True)
        .astype(int)
    )
    return metrics_df.sort_values(["item_id", "store_id", "rank"])
