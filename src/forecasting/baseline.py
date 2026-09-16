"""Naive forecast: last observation carried forward across the horizon."""

from __future__ import annotations

import numpy as np
import pandas as pd


def naive_forecast(history: pd.Series, horizon: int) -> np.ndarray:
    if history.empty:
        raise ValueError("Cannot forecast with empty history")
    last = float(history.iloc[-1])
    return np.full(horizon, last, dtype=float)


def seasonal_naive_forecast(history: pd.Series, horizon: int, season: int = 7) -> np.ndarray:
    if len(history) < season:
        return naive_forecast(history, horizon)
    pattern = history.iloc[-season:].to_numpy(dtype=float)
    reps = int(np.ceil(horizon / season))
    return np.tile(pattern, reps)[:horizon]


def fit_predict_naive(train: pd.DataFrame, future_dates: pd.DatetimeIndex, value_col: str = "sales_units") -> pd.DataFrame:
    yhat = naive_forecast(train[value_col], len(future_dates))
    return pd.DataFrame({"date": future_dates, "model": "Naive", "forecast": yhat})
