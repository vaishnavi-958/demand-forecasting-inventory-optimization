"""Choose the best model per SKU/store using chronological validation metrics."""

from __future__ import annotations

import pandas as pd

from src.utils.logging_config import get_logger

LOGGER = get_logger(__name__)


def select_best_models(metrics: pd.DataFrame, primary: str = "WMAPE") -> pd.DataFrame:
    if metrics.empty:
        return metrics
    ranked = metrics.dropna(subset=[primary]).sort_values(["item_id", "store_id", primary, "RMSE"])
    best = ranked.groupby(["item_id", "store_id"], as_index=False).first()
    best = best.rename(columns={"model": "best_model"})
    LOGGER.info("Selected best models for %s series using %s", len(best), primary)
    return best
