"""Configurable ARIMA/SARIMA. Applied only to selected high-value series."""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from src.forecasting.baseline import naive_forecast
from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)


def arima_forecast(
    history: pd.Series,
    horizon: int,
    order: tuple[int, int, int] = (1, 1, 1),
    seasonal_order: tuple[int, int, int, int] | None = (1, 0, 1, 7),
    maxiter: int = 50,
) -> np.ndarray:
    y = history.astype(float)
    if len(y) < 30 or y.nunique() <= 1:
        return naive_forecast(y, horizon)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = ARIMA(
                y,
                order=order,
                seasonal_order=seasonal_order if seasonal_order else (0, 0, 0, 0),
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            fitted = model.fit(method_kwargs={"maxiter": maxiter, "disp": 0})
            pred = fitted.forecast(horizon)
            return np.asarray(pred, dtype=float)
    except (ValueError, np.linalg.LinAlgError) as exc:
        LOGGER.warning("ARIMA failed (%s); falling back to naive", exc)
        return naive_forecast(y, horizon)


def fit_predict_arima(
    train: pd.DataFrame,
    future_dates: pd.DatetimeIndex,
    model_cfg: dict,
    value_col: str = "sales_units",
) -> pd.DataFrame:
    ar = model_cfg.get("arima", {})
    order = tuple(ar.get("order", [1, 1, 1]))
    seasonal = tuple(ar.get("seasonal_order", [1, 0, 1, 7]))
    yhat = arima_forecast(
        train[value_col],
        len(future_dates),
        order=order,
        seasonal_order=seasonal,
        maxiter=int(ar.get("maxiter", 50)),
    )
    return pd.DataFrame({"date": future_dates, "model": "ARIMA", "forecast": yhat})
