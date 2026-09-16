"""Moving-average forecasts. The last in-sample MA is carried forward."""

from __future__ import annotations

import numpy as np
import pandas as pd


def moving_average_forecast(history: pd.Series, horizon: int, window: int) -> np.ndarray:
    if history.empty:
        raise ValueError("Cannot forecast with empty history")
    w = min(window, len(history))
    level = float(history.iloc[-w:].mean())
    return np.full(horizon, level, dtype=float)


def fit_predict_moving_average(
    train: pd.DataFrame,
    future_dates: pd.DatetimeIndex,
    window: int,
    value_col: str = "sales_units",
) -> pd.DataFrame:
    yhat = moving_average_forecast(train[value_col], len(future_dates), window)
    return pd.DataFrame(
        {"date": future_dates, "model": f"MovingAverage_{window}", "forecast": yhat}
    )
