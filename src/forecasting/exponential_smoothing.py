"""Holt-Winters / Holt exponential smoothing via statsmodels."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.forecasting.baseline import naive_forecast
from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)


def holt_winters_forecast(
    history: pd.Series,
    horizon: int,
    trend: str | None = "add",
    seasonal: str | None = "add",
    seasonal_periods: int = 7,
    damped_trend: bool = False,
) -> np.ndarray:
    y = history.astype(float)
    if y.nunique() <= 1 or len(y) < max(seasonal_periods * 2, 14):
        return naive_forecast(y, horizon)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = ExponentialSmoothing(
                y,
                trend=trend,
                seasonal=seasonal if len(y) >= seasonal_periods * 2 else None,
                seasonal_periods=seasonal_periods if len(y) >= seasonal_periods * 2 else None,
                damped_trend=damped_trend if trend else False,
                initialization_method="estimated",
            )
            fitted = model.fit(optimized=True, remove_bias=False)
            pred = fitted.forecast(horizon)
            return np.asarray(pred, dtype=float)
    except (ValueError, np.linalg.LinAlgError) as exc:
        LOGGER.warning("Holt-Winters failed (%s); falling back to naive", exc)
        return naive_forecast(y, horizon)


def fit_predict_holt_winters(
    train: pd.DataFrame,
    future_dates: pd.DatetimeIndex,
    model_cfg: dict,
    value_col: str = "sales_units",
) -> pd.DataFrame:
    hw = model_cfg.get("holt_winters", {})
    yhat = holt_winters_forecast(
        train[value_col],
        len(future_dates),
        trend=hw.get("trend", "add"),
        seasonal=hw.get("seasonal", "add"),
        seasonal_periods=int(hw.get("seasonal_periods", 7)),
        damped_trend=bool(hw.get("damped_trend", False)),
    )
    return pd.DataFrame({"date": future_dates, "model": "HoltWinters", "forecast": yhat})
