"""Calendar-derived features used by demand analysis and forecasting."""

from __future__ import annotations

import pandas as pd


def add_calendar_features(frame: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    out = frame.copy()
    dates = pd.to_datetime(out[date_col])
    out["year"] = dates.dt.year
    out["month"] = dates.dt.month
    out["week"] = dates.dt.isocalendar().week.astype(int)
    out["dayofweek"] = dates.dt.dayofweek
    out["is_weekend"] = (out["dayofweek"] >= 5).astype(int)
    out["quarter"] = dates.dt.quarter
    out["is_month_start"] = dates.dt.is_month_start.astype(int)
    out["is_month_end"] = dates.dt.is_month_end.astype(int)
    return out
