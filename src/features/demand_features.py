"""SKU/store demand profiling used by forecasting selection and inventory policy."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)


def _linear_slope(values: np.ndarray) -> float:
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values), dtype=float)
    y = values.astype(float)
    if np.all(y == y[0]):
        return 0.0
    slope = np.polyfit(x, y, 1)[0]
    return float(slope)


def _seasonality_strength(values: np.ndarray, period: int = 7) -> float:
    if len(values) < period * 2:
        return 0.0
    y = values.astype(float)
    total_var = float(np.var(y))
    if total_var <= 0:
        return 0.0
    idx = np.arange(len(y))
    dow_means = np.array([y[idx % period == p].mean() if np.any(idx % period == p) else 0.0 for p in range(period)])
    seasonal_var = float(np.var(dow_means))
    return float(np.clip(seasonal_var / total_var, 0, 1))


def _adi_cv2(values: np.ndarray) -> tuple[float, float]:
    y = values.astype(float)
    nonzero = np.where(y > 0)[0]
    if len(nonzero) == 0:
        return float("inf"), 0.0
    if len(nonzero) == 1:
        adi = float(len(y))
        return adi, 0.0
    intervals = np.diff(nonzero)
    adi = float(np.mean(intervals))
    nz = y[y > 0]
    mean_nz = float(np.mean(nz))
    cv2 = float((np.std(nz, ddof=1) / mean_nz) ** 2) if mean_nz > 0 and len(nz) > 1 else 0.0
    return adi, cv2


def _demand_pattern(adi: float, cv2: float) -> str:
    if not np.isfinite(adi):
        return "no_demand"
    smooth = adi < 1.32
    regular = cv2 < 0.49
    if smooth and regular:
        return "smooth"
    if not smooth and regular:
        return "intermittent"
    if smooth and not regular:
        return "erratic"
    return "lumpy"


def build_demand_profile(fact: pd.DataFrame) -> pd.DataFrame:
    """Aggregate SKU/store demand statistics and volume/volatility segments."""
    grouped = []
    for (item_id, store_id), g in fact.groupby(["item_id", "store_id"], sort=False):
        g = g.sort_values("date")
        y = g["sales_units"].to_numpy(dtype=float)
        revenue = g["revenue"].to_numpy(dtype=float)
        zeros = float((y == 0).mean())
        mean_d = float(np.mean(y))
        std_d = float(np.std(y, ddof=1)) if len(y) > 1 else 0.0
        cv = float(std_d / mean_d) if mean_d > 0 else np.nan
        adi, cv2 = _adi_cv2(y)
        rolling_7 = float(pd.Series(y).rolling(7, min_periods=1).mean().iloc[-1])
        rolling_28 = float(pd.Series(y).rolling(28, min_periods=1).mean().iloc[-1])
        yoy = np.nan
        if len(y) >= 365 * 2:
            recent = float(np.sum(y[-365:]))
            prior = float(np.sum(y[-730:-365]))
            yoy = (recent - prior) / prior if prior > 0 else np.nan
        elif len(y) >= 365:
            # Partial YoY using last 28 days vs same offset last year when possible
            if len(y) >= 365 + 28:
                recent = float(np.sum(y[-28:]))
                prior = float(np.sum(y[-365 - 28 : -365]))
                yoy = (recent - prior) / prior if prior > 0 else np.nan

        row = {
            "item_id": item_id,
            "store_id": store_id,
            "dept_id": g["dept_id"].iloc[0],
            "cat_id": g["cat_id"].iloc[0],
            "state_id": g["state_id"].iloc[0],
            "avg_daily_demand": mean_d,
            "median_daily_demand": float(np.median(y)),
            "demand_std": std_d,
            "coefficient_of_variation": cv,
            "demand_trend": _linear_slope(y),
            "demand_volatility": std_d,
            "seasonality_strength": _seasonality_strength(y),
            "zero_sales_pct": zeros,
            "adi": adi,
            "cv2": cv2,
            "demand_pattern": _demand_pattern(adi, cv2),
            "rolling_7_day_demand": rolling_7,
            "rolling_28_day_demand": rolling_28,
            "yoy_demand_change": yoy,
            "annual_demand": float(np.sum(y[-365:])) if len(y) >= 30 else float(np.sum(y) * (365 / max(len(y), 1))),
            "total_units": float(np.sum(y)),
            "total_revenue": float(np.sum(revenue)),
            "avg_price": float(g["price"].mean()),
            "history_days": int(len(y)),
            "last_sale_date": str(pd.to_datetime(g["date"]).max().date()),
        }
        grouped.append(row)

    profile = pd.DataFrame(grouped)
    vol_cut = profile["avg_daily_demand"].median()
    cv_cut = profile["coefficient_of_variation"].median(skipna=True)

    def _segment(row: pd.Series) -> str:
        high_vol = row["avg_daily_demand"] >= vol_cut
        high_cv = row["coefficient_of_variation"] >= cv_cut if pd.notna(row["coefficient_of_variation"]) else True
        if high_vol and not high_cv:
            return "high_volume_low_volatility"
        if high_vol and high_cv:
            return "high_volume_high_volatility"
        if not high_vol and not high_cv:
            return "low_volume_low_volatility"
        return "low_volume_high_volatility"

    profile["demand_segment"] = profile.apply(_segment, axis=1)
    LOGGER.info("Built demand profile for %s SKU/store series", len(profile))
    return profile


def select_forecast_candidates(profile: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Lightweight models run on all eligible series; expensive models on high-value SKUs."""
    fc = config.get("forecasting", {})
    min_hist = int(fc.get("min_history_days", 90))
    max_skus = int(fc.get("max_forecast_skus", 48))
    expensive_n = int(fc.get("expensive_model_skus", 16))
    prophet_n = int(fc.get("prophet_skus", 8))

    eligible = profile.loc[profile["history_days"] >= min_hist].copy()
    eligible = eligible.sort_values("total_revenue", ascending=False)
    if len(eligible) > max_skus:
        eligible = eligible.head(max_skus)

    ranked = eligible.reset_index(drop=True)
    ranked["run_lightweight"] = True
    ranked["run_holt_winters"] = ranked.index < max(expensive_n, min(24, len(ranked)))
    ranked["run_arima"] = ranked.index < expensive_n
    ranked["run_prophet"] = ranked.index < prophet_n
    LOGGER.info(
        "Forecast candidate selection: %s lightweight, %s Holt-Winters, %s ARIMA, %s Prophet",
        int(ranked["run_lightweight"].sum()),
        int(ranked["run_holt_winters"].sum()),
        int(ranked["run_arima"].sum()),
        int(ranked["run_prophet"].sum()),
    )
    return ranked
