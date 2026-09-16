"""ABC classification on annual consumption value using cumulative-value cutoffs.

A ≈ top 80% of value, B ≈ next 15%, C ≈ remaining 5%.
Boundaries follow the cumulative-value method and are not forced to exact SKU counts.
"""

from __future__ import annotations

import pandas as pd


def abc_classify(
    frame: pd.DataFrame,
    value_col: str = "annual_consumption_value",
    a_cutoff: float = 0.80,
    b_cutoff: float = 0.95,
) -> pd.DataFrame:
    if frame.empty:
        out = frame.copy()
        out["cumulative_value"] = pd.Series(dtype=float)
        out["cumulative_value_pct"] = pd.Series(dtype=float)
        out["abc_class"] = pd.Series(dtype=str)
        return out
    if (frame[value_col] < 0).any():
        raise ValueError("annual consumption value cannot be negative")

    out = frame.copy()
    out = out.sort_values(value_col, ascending=False, kind="mergesort").reset_index(drop=True)
    total = float(out[value_col].sum())
    if total == 0:
        out["cumulative_value"] = 0.0
        out["cumulative_value_pct"] = 1.0
        out["abc_class"] = "C"
        return out

    out["cumulative_value"] = out[value_col].cumsum()
    out["cumulative_value_pct"] = out["cumulative_value"] / total

    def _class(pct: float) -> str:
        if pct <= a_cutoff:
            return "A"
        if pct <= b_cutoff:
            return "B"
        return "C"

    out["abc_class"] = out["cumulative_value_pct"].map(_class)
    # Guarantee the first SKU is A when it alone exceeds the A cutoff.
    if len(out) and out.loc[0, "abc_class"] != "A" and out.loc[0, value_col] > 0:
        out.loc[0, "abc_class"] = "A"
    return out
