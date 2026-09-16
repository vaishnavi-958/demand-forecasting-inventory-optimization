"""Prophet wrapper. Optional dependency — see docs/forecasting_methodology.md."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.forecasting.baseline import naive_forecast
from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)

try:
    from prophet import Prophet

    PROPHET_AVAILABLE = True
except Exception:  # ImportError and cmdstan runtime issues
    Prophet = None
    PROPHET_AVAILABLE = False


def prophet_forecast(
    train: pd.DataFrame,
    horizon: int,
    date_col: str = "date",
    value_col: str = "sales_units",
    weekly_seasonality: bool = True,
    yearly_seasonality: str | bool = "auto",
    interval_width: float = 0.95,
) -> pd.DataFrame:
    if not PROPHET_AVAILABLE:
        LOGGER.warning("Prophet is not installed; skipping Prophet model for this series")
        dates = pd.date_range(pd.to_datetime(train[date_col]).max() + pd.Timedelta(days=1), periods=horizon, freq="D")
        yhat = naive_forecast(train[value_col], horizon)
        return pd.DataFrame(
            {
                "date": dates,
                "model": "Prophet",
                "forecast": yhat,
                "forecast_lower": np.nan,
                "forecast_upper": np.nan,
                "status": "unavailable",
            }
        )

    history = train[[date_col, value_col]].rename(columns={date_col: "ds", value_col: "y"}).copy()
    history["ds"] = pd.to_datetime(history["ds"])
    yearly = yearly_seasonality
    if yearly == "auto":
        yearly = history["ds"].nunique() >= 365
    model = Prophet(
        weekly_seasonality=weekly_seasonality,
        yearly_seasonality=yearly,
        daily_seasonality=False,
        interval_width=interval_width,
    )
    model.fit(history)
    future = model.make_future_dataframe(periods=horizon, freq="D")
    forecast = model.predict(future).tail(horizon)
    return pd.DataFrame(
        {
            "date": forecast["ds"],
            "model": "Prophet",
            "forecast": forecast["yhat"].to_numpy(dtype=float),
            "forecast_lower": forecast["yhat_lower"].to_numpy(dtype=float),
            "forecast_upper": forecast["yhat_upper"].to_numpy(dtype=float),
            "status": "ok",
        }
    )


def fit_predict_prophet(
    train: pd.DataFrame,
    future_dates: pd.DatetimeIndex,
    model_cfg: dict,
    value_col: str = "sales_units",
) -> pd.DataFrame:
    pr = model_cfg.get("prophet", {})
    result = prophet_forecast(
        train,
        horizon=len(future_dates),
        value_col=value_col,
        weekly_seasonality=bool(pr.get("weekly_seasonality", True)),
        yearly_seasonality=pr.get("yearly_seasonality", "auto"),
        interval_width=float(pr.get("interval_width", 0.95)),
    )
    # Align to requested future dates if Prophet produced a matching horizon.
    if len(result) == len(future_dates):
        result = result.copy()
        result["date"] = future_dates
    return result
